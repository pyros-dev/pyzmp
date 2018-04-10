# -*- coding: utf-8 -*-
# This python package is implementing a very simple multiprocess framework
# The point of it is to be able to fully tests the multiprocess behavior,
#     in pure python, without having to run a ROS system.
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import tempfile
import multiprocessing, multiprocessing.reduction
import types
import uuid

import errno
import zmq
import socket
import logging
import pickle
import contextlib
#import dill as pickle

# allowing pickling of exceptions to transfer it
from collections import namedtuple

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

### IMPORTANT : COMPOSITION -> A SET OF NODE SHOULD ALSO 'BE' A NODE ###
### IMPORTANT : IDENTITY
### Category Theory https://en.wikipedia.org/wiki/Category_theory

### Data Flow with topic :
#
# object : message
# arrow : topic_listener
# binary op - associativity : listener l1, l2, l3 <= (l1 . l2) .l3 == l1. (l2. l3)
# binary op - identity : noop on listener => msg transfer as is
# -> Expressed in programming language (functional programming follows category theory) :
# msg3 = topic2_listener(topic1_listener(msg1))

# -> Expressed in graph :
# msg3 <--topic2_listener-- msg2 <--topic1_listener-- msg1

### RPC with services :
#
# object : (req, resp)
# arrow : service_call
# binary op - associativity : service s1, s2, s3 <= (s1 . s2) .s3 == s1. (s2. s3)
# binary op - identity : noop on service => (req, resp) transfer as is ( two ways comm )
# -> Expressed in programming language (functional programming follows category theory) :
#  (req3, resp3) = service2_call(service1_call((req1, resp1)))

# -> Expressed in graph :
# msg1 --service1_call--> msg2 --service2_call--> msg3

###### higher level for execution graph to be represented by a category ######

# TODO : CAREFUL topic is probably not a complete concept in itself
# => often we need to get back to pub / sub connections rather than dealing with "topics"
# We need the reverse flow of "service call" which is a distributed generalisation of function call
# We need the distributed generalisation of the callback function ( async calls and futures )

### Service is a first class citizen. node is abstracted in that perspective : implementation requires some discovery mechanism.
# object : service
# arrow : call
# binary op - associativity : call c1, c2, c3 <= (c1 . c2) .c3 == c1 . (c2 . c3)
# binary op - identity : ??? TODO
# -> Expressed in programming language (functional programming follows category theory) :
#  svc1 = lambda x: return ( lambda y: return svc3(y) )( x )  <= currying/partial => svc1 = lambda x, y : return svc23(x,y)

# -> Expressed in graph :
# svc1 --call--> svc2 --call--> svc3

### Node is a first class citizen
# object : node
# arrow : topic_listener / callback
# binary op - associativity : callback cb1. cb2. cb3 <= (cb1 . cb2) . cb3 == cb1 . (cb2 . cb3)
# binary op - identity : ??? TODO
# -> Expressed in programming language (functional programming follows category theory) :
#  node1.cb = lambda x: return ( lambda y: return node3.cb(y) )(x) <= currying/partial => node1.cb = lambda x, y : return node23(x,y)

# -> Expressed in graph :
# node3 <--topic_cb-- node2 <--topic_cb-- node1

from .master import manager
from .exceptions import UnknownServiceException, UnknownRequestTypeException
from .message import ServiceRequest, ServiceRequest_dictparse, ServiceResponse, ServiceException
from .service import service_provider_cm
#from .service import RequestMsg, ResponseMsg, ErrorMsg  # only to access message types





def maybe_tuple(a):
    return a if isinstance(a, tuple) else (a,)


