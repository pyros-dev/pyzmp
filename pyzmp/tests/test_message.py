# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import pickle
import pyzmp.message

import pytest
# http://pytest.org/latest/contents.html
# https://github.com/ionelmc/pytest-benchmark

# TODO : PYPY
# http://pypy.org/

# Careful : we dont support all fancy methods of the protocol buffer.
# We restrict ourselves to the methods that we are using in pyzmp.


# Generic initialization tests
def initialize_servicerequest(req):
    assert req.service == "testservice"
    assert pickle.loads(req.args)[0] == "testarg"
    assert pickle.loads(req.kwargs)["testkwarg"] == "test"
    assert req.initialized()


def initialize_serviceresponse(resp):
    assert resp.service == "testservice"
    assert resp.has_field('response') == True
    assert resp.has_field('exception') == False
    assert pickle.loads(resp.response) == "testresponse"
    assert resp.initialized()


def initialize_serviceexception(resp):
    assert resp.exc_type == "testexception"
    assert pickle.loads(resp.exc_value) == "testexceptionvalue"
    assert pickle.loads(resp.traceback) == "testtraceback"
    assert resp.initialized()


def initialize_serviceresponseexception(resp):
    assert resp.service == "testservice"
    assert resp.has_field('response') == False
    assert resp.has_field('exception') == True
    assert resp.exception.exc_type == "testexception"
    assert pickle.loads(resp.exception.exc_value) == "testexceptionvalue"
    assert pickle.loads(resp.exception.traceback) == "testtraceback"
    assert resp.initialized()


def default_initialize_servicerequest(req):
    # Although default initialization behaviors are different in protobuf and namedtuple, both should be initialized
    assert req.initialized()


def default_initialize_serviceresponse(resp):
    # Although default initialization behaviors are different in protobuf and namedtuple, both should be initialized
    assert resp.initialized()


def default_initialize_serviceexception(resp):
    # Although default initialization behaviors are different in protobuf and namedtuple, both should be initialized
    assert resp.initialized()


# No point to have a default_initialize_serviceresponseexception here


# Symmetric Serialize / Parse tests
def oneline_symmetric_serialize_parse_servicerequest(req):
    assert req.initialized()
    # Testing oneline implementation that works for both tuples and protobuf
    finalreq = pyzmp.message.ServiceRequest_dictparse(req.serialize())
    assert isinstance(finalreq, pyzmp.message.ServiceRequest)
    assert finalreq.initialized()
    assert finalreq.service == "testservice"
    assert pickle.loads(finalreq.args)[0] == "testarg"
    assert pickle.loads(finalreq.kwargs)["testkwarg"] == "test"


def oneline_symmetric_serialize_parse_serviceresponse(resp):
    assert resp.initialized()
    # Testing oneline implementation that works for both tuples and protobuf
    finalresp = pyzmp.message.ServiceResponse_dictparse(resp.serialize())
    assert isinstance(finalresp, pyzmp.message.ServiceResponse)
    assert finalresp.initialized()
    assert finalresp.service == "testservice"
    assert finalresp.has_field('response') == True
    assert finalresp.has_field('exception') == False
    assert pickle.loads(finalresp.response) == "testresponse"


def oneline_symmetric_serialize_parse_serviceexception(resp):
    assert resp.initialized()
    # Testing oneline implementation that works for both tuples and protobuf
    finalresp = pyzmp.message.ServiceException_dictparse(resp.serialize())
    assert isinstance(finalresp, pyzmp.message.ServiceException)
    assert finalresp.initialized()
    assert finalresp.exc_type == "testexception"
    assert pickle.loads(finalresp.exc_value) == "testexceptionvalue"
    assert pickle.loads(finalresp.traceback) == "testtraceback"


def oneline_symmetric_serialize_parse_serviceresponseexception(resp):
    assert resp.initialized()
    # Testing oneline implementation that works for both tuples and protobuf
    finalresp = pyzmp.message.ServiceResponse_dictparse(resp.serialize())
    assert isinstance(finalresp, pyzmp.message.ServiceResponse)
    assert finalresp.initialized()
    assert finalresp.service == "testservice"
    assert finalresp.has_field('response') ==  False
    assert finalresp.has_field('exception') ==  True
    assert finalresp.exception.exc_type ==  "testexception"
    assert pickle.loads(finalresp.exception.exc_value) == "testexceptionvalue"
    assert pickle.loads(finalresp.exception.traceback) == "testtraceback"


