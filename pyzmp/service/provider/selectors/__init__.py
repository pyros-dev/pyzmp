# This package contains different low level event handling systems.
# It is useful only for python < 3.5, before selectors abstracted all of it for asyncio.
# Reference : https://docs.python.org/3/library/selectors.html#module-selectors

# Note we do not care about ( 3.0 < python version < 3.5 ) since coroutines primitives were not implemented properly.

# TMP to make sure of what we are doing
# import sys
# if sys.version_info[0] >= 3 and sys.version_info[1] >= 5:
#     # if python version >= 3.5
#     # By default we use python standard selectors module
#     from selectors import *
#
#     from zmq.asyncio import Poller as zmq_poller
#
# else:
    # but if some specific selector is already setup, we should use this one instead
from .zmq import Poller as zmq_poller

