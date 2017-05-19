# -*- coding: utf-8 -*-
from __future__ import absolute_import

# To allow python to run these tests as main script
import functools
import multiprocessing
import sys
import os
import threading

import time

import re

from pyzmp.registry import NodeRegistry
from pyzmp.process import Process


def test_registry_create():
    reg = NodeRegistry()

    # assert len(reg) == 0
    # assert str(reg) == "{}"


class TestRegistry(object):
    def setup_method(self):
        self.reg = NodeRegistry()

    def teardown_method(self):
        self.reg = None  # let the registry be garbage collected

    def test_insert(self):
        assert self.reg.add(name='testname', address='testaddr')
        #assert 'testname' in self.reg
        assert self.reg.get('testname').get('address') == 'testaddr'
        #assert len(self.reg) == 1
        #assert str(self.reg) == "{'testname': 'testaddr'}"

    def test_delete(self):
        assert self.reg.add(name='testname', address='testaddr')
        #assert 'testkey' in self.reg
        assert self.reg.get('testname').get('address') == 'testaddr'
        assert self.reg.rem('testname')
        #assert 'testkey' not in self.reg
        #assert len(self.reg) == 0
        #assert str(self.reg) == "{}"

        assert self.reg.get('testname') is None


class TestRegistryAcrossProcess(object):

    class TestProcess(Process):
        def target(self, reg):
            # TODO : find a way to report errors clearly
            assert reg.add('test_process', 'test_address')

    def setup_method(self):
        self.reg = NodeRegistry()

    def teardown_method(self):
        self.reg = None  # let the registry be garbage collected

    def test_registry(self):
        n1 = self.TestProcess(args=(self.reg,))  # passing registry as argument.
        assert not n1.is_alive()
        svc_url = n1.start()
        # update might not have been called yet
        assert n1.is_alive()
        assert svc_url

        # getting value from the registry
        # here we need a timeout to wait for the process to add the value to the register
        start = time.time()
        endtime = 5

        reg = re.compile('test_process')
        test_regval = None
        while True:
            timed_out = time.time() - start > endtime
            test_regval = self.reg.get('test_process')
            if test_regval or timed_out:
                break
            time.sleep(0.2)

        assert test_regval is not None
        # Note : By design process doesnt offer sync over registry, this is the job of Node (which depends on Registry)

        # starting and shutdown should at least guarantee ONE call of update function.

        exitcode = n1.shutdown()
        assert exitcode == 0  # TODO : shouldnt it be 42 ?
        assert not n1.is_alive()


if __name__ == '__main__':
    import pytest
    pytest.main(['-s', '-x', __file__])
