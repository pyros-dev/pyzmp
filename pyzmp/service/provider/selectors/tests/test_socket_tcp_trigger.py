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


# def find_free_port_number():
#     socket.


def fuzz():
    time.sleep(random.randint(0, 1000) / 1000.0)


# @pytest.fixture
# def server_pub_tcp_port(server_pub_port="5558"):  # TODO : port 0 with zmq ?
#     def run(port, evt):
#         context = zmq.Context()
#         socket = context.socket(zmq.PUB)
#         socket.bind("tcp://127.0.0.1:{0}".format(port))
#         publisher_id = random.randrange(0, 9999)
#         print("Running server on port: {0}".format(port))
#         topic = 9  # need to match the topic expected by the client
#         messagedata = "server#{0}".format(publisher_id)
#
#         # Ref : http://zguide.zeromq.org/page:all#Node-Coordination
#         msg_sent = 0
#         while msg_sent < 5:  # publish only 5 meaningful messages and dies
#             if evt.wait(timeout=.5):  # a timeout of .5 secs means subscriber is not connected (yet|anymore)...
#                 print("EVENT !")
#                 evt.clear()  # we need to clear before sending !
#                 print("Publishing {0} {1}".format(topic, messagedata))
#                 socket.send("{0} {1}".format(topic, messagedata))
#                 msg_sent += 1
#             else:
#                 print("EVENT TIMEOUT...")
#                 # spamming until we get reply from subscriber to signal it is ready to receive messages
#                 socket.send("RDY?")  # to unblock subscriber polling and make sure we will get the next event
#
#     evt = Event()
#     Process(target=run, args=(server_pub_port, evt)).start()
#     return server_pub_port, evt


# TODO : test all implemented transport : Ref http://api.zeromq.org/2-1:_start
# TODO : test all socket types : Ref http://api.zeromq.org/2-1:zmq-socket
# The goal is to validate the current running configuration, even for a user.


# def test_client_pub_tcp(server_pub_tcp_port):
#     context = zmq.Context()
#     socket_sub = context.socket(zmq.SUB)
#     socket_sub.connect("tcp://localhost:{0}".format(server_pub_tcp_port[0]))
#     socket_sub.setsockopt(zmq.SUBSCRIBE, "9")
#     print("Connected to publisher with port {0}".format(server_pub_tcp_port[0]))
#
#     # Initialize poll set
#     poller = zmq.Poller()
#     poller.register(socket_sub, zmq.POLLIN)
#
#     msg_recvd = 0  # get only 5 messages and dies
#     while msg_recvd < 5:
#
#         print ("POLL()")
#         socks = dict(poller.poll())  # blocking until poller detect event
#
#         print ("MESSAGE !")
#         if socket_sub in socks and socks[socket_sub] == zmq.POLLIN:
#             string = socket_sub.recv()  # blocking until message is received
#             if string == "RDY?":
#                 print ("SET()")
#                 server_pub_tcp_port[1].set()  # signaling to publisher we are ready (making communication synchronous)
#                 continue  # looping to set event and get next message
#             else:
#                 topic, messagedata = string.split()
#                 print("Receiving {0} {1}".format(topic, messagedata))
#                 msg_recvd += 1
#         else:
#             print("Unexpected event on socket_sub")

def test_push_pull_tcp():

    def client(port, evt):
        context = zmq.Context()
        socket_push = context.socket(zmq.PUSH)
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

    start_evt = multiprocessing.Event()
    multiprocessing.Process(target=client, args=("5558", start_evt)).start()

    context = zmq.Context()
    context.setsockopt(socket.SO_REUSEADDR, 1)  # required to make restart easy and avoid debugging traps...
    socket_pull = context.socket(zmq.PULL)
    socket_pull.bind("tcp://127.0.0.1:{0}".format("5558"))
    print("Running consumer on port: {0}".format("5558"))

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

@pytest.mark.skip
def test_pull_push_tcp():  # "symmetric" regarding bind/connect with "same" push/pull (contravariant ?)

    def client(port, evt):
        with zmq.Context() as context:
            socket_pull = context.socket(zmq.PULL)
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

    start_evt = multiprocessing.Event()
    multiprocessing.Process(target=client, args=("5558", start_evt)).start()

    with zmq.Context() as context:
        context.setsockopt(socket.SO_REUSEADDR, 1)  # required to make restart easy and avoid debugging traps...
        socket_push = context.socket(zmq.PUSH)
        socket_push.bind("tcp://127.0.0.1:{0}".format("5558"))
        print("Running producer on port: {0}".format("5558"))

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
        with zmq.Context() as context:
            socket = context.socket(zmq.REQ)
            socket.connect("tcp://127.0.0.1:{0}".format("5557"))
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

    start_evt = multiprocessing.Event()
    client_proc = multiprocessing.Process(target=client, args=("5557", start_evt))
    client_proc.start()

    # Server
    with zmq.Context() as context:
        context.setsockopt(socket.SO_REUSEADDR, 1)  # required to make restart easy and avoid debugging traps...
        socket_rep = context.socket(zmq.REP)
        socket_rep.bind("tcp://127.0.0.1:{0}".format("5557"))
        print("Server ready on port {0}".format("5557"))

        # Initialize poll set
        poller = zmq_poller()
        poller.register(socket_rep, zmq.POLLIN)

        # Work on requests from client
        reqnum = 0

        # wait until se are
        start_evt.set()  # signal we are ready to start serving client requests
        while reqnum < 4:
            socks = dict(poller.poll())
            if socket_rep in socks and socks[socket_rep] == zmq.POLLIN:
                socket_rep.recv()  # getting (and ignoring) request data
                reqnum += 1
                socket_rep.send(b"Got it !")

    client_proc.join()






                        # # One fixture == One process strategy
# # to test things as independently from each other as possible (we still fork from the same interpreter though...)
# class TestSocketTCPTrigger(UnitTest):
#     def __init__(self, *args, **kwargs):
#         super(TestSocketTCPTrigger, self).__init__(*args, **kwargs)
#
#     def setup(self):
#         pass
#
#     def teardown(self):
#         pass
#
#
if __name__ == "__main__":
#     # Now we can run a few servers
#     server_push_port = "5556"
#     server_rep_port = "5557"
#     server_pub_port = "5558"
#     Process(target=server_push_tcp, args=(server_push_port,)).start()
#     Process(target=server_rep_tcp, args=(server_rep_port,)).start()
#     Process(target=server_pub_tcp, args=(server_pub_port,)).start()
#     Process(target=client, args=(server_push_port, server_pub_port,)).start()
    pytest.main(['-s', '-x', __file__])
