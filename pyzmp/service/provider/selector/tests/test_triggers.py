# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function


"""
This test will check the current selector configuration,
and determine which triggers are currently operational.
"""


def test_manual_trigger():
    # test manual trigger actually triggers (to handle events right now)
    pass


def test_timeout_trigger():
    # test timeout triggers (to handle predetermined delayed events)
    pass


def test_keypress_trigger():
    # test keypress triggers (to handle keypress events)
    pass


def test_mouseevent_trigger():
    # test mouseevent triggers (to handle mouse events)
    pass


def test_filesystem_trigger():
    # test filesystem changes triggers (to handle FS changes)
    pass


def test_signal_trigger():
    # test an OS signal actually triggers (to handle interprocess communication via OS posix way)
    pass


def test_pipes_trigger():
    # test a pipe event actually triggers (to handle interprocess communication via OS posix way)
    pass


def test_shared_memory_trigger():  # zmq inproc # useful for threaded implementation...

    pass


def test_unix_domain_socket_trigger():  # zmq ipc

    pass


def test_socket_tcp_trigger():  # zmq tcp
    # test a socket event triggers (to handle interprocess communication via socket - unix or network)
    pass

# TODO : more network transport  / socket types