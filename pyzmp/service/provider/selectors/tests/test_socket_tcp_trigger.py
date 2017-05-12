from __future__ import absolute_import
from __future__ import print_function

"""
Simple test to validate capabilities of zmq poller.
Also serves as code example for zmq implementation.
"""

# Ref : http://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/multisocket/zmqpoller.html
import os

import zmq
import time
import sys
import random
import pytest
import multiprocessing
import socket
import six


from pyzmp.service.provider.selectors.zmq_poller import zmq_poller


def fuzz():
    time.sleep(random.randint(0, 1000) / 1000.0)


def test_push_pull_tcp():

    def client(port, evt):
        client_context = zmq.Context()
        socket_push = client_context.socket(zmq.PUSH)
        socket_push.connect("tcp://localhost:{0}".format(port))
        print("Connected to consumer with port {0}".format(port))

        evt.wait()  # wait until server is ready to receive...
        # send only 5 messages and dies
        for reqnum in range(5):
            print("pushing msg {0}".format(reqnum))
            try:
                socket_push.send(b"msg %c" % reqnum)
            except Exception as e:
                raise e
            fuzz()

    context = zmq.Context()
    context.setsockopt(socket.SO_REUSEADDR, 1)  # required to make restart easy and avoid debugging traps...
    socket_pull = context.socket(zmq.PULL)
    port = socket_pull.bind_to_random_port("tcp://127.0.0.1")
    print("Running consumer on port: {0}".format(port))

    start_evt = multiprocessing.Event()
    client_proc = multiprocessing.Process(target=client, args=(port, start_evt))
    client_proc.daemon = True  # to have it die when parent finishes, to avoid blocking tests, just in case.
    client_proc.start()

    # Initialize poll set
    poller = zmq_poller()
    poller.register(socket_pull, zmq.POLLIN)

    # Work on requests from client
    reqnum = 0

    start_evt.set()  # signal we are ready to start serving client requests
    while reqnum < 5:
        socks = dict(poller.poll())
        if socket_pull in socks and socks[socket_pull] == zmq.POLLIN:
            msg = socket_pull.recv()  # getting (and ignoring) request data
            print("pulling {0}".format(msg))
            reqnum += 1


def test_pull_push_tcp():  # "symmetric" regarding bind/connect with "same" push/pull (contravariant ?)

    def client(port, evt):
        # with zmq.Context() as context: BLOCKING ... BUG ?
        client_context = zmq.Context()
        socket_pull = client_context.socket(zmq.PULL)
        socket_pull.connect("tcp://localhost:{0}".format(port))
        print("Connected to producer with port {0}".format(port))

        # Initialize poll set
        poller = zmq_poller()
        poller.register(socket_pull, zmq.POLLIN)

        # Work on requests from client
        reqnum = 0

        evt.set()  # signal we are ready to start consuming client requests
        while reqnum < 5:
            socks = dict(poller.poll())
            if socket_pull in socks and socks[socket_pull] == zmq.POLLIN:
                msg = socket_pull.recv()  # getting (and ignoring) request data
                print("pulling {0}".format(msg))
                reqnum += 1

    # with zmq.Context() as context: BLOCKING... BUG ?
    context = zmq.Context()
    socket_push = context.socket(zmq.PUSH)
    port = socket_push.bind_to_random_port("tcp://127.0.0.1")
    print("Running producer on port: {0}".format(port))

    start_evt = multiprocessing.Event()
    client_proc = multiprocessing.Process(target=client, args=(port, start_evt))
    client_proc.daemon = True  # to have it die when parent finishes, to avoid blocking tests, just in case.
    client_proc.start()

    start_evt.wait()  # wait until we are ready to receive...
    # send only 5 messages and dies
    for reqnum in range(5):
        print("pushing msg {0}".format(reqnum))
        try:
            socket_push.send(b"msg %c" % reqnum)
        except Exception as e:
            raise e
        fuzz()


def test_req_rep_tcp():

    def client(port, evt):
        # with zmq.Context() as context: BLOCKING... BUG ?
        client_context = zmq.Context()
        socket = client_context.socket(zmq.REQ)
        socket.connect("tcp://127.0.0.1:{0}".format(port))
        print("Client connected on port: {0}".format(port))

        evt.wait()  # wait until server is ready to receive...
        # send only 5 request and dies
        for reqnum in range(5):
            print("req {0} => ".format(reqnum), end='')
            try:
                socket.send(b"msg %c" % reqnum)
            except Exception as e:
                # CAREFUL : excepting here will block the test (server is still waiting...)
                raise e
            resp = socket.recv()  # getting ( and ignoring ) response data
            print("resp {0}".format(resp))
            fuzz()

    # Server
    # with zmq.Context() as context: BLOCKING...
    context = zmq.Context()
    context.setsockopt(socket.SO_REUSEADDR, 1)  # required to make restart easy and avoid debugging traps...
    socket_rep = context.socket(zmq.REP)
    port = socket_rep.bind_to_random_port("tcp://127.0.0.1")
    print("Server ready on port {0}".format(port))

    start_evt = multiprocessing.Event()
    client_proc = multiprocessing.Process(target=client, args=(port, start_evt))
    client_proc.daemon = True  # to have it die when parent finishes, to avoid blocking tests, just in case.
    client_proc.start()

    # Initialize poll set
    poller = zmq_poller()
    poller.register(socket_rep, zmq.POLLIN)

    # Work on requests from client
    reqnum = 0

    # wait until se are
    start_evt.set()  # signal we are ready to start serving client requests
    while reqnum < 5:
        socks = dict(poller.poll())
        if socket_rep in socks and socks[socket_rep] == zmq.POLLIN:
            socket_rep.recv()  # getting (and ignoring) request data
            reqnum += 1
            socket_rep.send(b"Got it !")


if __name__ == "__main__":
    pytest.main(['-s', '-x', __file__])
