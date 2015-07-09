from __future__ import absolute_import

from .rostful_mock import RostfulMock
from .rostful_client import RostfulClient

try:
    import rospy
    from .rostful_node import RostfulNode
except:
    rospy = None

import logging

from multiprocessing import Pipe
from collections import namedtuple
from contextlib import contextmanager

# A context manager to handle rospy init and shutdown properly.
# It also creates a pipe and pass it to a node and a client.
# So stable interprocess communication can happen via the pipe
@contextmanager
#TODO : think about passing ros arguments http://wiki.ros.org/Remapping%20Arguments
def RostfulCtx(name='rostful_node', argv=None, anonymous=True, disable_signals=True):
    if rospy:
        #we initialize the node here, passing ros parameters.
        #disabling signal to avoid overriding callers behavior
        rospy.init_node(name, argv=argv, anonymous=anonymous, disable_signals=disable_signals)
        rospy.logwarn('rostful node started with args : %r', argv)

        # TODO : check about synchronization to avoid concurrency on pip write/read ( in case of multiple clients for example )
        node_conn, client_conn = Pipe()
        ctx = namedtuple("rostful_context", "node client")
        yield ctx(node=RostfulNode(node_conn), client=RostfulClient(client_conn))
    else:
        logging.warn('rostful mock node started with args : %r', argv)

        # no ROS installed : pure python mock.
        node_conn, client_conn = Pipe()
        ctx = namedtuple("rostful_context", "node client")
        yield ctx(node=RostfulMock(node_conn), client=RostfulClient(client_conn))

    if rospy:
        rospy.logwarn('rostful node stopped')
        rospy.signal_shutdown('Closing')
    else:
        logging.warn('rostful mock node stopped')

