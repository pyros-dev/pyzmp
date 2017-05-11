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

import multiprocessing
import pyzmp.service.provider.proactor


def test_provide_activate():
    # test providing and activating and calling the service, in different sequence orders
    pass


# One fixture == One process strategy
# to test things as independently from each other as possible (we still fork from the same interpreter though...)
class TestProactor(object):
    def __init__(self, *args, **kwargs):
        provider = pyzmp.service.provider.proactor.Provider()
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
    multiprocessing.Process(target=client, args=(server_push_port,server_pub_port,)).start()