# -*- coding: utf-8 -*-
from __future__ import absolute_import

# To allow python to run these tests as main script
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import time
import multiprocessing
import pyzmp
import inspect

import pytest
# http://pytest.org/latest/contents.html
# https://github.com/ionelmc/pytest-benchmark

# TODO : PYPY
# http://pypy.org/


# IPC protocol
# Node as fixture to guarantee cleanup
# Better to have IPC as main class as it is simpler and easier to test than Socket.
class TestMockHWNodeIPC(object):
    __test__ = True

    class HWNode(pyzmp.Node):
        def __init__(self, name):
            super(TestMockHWNodeIPC.HWNode, self).__init__(name)
            self.magic_number = 666
            # TODO : improvement : autodetect class own methods
            # TODO : assert static ?
            self.provides(self.helloworld)
            self.provides(self.breakworld)
            self.provides(self.add)
            self.provides(self.getlucky)

        @staticmethod  # TODO : verify : is it true that a service is always a static method ( execution does not depend on instance <=> process local data ) ?
        def helloworld(msg):
            return "Hello! I am " + pyzmp.current_node().name if msg == "Hello" else "..."

        @staticmethod
        def breakworld(msg):
            raise Exception("Excepting Not Exceptionnally")

        @staticmethod
        def add(a, b):
            return a+b

        def getlucky(self):
            return self.magic_number

    def setup_method(self, method):
        # services is already setup globally
        self.hwnode = TestMockHWNodeIPC.HWNode(name="HNode")
        self.hwnodeextra = TestMockHWNodeIPC.HWNode(name="HNodeExtra")

    def teardown_method(self, method):
        if self.hwnode.is_alive():
            self.hwnode.shutdown(join=True)
        if self.hwnodeextra.is_alive():
            self.hwnodeextra.shutdown(join=True)
        # if it s still alive terminate it.
        if self.hwnode.is_alive():
            self.hwnode.terminate()
        if self.hwnodeextra.is_alive():
            self.hwnodeextra.terminate()

    # @nose.SkipTest  # to help debugging ( FIXME : how to programmatically start only one test - maybe in fixture - ? )
    def test_service_discover(self):
        print("\n" + inspect.currentframe().f_code.co_name)
        assert not self.hwnode.is_alive()

        print("Discovering helloworld Service...")
        helloworld = pyzmp.discover("helloworld")
        assert helloworld is None  # service not provided until node starts

        self.hwnode.start()
        assert self.hwnode.is_alive()

        print("Discovering helloworld Service...")
        helloworld = pyzmp.discover("helloworld", 5)  # we wait a bit to let it time to start
        assert not helloworld is None
        assert len(helloworld.providers) ==  1

        self.hwnode.shutdown()
        assert not self.hwnode.is_alive()

        print("Discovering helloworld Service...")
        helloworld = pyzmp.discover("helloworld")
        assert helloworld is None

    # @nose.SkipTest  # to help debugging ( FIXME : how to programmatically start only one test - maybe in fixture - ? )
    def test_service_discover_timeout(self):
        print("\n" + inspect.currentframe().f_code.co_name)
        assert not self.hwnode.is_alive()

        print("Discovering helloworld Service...")
        helloworld = pyzmp.discover("helloworld")
        assert helloworld is None  # service not provided until node starts

        print("Discovering helloworld Service...")
        helloworld = pyzmp.discover("helloworld", 1)  # check timeout actually times out
        assert helloworld is None

        print("Discovering helloworld Service...")
        helloworld = pyzmp.discover("helloworld", 1, 2)
        assert helloworld is None

    # @nose.SkipTest  # to help debugging ( FIXME : how to programmatically start only one test - maybe in fixture - ? )
    def test_service_discover_multiple_stack(self):
        print("\n" + inspect.currentframe().f_code.co_name)
        assert not self.hwnode.is_alive()

        print( "Discovering helloworld Service...")
        helloworld = pyzmp.discover("helloworld")
        assert helloworld is None  # service not provided until node starts

        # Start two nodes - stack process
        self.hwnodeextra.start()
        assert self.hwnodeextra.is_alive()

        print("Discovering helloworld Service...")
        helloworld = pyzmp.discover("helloworld", 5)  # we wait a bit to let it time to start
        assert not helloworld is None
        assert len(helloworld.providers) ==  1

        self.hwnode.start()
        assert self.hwnode.is_alive()

        print("Discovering helloworld Service...")
        helloworld = pyzmp.discover("helloworld", 5, 2)  # we wait until we get 2 providers ( or timeout )
        assert not helloworld is None
        assert len(helloworld.providers) ==  2

        self.hwnode.shutdown()
        assert not self.hwnode.is_alive()

        print("Discovering helloworld Service...")
        helloworld = pyzmp.discover("helloworld")  # we should have right away 1 provider only
        assert not helloworld is None
        assert len(helloworld.providers) ==  1

        self.hwnodeextra.shutdown()
        assert not self.hwnodeextra.is_alive()

    # @nose.SkipTest  # to help debugging ( FIXME : how to programmatically start only one test - maybe in fixture - ? )
    def test_service_discover_multiple_queue(self):
        print("\n" + inspect.currentframe().f_code.co_name)
        assert not self.hwnode.is_alive()

        print("Discovering helloworld Service...")
        helloworld = pyzmp.discover("helloworld")
        assert helloworld is None  # service not provided until node starts

        # Start two nodes queue process
        self.hwnodeextra.start()
        assert self.hwnodeextra.is_alive()

        print("Discovering helloworld Service...")
        helloworld = pyzmp.discover("helloworld", 5)  # we wait a bit to let it time to start
        assert not helloworld is None
        assert len(helloworld.providers) ==  1

        self.hwnode.start()
        assert self.hwnode.is_alive()

        print("Discovering helloworld Service...")
        helloworld = pyzmp.discover("helloworld", 5, 2)   # we wait until we get 2 providers ( or timeout )
        assert not helloworld is None
        assert len(helloworld.providers) ==  2

        self.hwnodeextra.shutdown()
        assert not self.hwnodeextra.is_alive()

        print("Discovering helloworld Service...")
        helloworld = pyzmp.discover("helloworld", 5)  # we wait a bit to let it time to start
        assert not helloworld is None
        assert len(helloworld.providers) ==  1

        self.hwnode.shutdown()
        assert not self.hwnode.is_alive()

    # @nose.SkipTest  # to help debugging ( FIXME : how to programmatically start only one test - maybe in fixture - ? )
    def test_service_comm_to_sub(self):

        print("\n" + inspect.currentframe().f_code.co_name)
        assert not self.hwnode.is_alive()
        self.hwnode.start()
        assert self.hwnode.is_alive()

        print("Discovering helloworld Service...")
        helloworld = pyzmp.discover("helloworld", 5)
        assert helloworld is not None  # to make sure we get a service provided
        resp = helloworld.call(args=("Hello",))
        print("Hello -> {0}".format(resp))
        assert resp == "Hello! I am HNode"
        resp = helloworld.call(args=("Hallo",))
        print("Hallo -> {0}".format(resp))
        assert resp == "..."

        self.hwnode.shutdown()
        assert not self.hwnode.is_alive()

    # @nose.SkipTest  # to help debugging ( FIXME : how to programmatically start only one test - maybe in fixture - ? )
    def test_service_comm_to_double_sub(self):
        print("\n" + inspect.currentframe().f_code.co_name)

        assert not self.hwnode.is_alive()
        self.hwnode.start()
        assert self.hwnode.is_alive()

        assert not self.hwnodeextra.is_alive()
        self.hwnodeextra.start()
        assert self.hwnodeextra.is_alive()

        print("Discovering helloworld Service...")
        helloworld = pyzmp.discover("helloworld", 5, 2)  # make sure we get both providers. we need them.
        assert helloworld is not None  # to make sure we get a service provided
        assert len(helloworld.providers) ==  2
        resp = helloworld.call(args=("Hello",))
        print("Hello -> {0}".format(resp))
        assert resp == "Hello! I am HNode" or resp == "Hello! I am HNodeExtra"
        resp = helloworld.call(args=("Hallo",))
        print("Hallo -> {0}".format(resp))
        assert resp == "..."

        resp = helloworld.call(args=("Hello",), node=self.hwnode.name)
        print("Hello -HNode-> {0}".format(resp))
        assert resp == "Hello! I am HNode"
        resp = helloworld.call(args=("Hello",), node=self.hwnodeextra.name)
        print("Hello -HNodeExtra-> {0}".format(resp))
        assert resp == "Hello! I am HNodeExtra"

        self.hwnode.shutdown()
        assert not self.hwnode.is_alive()
        self.hwnodeextra.shutdown()
        assert not self.hwnodeextra.is_alive()

    # @nose.SkipTest  # to help debugging ( FIXME : how to programmatically start only one test - maybe in fixture - ? )
    def test_service_double_comm_to_sub(self):

        print("\n" + inspect.currentframe().f_code.co_name)
        assert not self.hwnode.is_alive()
        self.hwnode.start()
        assert self.hwnode.is_alive()

        print("Discovering helloworld Service...")
        helloworld = pyzmp.discover("helloworld", 5)
        assert helloworld is not None  # to make sure we get a service provided

        def callit():
            hw = pyzmp.discover("helloworld", 5)
            return hw.call(args=("Hello",))

        c = multiprocessing.Process(name="Client", target=callit)
        assert not c.is_alive()
        c.start()
        assert c.is_alive()

        resp = helloworld.call(args=("Hello",))
        print("Hallo -> {0}".format(resp))
        assert resp == "Hello! I am HNode"
        resp = helloworld.call(args=("Hallo",))
        print("Hallo -> {0}".format(resp))
        assert resp == "..."
        resp = helloworld.call(args=("Hello",), node=self.hwnode.name)
        print("Hello -HNode-> {0}".format(resp))
        assert resp == "Hello! I am HNode"

        c.join()
        assert not c.is_alive()

        self.hwnode.shutdown()
        assert not self.hwnode.is_alive()

    # @nose.SkipTest  # to help debugging ( FIXME : how to programmatically start only one test - maybe in fixture - ? )
    def test_service_comm_to_sub_self(self):

        print("\n" + inspect.currentframe().f_code.co_name)
        assert not self.hwnode.is_alive()
        self.hwnode.magic_number = 42
        self.hwnode.start()
        assert self.hwnode.is_alive()

        print("Discovering getlucky Service...")
        getlucky = pyzmp.discover("getlucky", 5)
        assert getlucky is not None  # to make sure we get a service provided
        resp = getlucky.call()
        print("42 ? -> {0}".format(resp))
        assert resp == 42

        self.hwnode.shutdown()
        assert not self.hwnode.is_alive()

    # @nose.SkipTest  # to help debugging ( FIXME : how to programmatically start only one test - maybe in fixture - ? )
    def test_service_comm_to_double_sub_self(self):
        print("\n" + inspect.currentframe().f_code.co_name)

        assert not self.hwnode.is_alive()
        self.hwnode.magic_number = 42
        self.hwnode.start()
        assert self.hwnode.is_alive()

        assert not self.hwnodeextra.is_alive()
        self.hwnodeextra.magic_number = 79
        self.hwnodeextra.start()
        assert self.hwnodeextra.is_alive()

        print("Discovering getlucky Service...")
        getlucky = pyzmp.discover("getlucky", 5, 2)  # make sure we get both providers. we need them.
        assert getlucky is not None  # to make sure we get a service provided
        assert len(getlucky.providers) ==  2
        resp = getlucky.call()
        print("42 || 79 ? -> {0}".format(resp))
        assert resp == 42 or resp == 79

        resp = getlucky.call(node=self.hwnode.name)
        print("42 ? -HNode-> {0}".format(resp))
        assert resp == 42
        resp = getlucky.call(node=self.hwnodeextra.name)
        print("79 ? -HNodeExtra-> {0}".format(resp))
        assert resp == 79

        self.hwnode.shutdown()
        assert not self.hwnode.is_alive()
        self.hwnodeextra.shutdown()
        assert not self.hwnodeextra.is_alive()

    # @nose.SkipTest  # to help debugging ( FIXME : how to programmatically start only one test - maybe in fixture - ? )
    def test_service_double_comm_to_sub_self(self):

        print("\n" + inspect.currentframe().f_code.co_name)
        assert not self.hwnode.is_alive()
        self.hwnode.magic_number = 42
        self.hwnode.start()
        assert self.hwnode.is_alive()

        print("Discovering getlucky Service...")
        getlucky = pyzmp.discover("getlucky", 5)
        assert getlucky is not None  # to make sure we get a service provided

        def callit():
            getlucky = pyzmp.discover("getlucky", 5)
            return getlucky.call()

        c = multiprocessing.Process(name="Client", target=callit)
        assert not c.is_alive()
        c.start()
        assert c.is_alive()

        resp = getlucky.call()
        print("42 ? -> {0}".format(resp))
        assert resp == 42
        resp = getlucky.call(node=self.hwnode.name)
        print("42 ? -HNode-> {0}".format(resp))
        assert resp == 42

        c.join()
        assert not c.is_alive()

        self.hwnode.shutdown()
        assert not self.hwnode.is_alive()



    # @nose.SkipTest  # to help debugging ( FIXME : how to programmatically start only one test - maybe in fixture - ? )
    def test_service_except_from_sub(self):

        print("\n" + inspect.currentframe().f_code.co_name)
        assert not self.hwnode.is_alive()
        self.hwnode.start()
        assert self.hwnode.is_alive()

        print("Discovering breakworld Service...")
        breakworld = pyzmp.discover("breakworld", 5)
        assert breakworld is not None  # to make sure we get a service provided
        with pytest.raises(Exception) as cm:
            resp = breakworld.call(args=("Hello",))

        self.hwnode.shutdown()
        assert not self.hwnode.is_alive()

    # @nose.SkipTest  # to help debugging ( FIXME : how to programmatically start only one test - maybe in fixture - ? )
    def test_service_except_from_node_no_service(self):

        print("\n" + inspect.currentframe().f_code.co_name)
        assert not self.hwnode.is_alive()
        self.hwnode.start()
        assert self.hwnode.is_alive()

        print("Discovering breakworld Service...")
        breakworld = pyzmp.discover("breakworld", 5)
        assert breakworld is not None  # to make sure we get a service provided

        # messing around even if we should not
        breakworld.name = "NOT_EXISTING"

        with pytest.raises(pyzmp.UnknownServiceException) as cm:
            resp = breakworld.call(args=("Hello",))

        self.hwnode.shutdown()
        assert not self.hwnode.is_alive()

    # TODO : check mo exception cases

    # @nose.SkipTest  # to help debugging ( FIXME : how to programmatically start only one test - maybe in fixture - ? )
    def test_service_params_comm_to_sub(self):

        print("\n" + inspect.currentframe().f_code.co_name)
        assert not self.hwnode.is_alive()
        self.hwnode.start()
        assert self.hwnode.is_alive()

        print("Discovering add Service...")
        add = pyzmp.discover("add", 5)
        assert add is not None  # to make sure we get a service provided

        resp = add.call(args=(17, 25))
        print(" 17 + 25 -> {0}".format(resp))
        assert resp == 17+25

        self.hwnode.shutdown()
        assert not self.hwnode.is_alive()