# CAREFUL here : multiprocessing documentation specifies that a process object can be started only once...
class CoProcess(object):
    """
    A Collaborative Process (co- as in coroutines)
    Guarantees (process-level) Atomicity and (process-level) Isolation (as in ACID acronym)
    Interruption are signals only, following POSIX standard (for now...)
    Note that it can only keep guarantees that executed code does not violate
    Therefore using async coroutines inside, and implement pure functional features from outside perspective, is the preferred style.
    """
    # TODO : UNTANGLE this with asyncio.
    # We have here and event loop inside a process, but it should be more modular...
    # maybe also add a distributed constant scheduler (like erlang VM : each loop gets equal amount of cycles)...
    EndPoint = namedtuple("EndPoint", "self func")

    # TODO : allow just passing target to be able to make a Node from a simple function, and also via decorator...
    def __init__(self, name=None, context_manager=None, target=None, args=None, kwargs=None):
        # TODO : types hint to check context signature would avoid concurrency issues
        """
        Initializes a ZMP Node (Restartable Python Process communicating via ZMQ)
        :param name: Name of the node
        :param context_manager: a context_manager to be used with run (in a with statement)
        :return:
        """
        # TODO check name unicity
        # using process as delegate
        self._pargs = {
            'name': name or str(uuid.uuid4()),
            'args': args or (),
            'kwargs': kwargs or {},
            'target': self.run,  # Careful : our run() is not the same as the one for Process
        }
        # Careful : our own target is not the same as the one for Process
        self._target = target or self.task

        #: the actual process instance. lazy creation on start() call only.
        self._process = None

        #: whether or not the node name should be set as the actual process title
        #: replacing the string duplicated from the python interpreter run
        self.new_title = True

        self._user_ctx = context_manager
        self.context_manager = self.__chained_ctx  # TODO: extend to list if possible ( available for python >3.1 only )

        self.exit = multiprocessing.Event()
        self.started = multiprocessing.Event()

        self.tmpdir = tempfile.mkdtemp(prefix='zmp-' + self.name + '-')

    def __enter__(self):
        # __enter__ is called only if we pass this instance to with statement ( after __init__ )
        # start only if needed (so that we can hook up a context manager to a running node) :
        if not self.is_alive():
            self.start()
            # Note : start() will spawn the child process, which will enter it s own child_context
            # in effect actually chaining this context and its own internal context before retuning
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        # make sure we cleanup when we exit
        self.shutdown()

    # TODO : decorator to easily mix functional(via param) and inheritance(OO) API styles
    # See type classes, traits, etc.
    @contextlib.contextmanager
    def __chained_ctx(self, *args, **kwargs):
        # CAREFUL with timing constraints
        # TODO check with python 3.1 and list of CMs...
        with self.child_context(*args, **kwargs) as cm:

            ctxt = tuple()

            if cm is not None:
                ctxt = ctxt + maybe_tuple(cm)

            if self._user_ctx:
                with self._user_ctx(*args, **kwargs) as ucm:
                    if ucm is not None:
                        ctxt = ctxt + maybe_tuple(ucm)
                        # skipping Empty (None) Context

                    if ctxt:
                        yield ctxt
                    else:
                        yield

            else:
                if ctxt:
                    yield ctxt
                else:
                    yield

    @contextlib.contextmanager
    def child_context(self, *args, **kwargs):
        yield

    def has_started(self):
        """
        :return: True if the node has started (update() might not have been called yet). Might still be alive, or not...
        """
        return self.started.is_set()

    ### Process API delegation ###
    def is_alive(self):
        if self and self._process:
            return self._process.is_alive()

    def join(self, timeout=None):
        if not self._process:
            # blocking on started event before blocking on join
            self.started.wait(timeout=timeout)
        return self._process.join(timeout=timeout)

    @property
    def name(self):
        if self and self._process:
            return self._process.name
        else:
            return self._pargs.get('name', "ZMPNode")

    @name.setter
    def name(self, name):
        if self and self._process:
            self._process.name = name
            # only reset the name arg if it was accepted by the setter
            self._pargs['name']= self._process.name
        else:
            # TODO : maybe we should be a bit more strict here ?
            self._pargs['name']= name

    @property
    def daemon(self):
        """
        Return whether process is a daemon
        :return:
        """
        if self._process:
            return self._process.daemon
        else:
            return self._pargs.get('daemonic', False)

    @daemon.setter
    def daemon(self, daemonic):
        """
        Set whether process is a daemon
        :param daemonic:
        :return:
        """
        if self._process:
            self._process.daemonic = daemonic
        else:
            self._pargs['daemonic'] = daemonic

    @property
    def authkey(self):
        return self._process.authkey

    @authkey.setter
    def authkey(self, authkey):
        """
        Set authorization key of process
        """
        self._process.authkey = authkey

    @property
    def exitcode(self):
        """
        Return exit code of process or `None` if it has yet to stop
        """
        if self._process:
            return self._process.exitcode
        else:
            return None

    @property
    def ident(self):
        """
        Return identifier (PID) of process or `None` if it has yet to start
        """
        if self._process:
            return self._process.ident
        else:
            return None

    def __repr__(self):
        # TODO : improve this
        return self._process.__repr__()

    def start(self, timeout=None):
        """
        Start child process
        :param timeout: the maximum time to wait for child process to report it has actually started.
        None waits until the context manager has been entered, but update might not have been called yet.
        """

        # we lazily create our process delegate (with same arguments)
        if self.daemon:
            daemonic = True
        else:
            daemonic = False

        pargs = self._pargs.copy()
        pargs.pop('daemonic', None)

        self._process = multiprocessing.Process(**pargs)

        self._process.daemon = daemonic

        if self.is_alive():
            # if already started, we shutdown and join before restarting
            # not timeout will bock here (default join behavior).
            # otherwise we simply use the same timeout.
            self.shutdown(join=True, timeout=timeout)  # TODO : only restart if no error (check exitcode)
            self.start(timeout=timeout)  # recursive to try again if needed
        else:
            self._process.start()

        # timeout None means we want to wait and ensure it has started
        # deterministic behavior, like is_alive() from multiprocess.Process is always true after start()
        if self.started.wait(timeout=timeout):  # blocks until we know true or false


            return True
            # return self._svc_address  # returning the zmp url as a way to connect to the node
            # CAREFUL : doesnt make sense if this node only run a one-time task...
        # TODO: futures and ThreadPoolExecutor (so we dont need to manage the pool ourselves)
        else:
            return False

    # TODO : Implement a way to redirect stdout/stderr, or even forward to parent ?
    # cf http://ryanjoneil.github.io/posts/2014-02-14-capturing-stdout-in-a-python-child-process.html

    def terminate(self):
        """Forcefully terminates the underlying process (using SIGTERM)"""
        return self._process.terminate()
        # TODO : maybe redirect to shutdown here to avoid child process leaks ?


    # TODO : shortcut to discover/build only services provided by this node ?


    def shutdown(self, join=True, timeout=None):
        """
        Clean shutdown of the node.
        :param join: optionally wait for the process to end (default : True)
        :return: None
        """
        if self.is_alive():  # check if process started
            print("Shutdown initiated")
            self.exit.set()
            if join:
                self.join(timeout=timeout)
                # TODO : timeout before forcing terminate (SIGTERM)

        exitcode = self._process.exitcode if self._process else None  # we return None if the process was never started
        return exitcode

    def task(self, *args, **kwargs):
        """Child classes must define this method, that will be executed in a separate process,
        giving *some* Atomicity and Isolation guarantees (see ACID and BASE acronym for background on this)"""
        return  # careful : no side effects (exceptions or logs) by default !

    def eventloop(self, *args, **kwargs):
        """
        Hand crafted event loop, with only one event possible : exit
        More events ( and signals ) can be added later, after converting to asyncio.
        """

        # Setting status
        status = None

        # Starting the clock
        start = time.time()

        first_loop = True
        # loop running target, maybe more than once
        while not self.exit.is_set():

            if first_loop:
                first_loop = False
                # signalling startup only the first time, just after having check for exit request.
                # We need to return control before starting, but after entering context...
                self.started.set()
                # TODO : check if better outside of loop maybe ??
                # It will change semantics, but might be more intuitive...

            # time is ticking
            # TODO : move this out of here. this class should require only generic interface to any method.
            now = time.time()
            timedelta = now - start
            start = now

            # replacing the original Process.run() call, passing arguments to our target
            if self._target:
                # bwcompat
                kwargs['timedelta'] = timedelta

                # TODO : use return code to determine when/how we need to run this the next time...
                # Also we need to keep the exit status to be able to call external process as an update...

                logging.debug(
                    "[{self.name}] calling {self._target.__name__} with args {args} and kwargs {kwargs}...".format(
                        **locals()))
                status = self._target(*args, **kwargs)

            if status is not None:
                break

        if self.started.is_set() and status is None and self.exit.is_set():
            # in the not so special case where we started, we didnt get exit code and we exited,
            # this is expected as a normal result and we set an exitcode here of 0
            # As 0 is the conventional success for unix process successful run
            status = 0

        return status

    def run(self, *args, **kwargs):
        """
        The Node main method, running in a child process (similar to Process.run() but also accepts args)
        A children class can override this method, but it needs to call super().run(*args, **kwargs)
        for the node to start properly and call update() as expected.
        :param args: arguments to pass to update()
        :param kwargs: keyword arguments to pass to update()
        :return: last exitcode returned by update()
        """
        # TODO : make use of the arguments ? since run is now the target for Process...

        exitstatus = None  # keeping the semantic of multiprocessing.Process : running process has None

        if setproctitle and self.new_title:
            setproctitle.setproctitle("{0}".format(self.name))

        print('[{proc}] Proc started as [{pid}]'.format(proc=self.name, pid=self.ident))

        with self.context_manager(*args, **kwargs) as cm:
            if cm:
                cmargs = maybe_tuple(cm)
                # prepending context manager, to be able to access it from target
                args = cmargs + args

            exitstatus = self.eventloop(*args, **kwargs)

            logging.debug("[{self.name}] Proc exited.".format(**locals()))
            return exitstatus  # returning last exit status from the update function

        # all context manager is destroyed properly here




