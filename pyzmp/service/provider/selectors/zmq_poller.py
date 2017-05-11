from __future__ import absolute_import, division, print_function

import zmq


# TODO : match api with asyncio selectors somehow...
# maybe use  https://github.com/zeromq/pyzmq/blob/master/zmq/asyncio/__init__.py

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
zmq_poller = zmq.Poller