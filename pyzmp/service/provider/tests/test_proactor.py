# -*- coding: utf-8 -*-
from __future__ import absolute_import

# To allow python to run these tests as main script
import sys
import os

import time

import pytest
# http://pytest.org/latest/contents.html
# https://github.com/ionelmc/pytest-benchmark

# TODO : PYPY
# http://pypy.org/




def test_provide_activate():
    # test providing and activating and calling the service, in different sequence orders
    pass


# One fixture == One process strategy
# to test things as independently from each other as possible (we still fork from the same interpreter though...)
class TestProactor(UnitTest):
    def __init__(self, *args, **kwargs):
        provider = Provider()
        super(TestProactor, self).__init__(*args, **kwargs)

    def setup(self):
        pass

    def teardown(self):
        pass




if __name__ == "__main__":
    # Now we can run a few servers
    server_push_port = "5556"
    server_pub_port = "5558"
    Process(target=server_push, args=(server_push_port,)).start()
    Process(target=server_pub, args=(server_pub_port,)).start()
    Process(target=client, args=(server_push_port,server_pub_port,)).start()