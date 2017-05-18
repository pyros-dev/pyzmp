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
from .process import Process
# from .service import RequestMsg, ResponseMsg, ErrorMsg  # only to access message types

current_node = multiprocessing.current_process

# Lock is definitely needed ( not implemented in proxy objects, unless the object itself already has it, like Queue )
nodes_lock = manager.Lock()
nodes = manager.dict()
# note we do not want any "node discovery" feature here, as it might be misused.
# The nodes should not matter for the user (client of the zmp multiprocess system).
# => it is fine for a client to rebuild the list of nodes from the list of a set of services providers


# REF : http://stackoverflow.com/questions/3024925/python-create-a-with-block-on-several-context-managers


# TODO : Nodelet ( thread, with fast intraprocess zmq comm - entity system design /vs/threadpool ?)
# CAREFUL here : multiprocessing documentation specifies that a process object can be started only once...
class Node(Process):

    EndPoint = namedtuple("EndPoint", "self func")

    # TODO : allow just passing target to be able to make a Node from a simple function, and also via decorator...
    def __init__(self, name=None, socket_bind=None, target_context=None, target=None, args=None, kwargs=None):
        """
        Initializes a ZMP Node (Restartable Python Process communicating via ZMQ)
        :param name: Name of the node
        :param socket_bind: the string describing how to bind the ZMQ socket ( IPC, TCP, etc. )
        :param target_context: a context_manager to be used during "run()".
                This is used to ensure the target is called with the appropriate context
        :param target: the function to call in child process. It will be called while ti returns None. 
                When an int is returned the loop will stop.
                That loop can also be stopped by setting the terminate event (see Process).
        :param args: the arguments to pass to the target
        :param kwargs: the keywords arguments to pass to the target
        :return:
        """

        self._target = target
        target_wrap = self._update

        # careful we need to swap context managers to keep the order of calling as expected
        self.user_required_context = target_context
        # we only register the node context in for the process instance
        super(Node, self).__init__(name=name, target_context=self._node_context, target=target_wrap, args=args, kwargs=kwargs)

        self.listeners = {}
        self._providers = {}
        self.tmpdir = tempfile.mkdtemp(prefix='zmp-' + self.name + '-')
        # if no socket is specified the services of this node will be available only through IPC
        self._svc_address = socket_bind if socket_bind else 'ipc://' + self.tmpdir + '/services.pipe'

    def start(self, timeout=None):
        """
        Start child process
        :param timeout: the maximum time to wait for child process to report it has actually started.
        None waits until the update has been called at least once.
        """

        started = super(Node, self).start(timeout=timeout)

        # timeout None means we want to wait and ensure it has started
        # deterministic behavior, like is_alive() from multiprocess.Process is always true after start()
        if started:  # blocks until we know true or false
            return self._svc_address  # returning the zmp url as a way to connect to the node
            # CAREFUL : doesnt make sense if this node only run a one-time task...
        # TODO: futures and ThreadPoolExecutor (so we dont need to manage the pool ourselves)
        else:
            return False

    # TODO : Implement a way to redirect stdout/stderr, or even forward to parent ?
    # cf http://ryanjoneil.github.io/posts/2014-02-14-capturing-stdout-in-a-python-child-process.html

    def provides(self, svc_callback, service_name=None):
        service_name = service_name or svc_callback.__name__
        # we store an endpoint ( bound method or unbound function )
        self._providers[service_name] = Node.EndPoint(
            self=getattr(svc_callback, '__self__', None),
            func=getattr(svc_callback, '__func__', svc_callback),
        )

    def withholds(self, service_name):
        service_name = getattr(service_name, '__name__', service_name)
        # we store an endpoint ( bound method or unbound function )
        self._providers.pop(service_name)

    # TODO : shortcut to discover/build only services provided by this node ?


    @contextlib.contextmanager
    def _node_context(self):
        # declaring our services first
        with service_provider_cm(self.name, self._svc_address, self._providers) as spcm:
            # advertise itself
            nodes_lock.acquire()
            nodes[self.name] = {'service_conn': self._svc_address}
            nodes_lock.release()

            yield

            # concealing itself
            nodes_lock.acquire()
            nodes[self.name] = {}
            nodes_lock.release()

    @contextlib.contextmanager
    def _zmq_poller_context(self, ):
        zcontext = zmq.Context()  # check creating context in init ( compatibility with multiple processes )
        # Apparently not needed ? Ref : https://github.com/zeromq/pyzmq/issues/770
        zcontext.setsockopt(socket.SO_REUSEADDR, 1)  # required to make restart easy and avoid debugging traps...
        svc_socket = zcontext.socket(zmq.REP)  # Ref : http://api.zeromq.org/2-1:zmq-socket # TODO : ROUTER instead ?

        try:  # attempting binding socket
            svc_socket.bind(self._svc_address, )
        except zmq.ZMQError as ze:
            if ze.errno == errno.ENOENT:  # No such file or directory
                # TODO : handle all possible cases
                fpath = self._svc_address.split(':')[1]
                if fpath.startswith("//"): fpath = fpath[2:]
                try:
                    os.makedirs(os.path.dirname(fpath))
                except OSError as ose:
                    if ose.errno == errno.EEXIST and os.path.isdir(fpath):
                        pass
                    else:
                        raise
                # try again or break
                svc_socket.bind(self._svc_address, )
            else:
                raise

        except Exception as e:
            raise

        poller = zmq.Poller()
        poller.register(svc_socket, zmq.POLLIN)

        yield {'poller': poller, 'socket': svc_socket}

        zcontext.term()

    # Careful : this is NOT the same usage as "run()" from Process :
    # it is called inside a loop that it does not directly control...
    # TOOD : think about it and improve (Entity System integration ? Pool + Futures integration ?)
    def _update(self, poller, svc_socket, **kwargs):
        """
        Runs at every update cycle in the node process/thread.
        ######## Usually you want to override this method to extend the behavior of the node in your implementation #### still true ???
        :return: integer as exitcode to stop the node, or None to keep looping...
        """

        # blocking. messages are received ASAP. timeout only determine update/shutdown speed.
        socks = dict(poller.poll(timeout=100))
        if svc_socket in socks and socks[svc_socket] == zmq.POLLIN:
            req = None
            try:
                req_unparsed = svc_socket.recv()
                req = ServiceRequest_dictparse(req_unparsed)
                if isinstance(req, ServiceRequest):
                    if req.service and req.service in self._providers.keys():

                        request_args = pickle.loads(req.args) if req.args else ()
                        # add 'self' if providers[req.service] is a bound method.
                        if self._providers[req.service].self:
                            request_args = (self,) + request_args
                        request_kwargs = pickle.loads(req.kwargs) if req.kwargs else {}

                        resp = self._providers[req.service].func(*request_args, **request_kwargs)
                        svc_socket.send(ServiceResponse(
                            service=req.service,
                            response=pickle.dumps(resp),
                        ).serialize())

                    else:
                        raise UnknownServiceException("Unknown Service {0}".format(req.service))
                else:  # should not happen : dictparse would fail before reaching here...
                    raise UnknownRequestTypeException("Unknown Request Type {0}".format(type(req.request)))
            except Exception:  # we transmit back all errors, and keep spinning...
                exctype, excvalue, tb = sys.exc_info()
                # trying to make a pickleable traceback
                try:
                    ftb = Traceback(tb)
                except TypeError as exc:
                    ftb = "Traceback manipulation error: {exc}. Verify that python-tblib is installed.".format(exc=exc)

                # sending back that exception with traceback
                svc_socket.send(ServiceResponse(
                    service=req.service,
                    exception=ServiceException(
                        exc_type=pickle.dumps(exctype),
                        exc_value=pickle.dumps(excvalue),
                        traceback=pickle.dumps(ftb),
                    )
                ).serialize())

        return None  # we keep looping by default (need to deal with services here...)

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

        print('[{node}] Node available at [{address}]'.format(node=self.name, address=self._svc_address))

        # Initializing all context managers
        with self.user_required_context() as cm:  # user context first

            # setting up our event poller
            with self._zmq_poller_context() as zcm:

                # This will start looping and calling our target...
                exitstatus = super(Node, self).run(poller=zcm.get('poller'), svc_address=zcm.get('socket'))

        # all context managers are destroyed properly here

        logging.debug("[{self.name}] Node stopped.".format(**locals()))
        return exitstatus  # returning last exit status from the update function





