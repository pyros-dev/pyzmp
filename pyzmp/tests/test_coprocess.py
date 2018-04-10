# -*- coding: utf-8 -*-
from __future__ import absolute_import

# To allow python to run these tests as main script
import contextlib
import functools
import multiprocessing
import sys
import os
import threading

import types
from random import randint

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import time
import pyzmp

import pytest
# http://pytest.org/latest/contents.html
# https://github.com/ionelmc/pytest-benchmark

# TODO : PYPY
# http://pypy.org/

# TODO : Test Node exception : correctly transmitted, process still keeps spinning...


@pytest.mark.timeout(5)
def test_process_termination():
    """Checks that a process can be shutdown without being started and indicate that it never ran"""
    n1 = pyzmp.CoProcess()
    assert not n1.is_alive()
    exitcode = n1.shutdown()  # shutdown should have no effect here (if not started, same as noop )
    assert exitcode is None  # exitcode should be None (process didn't start and didn't stop so no exit code)
    assert not n1.is_alive()


@pytest.mark.timeout(5)
def test_process_creation_termination():
    """Checks that a process can be started and shutdown and indicate that it ran successfully"""
    n1 = pyzmp.CoProcess()
    assert not n1.is_alive()
    svc_url = n1.start()
    assert n1.is_alive()
    assert svc_url
    exitcode = n1.shutdown()
    assert exitcode == 0  # default process should spin without issues
    assert not n1.is_alive()


@pytest.mark.timeout(5)
def test_process_timeout_creation_termination():
    """Checks that a process can be started with timeout and shutdown and indicate that it ran successfully"""
    n1 = pyzmp.CoProcess()
    assert not n1.is_alive()
    svc_url = n1.start(1)
    assert svc_url
    assert n1.is_alive()
    exitcode = n1.shutdown()
    assert exitcode == 0
    assert not n1.is_alive()


# @nose.SkipTest  # to help debugging ( FIXME : how to programmatically start only one test - maybe in fixture - ? )
@pytest.mark.timeout(5)
def test_process_double_creation_termination():
    """Checks that a process can be started twice and shutdown and indicate that it ran successfully"""
    n1 = pyzmp.CoProcess()
    assert not n1.is_alive()
    svc_url1 =n1.start()
    assert n1.is_alive()
    assert svc_url1
    svc_url2 = n1.start()  # this shuts down properly and restart the process
    assert n1.is_alive()
    assert svc_url2

    # the process is the same (same id) so we should get same url
    assert svc_url1 == svc_url2

    exitcode = n1.shutdown()
    assert exitcode == 0
    assert not n1.is_alive()


# @nose.SkipTest  # to help debugging ( FIXME : how to programmatically start only one test - maybe in fixture - ? )
@pytest.mark.timeout(5)
def test_process_timeout_double_creation_termination():
    """Checks that a process can be started twice with timeout and shutdown and indicate that it ran successfully"""
    n1 = pyzmp.CoProcess()
    assert not n1.is_alive()
    svc_url1 = n1.start(1)
    assert n1.is_alive()
    assert svc_url1

    svc_url2 = n1.start(1)  # this shuts down and restart the process
    assert n1.is_alive()
    assert svc_url2

    # the process is the same (same id) so we should get same url
    assert svc_url1 == svc_url2

    exitcode = n1.shutdown()
    assert exitcode == 0
    assert not n1.is_alive()


@pytest.mark.timeout(5)
def test_process_creation_double_termination():
    """Checks that a process can be started and shutdown twice and indicate that it ran successfully"""
    n1 = pyzmp.CoProcess()
    assert not n1.is_alive()

    svc_url1 = n1.start()
    assert n1.is_alive()
    assert svc_url1

    exitcode = n1.shutdown()
    assert exitcode == 0
    assert not n1.is_alive()
    exitcode = n1.shutdown()
    assert exitcode == 0  # the exit code is still 0 since we didn't restart...
    assert not n1.is_alive()


@pytest.mark.timeout(5)
def test_process_creation_args():
    """Checks that a process can be passed an argument using inheritance"""
    ns = multiprocessing.Manager().Namespace()
    ns.arg = 42

    class TestArgProcess(pyzmp.CoProcess):
        def task(self, *args, **kwargs):
            ns.arg -= args[0]
            return ns.arg

    n1 = TestArgProcess(args=(ns.arg,))
    assert not n1.is_alive()
    svc_url = n1.start()
    assert n1.is_alive()
    assert svc_url

    # starting and shutdown should at least guarantee ONE call of update function.

    exitcode = n1.shutdown()
    assert exitcode == 0
    assert not n1.is_alive()

    assert ns.arg == 0


