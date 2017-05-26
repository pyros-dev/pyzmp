# -*- coding: utf-8 -*-
# This python package is implementing a very simple multiprocess framework
# The point of it is to be able to fully tests the multiprocess behavior,
#     in pure python, without having to run a ROS system.
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import tempfile
if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

import multiprocessing, multiprocessing.reduction  #TODO we should probably use subprocess + psutil instead...
import threading
import psutil
import pexpect.fdpexpect
import types
import uuid

import errno

import re
import zmq
import socket
import logging
import pickle
import contextlib
#import dill as pickle

# allowing pickling of exceptions to transfer it
from collections import namedtuple, OrderedDict

from .registry import FileBasedRegistry

import time

try:
    from tblib.decorators import Traceback
    # TODO : potential candidates for pickle + tblib replacement for easier serialization
    # TODO : - https://github.com/uqfoundation/dill
    # TODO : - OR https://github.com/cloudpipe/cloudpickle
    # TODO : - OR https://github.com/irmen/Serpent ?
    # TODO : - OR https://github.com/esnme/ultrajson ?
    # TODO : - OR something else ?
except ImportError:
    Traceback = None

try:
    import setproctitle
except ImportError:
    setproctitle = None


# TODO : Nodelet ( thread, with fast intraprocess zmq comm - entity system design /vs/threadpool ?)

pid_registry = FileBasedRegistry("pid")


def on_terminate(proc):
    print("process {} terminated with exit code {}".format(proc, proc.returncode))


