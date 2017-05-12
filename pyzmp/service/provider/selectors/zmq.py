from __future__ import absolute_import, division, print_function

# TODO : match api with asyncio selectors somehow...
# maybe use  https://github.com/zeromq/pyzmq/blob/master/zmq/asyncio/__init__.py

import sys
if sys.version_info[0] >= 3 and sys.version_info[1] >= 5:
    # if python version >= 3.5
    # By default we use python standard selectors module
    from selectors import *

    from zmq.asyncio import *

else:
    from zmq import *