@pytest.mark.timeout(5)
def test_process_creation_args_delegate():
    """Checks that a process can be passed an argument using delegation"""
    ns = multiprocessing.Manager().Namespace()
    ns.arg = 42

    def arguser(fortytwo, **kwargs):  # kwargs is there to accept extra arguments nicely (timedelta)
        ns.arg -= fortytwo
        return ns.arg

    n1 = pyzmp.CoProcess(args=(ns.arg,), target=arguser)
    assert not n1.is_alive()
    svc_url = n1.start()
    assert n1.is_alive()
    assert svc_url

    exitcode = n1.shutdown()
    assert exitcode == 0
    assert not n1.is_alive()

    assert ns.arg == 0


@pytest.mark.timeout(5)
def test_process_creation_kwargs():
    """Checks that a process can be passed a keyword argument using inheritance"""
    ns = multiprocessing.Manager().Namespace()
    ns.kwarg = 42

    class TestKWArgProcess(pyzmp.CoProcess):
        def task(self, *args, **kwargs):
            ns.kwarg -= kwargs.get('intval')
            return ns.kwarg

    n1 = TestKWArgProcess(kwargs={'intval': ns.kwarg, })
    assert not n1.is_alive()
    svc_url = n1.start()
    assert n1.is_alive()
    assert svc_url

    exitcode = n1.shutdown()
    assert exitcode == 0
    assert not n1.is_alive()

    assert ns.kwarg == 0


@pytest.mark.timeout(5)
def test_process_creation_kwargs_delegate():
    """Checks that a process can be passed a keyword argument using delegation"""
    ns = multiprocessing.Manager().Namespace()
    ns.kwarg = 42

    def kwarguser(intval, **kwargs):  # kwargs is there to accept extra arguments nicely (timedelta)
        ns.kwarg -= intval
        return ns.kwarg

    n1 = pyzmp.CoProcess(kwargs={'intval': ns.kwarg, }, target=kwarguser)
    assert not n1.is_alive()
    svc_url = n1.start()
    assert n1.is_alive()
    assert svc_url

    exitcode = n1.shutdown()
    assert exitcode == 0
    assert not n1.is_alive()

    assert ns.kwarg == 0


# @nose.SkipTest  # to help debugging ( FIXME : how to programmatically start only one test - maybe in fixture - ? )
@pytest.mark.timeout(5)
def test_process_as_context_manager():
    """Checks that a process can be used as a context manager"""
    with pyzmp.CoProcess() as n1:  # this will __init__ and __enter__
        assert n1.is_alive()
    assert not n1.is_alive()


# @nose.SkipTest  # to help debugging ( FIXME : how to programmatically start only one test - maybe in fixture - ? )
@pytest.mark.timeout(5)
def test_process_running_as_context_manager():
    """Checks that an already running process can be used as a context manager"""
    n1 = pyzmp.CoProcess()
    n1.start()
    with n1:  # hooking to an already started process
        # This might restart the process (might be bad but ideally should not matter.)
        assert n1.is_alive()
    assert not n1.is_alive()



@pytest.mark.timeout(5)
def test_context_before_started():
    """Checks that a coprocess initializes its context before starting """

    mgr = multiprocessing.Manager()
    # creating namespace proxy (see https://docs.python.org/3/library/multiprocessing.html#proxy-objects)
    ns = mgr.Namespace()

    mypid = os.getpid()

    # We can use the context to setup the value in the namespace
    @contextlib.contextmanager
    def ctxtuser(intval, *args, **kwargs):
        # to make sure we are in another process
        assert os.getpid() != mypid
        # ns is referenced in this closure and proxy has been passed to child process
        ns.kwarg = intval
        yield ns
        ns.kwarg = None  # to make sure we exit before shutdown returns

    def kwarguser(ns, intval, *args, **kwargs):  # kwargs is there to accept extra arguments nicely (timedelta)
        ns.kwarg -= intval
        ns.call = ns.call +1 if hasattr(ns,'call') else 1  # first call is 1
        return ns.kwarg

    n1 = pyzmp.CoProcess(kwargs={'intval': 42, }, target=kwarguser, context_manager=ctxtuser)
    assert not n1.is_alive()

    # here the context has NOT already been entered
    assert not hasattr(ns, 'kwarg')

    svc_url = n1.start()
    assert n1.is_alive()
    assert svc_url

    # here the context HAS BEEN entered
    assert hasattr(ns, 'kwarg')

    # MAYBE update has NOT already been called
    # Note we want to keep indeterminism here, as linearizability of events should only be enforced
    # via context manager with the usual method/procedure call API.
    # other events could potentially be completely asynchronous (might depend on OS / process interface)
    assert ns.kwarg in [42, 0]

    exitcode = n1.shutdown()
    assert exitcode == 0
    assert not n1.is_alive()

    # update HAS been called once (or more), and context has been exited
    assert ns.call >= 1
    assert ns.kwarg is None



### TODO : more testing in case of crash in process, exception, signal, etc.

# Just in case we run this directly
if __name__ == '__main__':
    import pytest
    pytest.main([
        '-s', __file__,
])