class ProcessObserver(object):
    """A ProcessObserver can observe any local running process (even if we did not launch it and are not the parent)"""

    @classmethod
    def from_ptyprocess(cls, pexpect_spawn):
        # We want to use pexpect tty interactive feature to control a process
        return cls(pid=ptyprocess_spawn.pid,
                   expect_out=ptyprocess_spawn,
                   expect_err=ptyprocess_spawn)

    @classmethod
    def from_subprocess(cls, subprocess_popen):
        # building pexpect objects on file descriptors
        return cls(pid=subprocess_popen.pid,
                   expect_out=pexpect.fdpexpect.fdspawn(subprocess_popen.stdout),
                   expect_err=pexpect.fdpexpect.fdspawn(subprocess_popen.stderr))

    def __init__(self, out_watchers=None, err_watchers=None, async=True):
        """
        Creates a ProcessObserver for the process matching the pid (or the current process if pid is None).
        :param err_watcher: a list of pattern to watch for, along with the callback to call.
        :param async: On py2 will create another thread to run the err_watcher callbacks. On py3 will use corountines instead.
          Setting async to false means the monitor() method need to be called periodically in order to check for pattern in the output
        """

        self._lock = threading.RLock()
        self._out_watcher = OrderedDict()
        self._out_cpl_pattern = None
        self._err_watcher = OrderedDict()
        self._err_cpl_pattern = None

        # same as add_err_watcher and add_out_watcher
        # careful we need to keep keys order here...
        if out_watchers:
            self.add_out_watcher(out_watchers)
        if err_watchers:
            self.add_err_watcher(err_watchers)

        if async:
            # Optional function, can be used if we are not calling monitor from current process
            # CAREFUL : callback will be done in another thread
            def event_loop():   # TODO : make this an event loop with asyncio and python 3
                """
                Function to monitor the registry entry for this process.
                This needs to be called by the update method of the parent process
                """
                with self.monitor_context as mc:
                    while self._expect_out.isalive() or self._expect_err.isalive():
                        self.monitor(mc)

            # async in python3 doesnt need a thread...
            threading.Thread(name='threaded_eventloop', target=event_loop)


    def attach(self, process):

        self._process = psutil.Process(pid=process.pid)

        # the pexpect/ptyprocess case (simpler)
        if hasattr(process, 'read') and hasattr(process, 'write'):
            self._expect_out = process
            self._expect_err = process

        # the more complex subprocess case (hooking onto subprocess pipes)
        elif hasattr(process, 'stdout') and hasattr(process, 'stderr'):
            self._expect_out = pexpect.fdpexpect.fdspawn(process.stdout)
            self._expect_err = pexpect.fdpexpect.fdspawn(process.stderr)


    def ppid(self):
        """ delegating to _process """
        return self._process.ppid()


    def expect(self, pattern_list, timeout=-1, searchwindowsize=-1, async=False):
        if self._expect_out:
            return self._expect_out.expect(pattern=pattern_list, timeout=timeout, searchwindowsize=searchwindowsize, async=async)

    def expect_exact(self, pattern_list, timeout=-1, searchwindowsize=-1, async=False):
        if self._expect_out:
            return self._expect_out.expect(pattern=pattern_list, timeout=timeout, searchwindowsize=searchwindowsize, async=async)

    def add_err_watcher(self, watchers):
        for pattern, fun in watchers.items():
            with self._lock:
                self._err_watcher[pattern] = fun
                #self._err_cpl_pattern = self._expect_err.compile_pattern_list(self._err_watcher.keys())

    def add_out_watcher(self, watchers):
        for pattern, fun in watchers.items():
            with self._lock:
                self._out_watcher[pattern] = fun
                #self._out_cpl_pattern = self._expect_out.compile_pattern_list(self._out_watcher.keys())

    @contextlib.contextmanager
    def monitor_context(self):
        last_err_cpl = self._err_watcher.keys()
        last_out_cpl = self._out_watcher.keys()
        self._err_cpl_pattern = self._expect_err.compile_pattern_list(last_err_cpl)
        self._out_cpl_pattern = self._expect_out.compile_pattern_list(last_out_cpl)
        yield last_out_cpl, last_err_cpl

    def monitor(self, monitor_context):
        """
        Function to monitor the registry entry for this process.
        This needs to be called by the update method of the parent process
        """

        # if there is a change in patterns to watch, we recompile it
        if monitor_context[1] != self._err_watcher.keys():
            self._err_cpl_pattern = self._expect_err.compile_pattern_list(self._err_watcher.keys())
        if monitor_context[0] != self._out_watcher.keys():
            self._out_cpl_pattern = self._expect_out.compile_pattern_list(self._out_watcher.keys())

        try:
            with self._lock:
                # TODO : make this a corountine with asyncio and python 3
                i = self.expect(self._err_watcher, 1)
                if i:
                    # calling function for this pattern
                    self._err_watcher[i]()

                # TODO : make this a corountine with asyncio and python 3
                i = self.expect(self._out_watcher, 1)
                if i:
                    # calling function for this pattern
                    self._out_watcher[i]()
        except pexpect.TIMEOUT:
            pass

        # need this for a delayed cleanup in case of process termination/crash
        if not self.is_running():
            pid_registry.pop(self.pid)

    def terminate(self):
        return super(ProcessObserver, self).terminate()

    def kill(self):
        return super(ProcessObserver, self).kill()

    def __del__(self):
        """Upong deletion, we want to get rid of everything, as properly as possible"""
        for p in self.children():
            p.terminate()
        gone, still_alive = psutil.wait_procs(self, timeout=3, callback=on_terminate)
        for p in still_alive:
            p.kill()


def discover_process(name_regex='.*', timeout=None):
    """
    Discovers all processes.
    Note : we do not want to make the discovery block undefinitely since we never know for sure if a process is running or not
    TODO : improve with future...
    :param name_regex: regex to filter the nodes by name/uuid
    :param timeout: maximum number of seconds the discover can wait for a discovery matching requirements. if None, doesn't wait.
    """
    start = time.time()
    endtime = timeout if timeout else 0

    reg = re.compile(name_regex)

    while True:
        timed_out = time.time() - start > endtime
        dp = {
            p: ProcessObserver(pid_registry[p])
            for p in pid_registry if reg.match(p)
        # filtering by regex here TODO : move that feature to the Registry
        }  # return right away if we have something

        if dp:
            return dp
        elif timed_out:
            break
        # else we keep looping after a short sleep ( to allow time to refresh services list )
        time.sleep(0.2)  # sleep
    return None

