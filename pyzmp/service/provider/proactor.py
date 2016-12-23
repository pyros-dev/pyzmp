# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

# Proactor version of service provider.
# Here we are polling zmp directly.

import contextlib
import types

import six
import time
from collections import namedtuple
import zmq
import sys
import socket
import pickle
#import dill as pickle
import inspect

import logging

try:
    from six import reraise
except ImportError:  # if six is not present we will not reraise the remote exception
    reraise = None

try:
    from tblib import Traceback
except ImportError:  # if tblib is not present, we will not be able to forward the traceback
    Traceback = None

from pyzmp.message import ServiceRequest, ServiceResponse, ServiceResponse_dictparse, ServiceException, ServiceException_dictparse

from pyzmp.exceptions import UnknownServiceException, UnknownRequestTypeException
from pyzmp.message import ServiceRequest, ServiceRequest_dictparse, ServiceResponse, ServiceException
from pyzmp.master import manager
from pyzmp.exceptions import UnknownResponseTypeException
from pyzmp.exceptions import UnknownServiceException

# Lock is definitely needed ( not implemented in proxy objects, unless the object itself already has it, like Queue )
services_lock = manager.Lock()
services = manager.dict()


class Provider(object):

    EndPoint = namedtuple("EndPoint", "self func")

    def __init__(self, node_name, svc_address):
        self._svc_providers = {}
        self.node_name = node_name
        self.svc_address = svc_address

    def provides(self, svc_callback, inst=None, service_name=None):
        service_name = service_name or svc_callback.__name__
        inst = inst or svc_callback.__self__ if isinstance(svc_callback, types.MethodType) else None
        # we store an endpoint ( bound method or unbound function )
        self._svc_providers[service_name] = Provider.EndPoint(
            self=getattr(svc_callback, '__self__', inst),
            func=getattr(svc_callback, '__func__', svc_callback),
        )

    def withholds(self, service_name):
        service_name = getattr(service_name, '__name__', service_name)
        # we store an endpoint ( bound method or unbound function )
        self._svc_providers.pop(service_name)

    def dispatch_and_reply(self, req, svc_socket):
        if req.service and req.service in self._svc_providers.keys():

            request_args = pickle.loads(req.args) if req.args else ()
            # add 'instance' if providers[req.service] is a bound method.
            if self._svc_providers[req.service].self:
                request_args = (self._svc_providers[req.service].self,) + request_args
            request_kwargs = pickle.loads(req.kwargs) if req.kwargs else {}

            resp = self._svc_providers[req.service].func(*request_args, **request_kwargs)
            svc_socket.send(ServiceResponse(
                service=req.service,
                response=pickle.dumps(resp),
            ).serialize())

        else:
            raise UnknownServiceException("Unknown Service {0}".format(req.service))

    def activate(self):
        @contextlib.contextmanager
        def activate_cm():
            # advertising services
            services_lock.acquire()
            for svc_name, svc_endpoint in six.iteritems(self._svc_providers):
                # print('-> Providing {0} with {1}'.format(svc_name, svc_endpoint))
                # needs reassigning to propagate update to manager
                services[svc_name] = (services[svc_name] if svc_name in services else []) + [(self.node_name, self.svc_address)]
            services_lock.release()

            yield

            # concealing services
            services_lock.acquire()
            for svc_name, svc_endpoint in six.iteritems(self._svc_providers):
                # print('-> Unproviding {0}'.format(svc_name))
                services[svc_name] = [(n, a) for (n, a) in services[svc_name] if n != self.node_name]
            services_lock.release()
        return activate_cm()

    def eventloop_until(self, svc_address, exit, *args, **kwargs):
        zcontext = zmq.Context()  # check creating context in init ( compatibility with multiple processes )
        # Apparently not needed ? Ref : https://github.com/zeromq/pyzmq/issues/770
        zcontext.setsockopt(socket.SO_REUSEADDR, 1)  # required to make restart easy and avoid debugging traps...
        svc_socket = zcontext.socket(zmq.REP)  # Ref : http://api.zeromq.org/2-1:zmq-socket # TODO : ROUTER instead ?
        svc_socket.bind(svc_address, )

        poller = zmq.Poller()
        poller.register(svc_socket, zmq.POLLIN)

        # Initializing all context managers
        with self.activate() as cm:

            # Starting the clock
            start = time.time()

            first_loop = True
            # loop listening to connection
            while not exit.is_set():

                # blocking. messages are received ASAP. timeout only determine update/shutdown speed.
                socks = dict(poller.poll(timeout=100))
                if svc_socket in socks and socks[svc_socket] == zmq.POLLIN:
                    req = None
                    try:
                        req_unparsed = svc_socket.recv()
                        req = ServiceRequest_dictparse(req_unparsed)
                        if isinstance(req, ServiceRequest):
                            self.dispatch_and_reply(req=req, svc_socket=svc_socket)
                        else:  # should not happen : dictparse would fail before reaching here...
                            raise UnknownRequestTypeException("Unknown Request Type {0}".format(type(req.request)))
                    except Exception:  # we transmit back all errors, and keep spinning...
                        exctype, excvalue, tb = sys.exc_info()
                        # trying to make a pickleable traceback
                        try:
                            ftb = Traceback(tb)
                        except TypeError as exc:
                            ftb = "Traceback manipulation error: {exc}. Verify that python-tblib is installed.".format(
                                exc=exc)

                        # sending back that exception with traceback
                        svc_socket.send(ServiceResponse(
                            service=req.service,
                            exception=ServiceException(
                                exc_type=pickle.dumps(exctype),
                                exc_value=pickle.dumps(excvalue),
                                traceback=pickle.dumps(ftb),
                            )
                        ).serialize())

                # time is ticking
                # TODO : move this out of here. this class should require only generic interface to update method.
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
                    exitstatus = self._target(*args, **kwargs)

                if first_loop:
                    # signalling startup only at the end of the loop, only the first time
                    self.started.set()
                    first_loop = False

                if exitstatus is not None:
                    break

            if self.started.is_set() and exitstatus is None and self.exit.is_set():
                # in the not so special case where we started, we didnt get exit code and we exited,
                # this is expected as a normal result and we set an exitcode here of 0
                # As 0 is the conventional success for unix process successful run
                exitstatus = 0

        logging.debug("[{self.name}] Node stopped.".format(**locals()))
        return exitstatus  # returning last exit status from the update function

        # all context managers are destroyed properly here
