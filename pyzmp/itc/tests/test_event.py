from __future__ import absolute_import, division, print_function, unicode_literals

import copy

import pyzmp.itc.event as event

import pytest


def test_init():
    e = event.Event()
    assert e.value == 0
    assert e.left is None and e.right is None


def test_eq():
    """Test that the equality depends on the value tree"""
    e1 = event.Event()
    e2 = event.Event()

    e1.value = 42
    e2.value = 42

    assert e1 == e2

    e3 = event.Event()
    e2.left = e3

    assert e1 != e2

    e1.left = event.Event(31)
    e3.value = 31

    assert e1 == e2

def test_normalize():
    pytest.mark.skip("Not Implemented")

def test_join():
    pytest.mark.skip("Not Implemented")

def test_leq():
    pytest.mark.skip("Not Implemented")

