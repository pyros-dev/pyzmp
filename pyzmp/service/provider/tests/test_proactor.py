# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

# To allow python to run these tests as main script
import sys
import os

import time

import pytest
# http://pytest.org/latest/contents.html
# https://github.com/ionelmc/pytest-benchmark

# TODO : PYPY
# http://pypy.org/

import random
import multiprocessing
import zmq
import pyzmp.service.provider.proactor
import pyzmp.proto.message


def fuzz():
    time.sleep(random.randint(0, 1000) / 1000.0)


def test_update_once():
    # test verifying that we can call update only once and get the exit status
    pass


def test_update_loop():
    # test verifying that we can call update in a loop
    pass


def test_provide_activate():
    # test providing and activating and calling the service, in different sequence orders

    def provider_test(name, address, started_evt, terminate_evt, port=None):
        # Note we do not provide the port, because we want the system to pick one for us (test usecase)
        provider = pyzmp.service.provider.proactor.Provider(name, address)

        def provided_svctest():
            return 42

        def unprovided_svctest():
            return 21

        def withheld_svctest():
            return 22

        provider.provides(svc_callback=withheld_svctest, service_name='withheld_svctest')
        provider.provides(svc_callback=provided_svctest, service_name='provided_svctest')

        provider.withholds(service_name='withheld_svctest')

        # Looping until terminate...
        try:
            provider.eventloop(started_evt=started_evt, terminate_evt=terminate_evt, assigned_port=port)
        except Exception as e:
            # CAREFUL : excepting here will block the test...
            raise e

    started_evt = multiprocessing.Event()
    terminate_evt = multiprocessing.Event()
    provider_port = multiprocessing.Value('I', 0)  # to dynamically retrieve the port after it has been atttributed by the system
    provider_proc = multiprocessing.Process(target=provider_test, args=('provider_test', 'tcp://127.0.0.1', started_evt, terminate_evt, provider_port))
    provider_proc.daemon = True  # to have it die when parent finishes, to avoid blocking tests, just in case.
    provider_proc.start()

    # with zmq.Context() as context: BLOCKING... BUG ?
    client_context = zmq.Context()
    socket = client_context.socket(zmq.REQ)

    started_evt.wait()

    # here the port should be set
    socket.connect('tcp://127.0.0.1:{0}'.format(provider_port))
    print("Client connected on : {0}".format('tcp://127.0.0.1.{0}'.format(provider_port)))

    # try calling each service
    provided_req = pyzmp.proto.message.ServiceRequest(service='provided_svctest', args=(), kwargs={})
    unprovided_req = pyzmp.proto.message.ServiceRequest(service='unprovided_svctest', args=(), kwargs={})
    withheld_req = pyzmp.proto.message.ServiceRequest(service='withheld_svctest', args=(), kwargs={})

    # Unprovided test
    print("req {0} => ".format(unprovided_req), end='')
    try:
        socket.send(unprovided_req.serialize())
    except Exception as e:
        # CAREFUL : excepting here will block the test (server is still waiting...)
        raise e
    resp = socket.recv()  # getting ( and ignoring ) response data
    assert resp == 42, resp
    print("resp {0}".format(resp))

    fuzz()

    # provided test
    print("req {0} => ".format(provided_req), end='')
    try:
        socket.send(provided_req.serialize())
    except Exception as e:
        # CAREFUL : excepting here will block the test (server is still waiting...)
        raise e
    resp = socket.recv()  # getting ( and ignoring ) response data
    assert resp == 21, resp
    print("resp {0}".format(resp))

    fuzz()

    # Withheld test
    print("req {0} => ".format(withheld_req), end='')
    try:
        socket.send(withheld_req.serialize())
    except Exception as e:
        # CAREFUL : excepting here will block the test (server is still waiting...)
        raise e
    resp = socket.recv()  # getting ( and ignoring ) response data
    assert resp == 21, resp
    print("resp {0}".format(resp))

    # lets terminate the eventloop...
    terminate_evt.set()

    # wait for it...
    provider_proc.join()

    # and we re done.




if __name__ == "__main__":
    pytest.main(['-s', '-x', __file__])
