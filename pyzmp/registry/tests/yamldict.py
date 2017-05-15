from __future__ import absolute_import, division, print_function, unicode_literals

import uuid

import pytest

import pyzmp.registry.yamldict as yamldict


def UUID_filename_inverse():
    id = uuid.uuid4()
    fn = yamldict.UUID_filename(id)
    assert yamldict.filename_UUID(fn) == id






if '__name__' == '__main__':
    pytest.main(['-s', '-x', __file__])