if_protobuf = pytest.mark.skipif(not pyzmp.message.protobuf_implementation_enabled,
                    reason="Protobuf implementation not supported !")

# PROTOBUF Implementation test - default
class TestMessageProtobuf(object):
    def setup_method(self, method):
        # Checking protobuf implementation
        pass

    def teardown_method(self, method):
        # Setting back default implementation
        pass

    @if_protobuf
    def test_initialize_servicerequest_protobuf(self):
        # Test Initialization
        req = pyzmp.message.ServiceRequest(
            service="testservice",
            args=pickle.dumps(("testarg",)),
            kwargs=pickle.dumps({'testkwarg': 'test'}),
        )
        # Check we have desired implementation
        assert isinstance(req, pyzmp.message.ServiceRequestImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(req, pyzmp.message.ServiceRequest)
        # run actual test
        initialize_servicerequest(req)

    @if_protobuf
    def test_initialize_serviceresponse_protobuf(self):
        #Test Initialization
        resp = pyzmp.message.ServiceResponse(
            service="testservice",
            response=pickle.dumps("testresponse"),
        )
        # Check we have desired implementation
        assert isinstance(resp, pyzmp.message.ServiceResponseImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(resp, pyzmp.message.ServiceResponse)
        # run actual test
        initialize_serviceresponse(resp)

    @if_protobuf
    def test_initialize_serviceexception_protobuf(self):
        #Test Initialization
        resp = pyzmp.message.ServiceException(
            exc_type="testexception",
            exc_value=pickle.dumps("testexceptionvalue"),
            traceback=pickle.dumps("testtraceback"),
        )
        # Check we have desired implementation
        assert isinstance(resp, pyzmp.message.ServiceExceptionImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(resp, pyzmp.message.ServiceException)
        # run actual test
        initialize_serviceexception(resp)

    @if_protobuf
    def test_initialize_serviceresponseexception_protobuf(self):
        #Test Initialization
        resp = pyzmp.message.ServiceResponse(
            service="testservice",
            exception=pyzmp.message.ServiceException(
                exc_type="testexception",
                exc_value=pickle.dumps("testexceptionvalue"),
                traceback=pickle.dumps("testtraceback"),
            )
        )
        # Check we have desired implementation
        assert isinstance(resp, pyzmp.message.ServiceResponseImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(resp, pyzmp.message.ServiceResponse)
        # run actual test
        initialize_serviceresponseexception(resp)

    @if_protobuf
    def test_default_initialize_servicerequest_protobuf(self):
        # Test Initialization
        req = pyzmp.message.ServiceRequest()
        # Check we have desired implementation
        assert isinstance(req, pyzmp.message.ServiceRequestImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(req, pyzmp.message.ServiceRequest)
        # run actual test
        default_initialize_servicerequest(req)

    @if_protobuf
    def test_default_initialize_serviceresponse_protobuf(self):
        # Test Initialization
        resp = pyzmp.message.ServiceResponse()
        # Check we have desired implementation
        assert isinstance(resp, pyzmp.message.ServiceResponseImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(resp, pyzmp.message.ServiceResponse)
        # run actual test
        default_initialize_serviceresponse(resp)

    @if_protobuf
    def test_default_initialize_serviceexception_protobuf(self):
        # Test Initialization
        exc = pyzmp.message.ServiceException()
        # Check we have desired implementation
        assert isinstance(exc, pyzmp.message.ServiceExceptionImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(exc, pyzmp.message.ServiceException)
        # run actual test
        default_initialize_serviceexception(exc)


    # No point to have a test_default_initialize_serviceresponseexception_protobuf here

    @if_protobuf
    def test_symmetric_serialize_parse_servicerequest_protobuf(self):
        # Test Initialization
        req = pyzmp.message.ServiceRequest(
            service="testservice",
            args=pickle.dumps(("testarg",)),
            kwargs=pickle.dumps({'testkwarg': 'test'}),
        )
        # Check we have desired implementation
        assert isinstance(req, pyzmp.message.ServiceRequestImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(req, pyzmp.message.ServiceRequest)

        assert req.initialized()

        # assert parse modifies the current message
        parsedreq = pyzmp.message.ServiceRequest()
        parsedreq._parse(req.serialize())
        assert isinstance(parsedreq, pyzmp.message.ServiceRequest)
        assert parsedreq.initialized()
        assert parsedreq.service ==  "testservice"
        assert pickle.loads(parsedreq.args)[0] ==  "testarg"
        assert pickle.loads(parsedreq.kwargs)["testkwarg"] ==  "test"

        # assert parse returns the modified list
        parsedreq_oneline = pyzmp.message.ServiceRequest()._parse(req.serialize())
        assert isinstance(parsedreq_oneline, pyzmp.message.ServiceRequest)
        assert parsedreq_oneline.initialized()
        assert parsedreq_oneline.service ==  "testservice"
        assert pickle.loads(parsedreq_oneline.args)[0] ==  "testarg"
        assert pickle.loads(parsedreq_oneline.kwargs)["testkwarg"] ==  "test"

        # run actual tuple-compatible online test
        oneline_symmetric_serialize_parse_servicerequest(req)

    @if_protobuf
    def test_symmetric_serialize_parse_serviceresponse_protobuf(self):
        #Test Initialization
        resp = pyzmp.message.ServiceResponse(
            service="testservice",
            response=pickle.dumps("testresponse")
        )
        # Check we have desired implementation
        assert isinstance(resp, pyzmp.message.ServiceResponseImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(resp, pyzmp.message.ServiceResponse)

        assert resp.initialized()

        # assert parse modifies the current message
        parsedresp = pyzmp.message.ServiceResponse()
        parsedresp._parse(resp.serialize())
        assert isinstance(parsedresp, pyzmp.message.ServiceResponse)
        assert parsedresp.initialized()
        assert parsedresp.service ==  "testservice"
        assert pickle.loads(parsedresp.response) ==  "testresponse"

        # assert parse returns the modified list
        parsedresp_oneline = pyzmp.message.ServiceResponse()._parse(resp.serialize())
        assert isinstance(parsedresp_oneline, pyzmp.message.ServiceResponse)
        assert parsedresp_oneline.initialized()
        assert parsedresp_oneline.service ==  "testservice"
        assert pickle.loads(parsedresp_oneline.response) ==  "testresponse"

        # run actual tuple-compatible online test
        oneline_symmetric_serialize_parse_serviceresponse(resp)

    @if_protobuf
    def test_symmetric_serialize_parse_serviceexception_protobuf(self):
        #Test Initialization
        resp = pyzmp.message.ServiceException(
            exc_type="testexception",
            exc_value=pickle.dumps("testexceptionvalue"),
            traceback=pickle.dumps("testtraceback"),
        )
        # Check we have desired implementation
        assert isinstance(resp, pyzmp.message.ServiceExceptionImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(resp, pyzmp.message.ServiceException)

        assert resp.initialized()

        # assert parse modifies the current message
        parsedresp = pyzmp.message.ServiceException()
        parsedresp._parse(resp.serialize())
        assert isinstance(parsedresp, pyzmp.message.ServiceException)
        assert parsedresp.initialized()
        assert parsedresp.exc_type ==  "testexception"
        assert pickle.loads(parsedresp.exc_value) ==  "testexceptionvalue"
        assert pickle.loads(parsedresp.traceback) ==  "testtraceback"

        # assert parse returns the modified list
        parsedresp_oneline = pyzmp.message.ServiceException()._parse(resp.serialize())
        assert isinstance(parsedresp_oneline, pyzmp.message.ServiceException)
        assert parsedresp_oneline.initialized()
        assert parsedresp_oneline.exc_type ==  "testexception"
        assert pickle.loads(parsedresp_oneline.exc_value) ==  "testexceptionvalue"
        assert pickle.loads(parsedresp_oneline.traceback) ==  "testtraceback"

        # run actual tuple-compatible online test
        oneline_symmetric_serialize_parse_serviceexception(resp)

    @if_protobuf
    def test_symmetric_serialize_parse_serviceresponseexception_protobuf(self):
        #Test Initialization
        resp = pyzmp.message.ServiceResponse(
            service="testservice",
            exception=pyzmp.message.ServiceException(
                exc_type="testexception",
                exc_value=pickle.dumps("testexceptionvalue"),
                traceback=pickle.dumps("testtraceback"),
            )
        )
        # Check we have desired implementation
        assert isinstance(resp, pyzmp.message.ServiceResponseImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(resp, pyzmp.message.ServiceResponse)

        assert resp.initialized()

        # assert parse modifies the current message
        parsedresp = pyzmp.message.ServiceResponse()
        parsedresp._parse(resp.serialize())
        assert isinstance(parsedresp, pyzmp.message.ServiceResponse)
        assert parsedresp.initialized()
        assert parsedresp.service ==  "testservice"
        assert parsedresp.HasField('response') ==  False
        assert parsedresp.HasField('exception') ==  True
        assert parsedresp.exception.exc_type ==  "testexception"
        assert pickle.loads(parsedresp.exception.exc_value) ==  "testexceptionvalue"
        assert pickle.loads(parsedresp.exception.traceback) ==  "testtraceback"

        # assert parse returns the modified list
        parsedresp_oneline = pyzmp.message.ServiceResponse()._parse(resp.serialize())
        assert isinstance(parsedresp_oneline, pyzmp.message.ServiceResponse)
        assert parsedresp_oneline.initialized()
        assert parsedresp_oneline.service ==  "testservice"
        assert parsedresp_oneline.HasField('response') ==  False
        assert parsedresp_oneline.HasField('exception') ==  True
        assert parsedresp_oneline.exception.exc_type ==  "testexception"
        assert pickle.loads(parsedresp_oneline.exception.exc_value) ==  "testexceptionvalue"
        assert pickle.loads(parsedresp_oneline.exception.traceback) ==  "testtraceback"

        # run actual tuple-compatible online test
        oneline_symmetric_serialize_parse_serviceresponseexception(resp)


class TestMessageTupleFallback(object):
    def setup_method(self, method):
        # Forcing tuple implementation
        pyzmp.message.force_namedtuple_implementation()

    def teardown_method(self, method):
        # Setting back default implementation
        pyzmp.message.force_protobuf_implementation()

    def test_initialize_servicerequest_namedtuple(self):
        #Test Initialization
        req = pyzmp.message.ServiceRequest(
            service="testservice",
            args=pickle.dumps(("testarg",)),
            kwargs=pickle.dumps({'testkwarg': 'test'}),
        )
        # Check we have desired implementation
        assert isinstance(req, pyzmp.message.ServiceRequestNTImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(req, pyzmp.message.ServiceRequest)
        # run actual test
        initialize_servicerequest(req)

    def test_initialize_serviceresponse_namedtuple(self):
        #Test Initialization
        resp = pyzmp.message.ServiceResponse(
            service="testservice",
            response=pickle.dumps("testresponse"),
            exception=None,
        )
        # Check we have desired implementation
        assert isinstance(resp, pyzmp.message.ServiceResponseNTImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(resp, pyzmp.message.ServiceResponse)
        # run actual test
        initialize_serviceresponse(resp)

    def test_initialize_serviceexception_namedtuple(self):
        #Test Initialization
        resp = pyzmp.message.ServiceException(
            exc_type="testexception",
            exc_value=pickle.dumps("testexceptionvalue"),
            traceback=pickle.dumps("testtraceback"),
        )
        # Check we have desired implementation
        assert isinstance(resp, pyzmp.message.ServiceExceptionNTImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(resp, pyzmp.message.ServiceException)
        # run actual test
        initialize_serviceexception(resp)

    def test_initialize_serviceresponseexception_namedtuple(self):
        #Test Initialization
        resp = pyzmp.message.ServiceResponse(
            service="testservice",
            response=None,
            exception=pyzmp.message.ServiceException(
                exc_type="testexception",
                exc_value=pickle.dumps("testexceptionvalue"),
                traceback=pickle.dumps("testtraceback"),
            )
        )
        # Check we have desired implementation
        assert isinstance(resp, pyzmp.message.ServiceResponseNTImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(resp, pyzmp.message.ServiceResponse)
        # run actual test
        initialize_serviceresponseexception(resp)

    def test_default_initialize_servicerequest_namedtuple(self):
        # Test Initialization
        req = pyzmp.message.ServiceRequest()
        # Check we have desired implementation
        assert isinstance(req, pyzmp.message.ServiceRequestNTImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(req, pyzmp.message.ServiceRequest)
        # run actual test
        default_initialize_servicerequest(req)

    def test_default_initialize_serviceresponse_namedtuple(self):
        # Test Initialization
        resp = pyzmp.message.ServiceResponse()
        # Check we have desired implementation
        assert isinstance(resp, pyzmp.message.ServiceResponseNTImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(resp, pyzmp.message.ServiceResponse)
        # run actual test
        default_initialize_serviceresponse(resp)

    def test_default_initialize_serviceexception_namedtuple(self):
        # Test Initialization
        resp = pyzmp.message.ServiceException()
        # Check we have desired implementation
        assert isinstance(resp, pyzmp.message.ServiceExceptionNTImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(resp, pyzmp.message.ServiceException)
        # run actual test
        default_initialize_serviceexception(resp)

    def test_symmetric_serialize_parse_servicerequest_namedtuple(self):
        # Test Initialization
        req = pyzmp.message.ServiceRequest(
            service="testservice",
            args=pickle.dumps(("testarg",)),
            kwargs=pickle.dumps({'testkwarg': 'test'}),
        )
        # Check we have desired implementation
        assert isinstance(req, pyzmp.message.ServiceRequestNTImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(req, pyzmp.message.ServiceRequest)

        assert req.initialized()

        # run actual protobuf-compatible online test
        oneline_symmetric_serialize_parse_servicerequest(req)

    def test_symmetric_serialize_parse_serviceresponse_namedtuple(self):
        #Test Initialization
        resp = pyzmp.message.ServiceResponse(
            service="testservice",
            response=pickle.dumps("testresponse"),
            exception=None,
        )
        # Check we have desired implementation
        assert isinstance(resp, pyzmp.message.ServiceResponseNTImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(resp, pyzmp.message.ServiceResponse)

        assert resp.initialized()

        # run actual protobuf-compatible online test
        oneline_symmetric_serialize_parse_serviceresponse(resp)


    def test_symmetric_serialize_parse_serviceexception_namedtuple(self):
        #Test Initialization
        resp = pyzmp.message.ServiceException(
            exc_type="testexception",
            exc_value=pickle.dumps("testexceptionvalue"),
            traceback=pickle.dumps("testtraceback"),
        )
        # Check we have desired implementation
        assert isinstance(resp, pyzmp.message.ServiceExceptionNTImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(resp, pyzmp.message.ServiceException)

        assert resp.initialized()

        # run actual protobuf-compatible online test
        oneline_symmetric_serialize_parse_serviceexception(resp)

    def test_symmetric_serialize_parse_serviceresponseexception_namedtuple(self):
        #Test Initialization
        resp = pyzmp.message.ServiceResponse(
            service="testservice",
            response=None,
            exception=pyzmp.message.ServiceException(
                exc_type="testexception",
                exc_value=pickle.dumps("testexceptionvalue"),
                traceback=pickle.dumps("testtraceback"),
            ),
        )
        # Check we have desired implementation
        assert isinstance(resp, pyzmp.message.ServiceResponseNTImpl)
        # Check it is an instance of Dynamic Functional Facade
        assert isinstance(resp, pyzmp.message.ServiceResponse)

        assert resp.initialized()

        # run actual protobuf-compatible online test
        oneline_symmetric_serialize_parse_serviceresponseexception(resp)