# Node as fixture to guarantee cleanup
# TCP protocol
class TestMockHWNodeSocket(TestMockHWNodeIPC):
    __test__ = True

    class HWNode(pyzmp.Node):
        def __init__(self, name, socket_bind):
            super(TestMockHWNodeSocket.HWNode, self).__init__(name, socket_bind)
            self.magic_number = 999
            # TODO : improvement : autodetect class own methods
            # TODO : assert static ?
            self.provides(self.helloworld)
            self.provides(self.breakworld)
            self.provides(self.add)
            self.provides(self.getlucky)

        @staticmethod  # TODO : verify : is it true that a service is always a static method ( execution does not depend on instance <=> process local data ) ?
        def helloworld(msg):
            return "Hello! I am " + pyzmp.current_node().name if msg == "Hello" else "..."

        @staticmethod
        def breakworld(msg):
            raise Exception("Excepting Not Exceptionnally")

        @staticmethod
        def add(a, b):
            return a+b

        def getlucky(self):
            return self.magic_number

    def setup_method(self, method):
        # services is already setup globally
        self.hwnode = TestMockHWNodeSocket.HWNode(name="HNode", socket_bind="tcp://127.0.0.1:4242")
        self.hwnodeextra = TestMockHWNodeSocket.HWNode(name="HNodeExtra", socket_bind="tcp://127.0.0.1:4243")

    def teardown_method(self, method):
        if self.hwnode.is_alive():
            self.hwnode.shutdown(join=True)
        if self.hwnodeextra.is_alive():
            self.hwnodeextra.shutdown(join=True)
        # if it s still alive terminate it.
        if self.hwnode.is_alive():
            self.hwnode.terminate()
        if self.hwnodeextra.is_alive():
            self.hwnodeextra.terminate()

    #TODO : verify all tests are run again with proper fixture


