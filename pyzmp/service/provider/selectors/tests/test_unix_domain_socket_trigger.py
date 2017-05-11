# Ref : http://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/multisocket/zmqpoller.html

import zmq
import time
import sys
import random
import pytest
import multiprocessing


def server_push_ipc(port="5556"):
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.bind("ipc://*:{0}".format(port))
    print("Running server on port: {0}".format(port))
    # serves only 5 request and dies
    for reqnum in range(10):
        if reqnum < 6:
            socket.send("Continue")
        else:
            socket.send("Exit")
            break
        time.sleep(1)


def server_pub_ipc(port="5558"):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("ipc://*:%s" % port)
    publisher_id = random.randrange(0, 9999)
    print("Running server on port: {0}".format(port))
    # serves only 5 request and dies
    for reqnum in range(10):
        # Wait for next request from client
        topic = random.randrange(8, 10)
        messagedata = "server#{0}".format(publisher_id)
        print("{0} {1}".format(topic, messagedata))
        socket.send("{0} {1}".format(topic, messagedata))
        time.sleep(1)


def server_rep_ipc(port="5558"):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("ipc://*:{0}".format(port))
    publisher_id = random.randrange(0, 9999)
    print("Running server on port: {0}".format(port))
    # serves only 5 request and dies
    for reqnum in range(10):
        # Wait for next request from client
        topic = random.randrange(8, 10)
        messagedata = "server#{0}".format(publisher_id)
        print("{0} {1}".format(topic, messagedata))
        socket.send("{0} {1}".format(topic, messagedata))
        time.sleep(1)


# TODO : test all socket types : Ref http://api.zeromq.org/2-1:zmq-socket
# The goal is to validate the current running configuration, even for a user.
# And make sure the selector works for any type of socket (in case the user wants to customize its ZMQ socket type...)


def client(port_push, port_sub):
    context = zmq.Context()
    socket_pull = context.socket(zmq.PULL)
    socket_pull.connect("tcp://localhost:{0}".format(port_push))
    print("Connected to server with port {0}".format(port_push))
    socket_sub = context.socket(zmq.SUB)
    socket_sub.connect("tcp://localhost:{0}".format(port_sub))
    socket_sub.setsockopt(zmq.SUBSCRIBE, "9")
    print("Connected to publisher with port {0}".format(port_sub))
    # Initialize poll set
    poller = zmq.Poller()
    poller.register(socket_pull, zmq.POLLIN)
    poller.register(socket_sub, zmq.POLLIN)

    # Work on requests from both server and publisher
    should_continue = True
    while should_continue:
        socks = dict(poller.poll())
        if socket_pull in socks and socks[socket_pull] == zmq.POLLIN:
            message = socket_pull.recv()
            print("Received control command: {0}".format(message))
            if message == "Exit":
                print("Received exit command, client will stop recieving messages")
                should_continue = False

        if socket_sub in socks and socks[socket_sub] == zmq.POLLIN:
            string = socket_sub.recv()
            topic, messagedata = string.split()
            print("Processing ... {0} {1}".format(topic, messagedata))


# One fixture == One process strategy
# to test things as independently from each other as possible (we still fork from the same interpreter though...)
class TestProactor(object):
    def __init__(self, *args, **kwargs):
        super(TestProactor, self).__init__(*args, **kwargs)

    def setup(self):
        pass

    def teardown(self):
        pass


if __name__ == "__main__":
    # Now we can run a few servers
    server_push_port = "5556"
    server_pub_port = "5558"
    multiprocessing.Process(target=server_push, args=(server_push_port,)).start()
    multiprocessing.Process(target=server_pub, args=(server_pub_port,)).start()
    multiprocessing.Process(target=client, args=(server_push_port, server_pub_port,)).start()