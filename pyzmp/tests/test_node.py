# -*- coding: utf-8 -*-
from __future__ import absolute_import

# To allow python to run these tests as main script
import functools
import multiprocessing
import sys
import os
import threading

import types
from random import randint

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import time
import pyzmp

import pytest
# http://pytest.org/latest/contents.html
# https://github.com/ionelmc/pytest-benchmark

# TODO : PYPY
# http://pypy.org/


# TODO :
# test that we can start a ode
# test that, afte the node started, services are immediately available
# test that, after a node stoped / terminated / crashed, services re not avialable







if __name__ == '__main__':
    import pytest
    pytest.main(['-s', '-x', __file__])
