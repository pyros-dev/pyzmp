from __future__ import absolute_import
from __future__ import print_function

import contextlib
import os
import multiprocessing
import subprocess

# TODO : turn this into an actual pyzmp Node.
# It will also give us a way to encapsulate shell commands in a pyzmp node, which will be useful.

# TODO : mix all this with xonsh ?

# TODO :check psutil for alternative implementation


def watcher_proc(pid=None):
    """
    Simply encapsulate a shell call to pstree into python, the standard way.
    :param pid:
    :return:
    """
    # : this is a synchronous call that waits for completion
    return subprocess.check_call("xterm -e watch pstree -cap {0}".format(str(pid)), shell=True)


def process_watcher(pid=None, daemon=True):
    pid = pid or os.getpid()
    watchp = multiprocessing.Process(target=watcher_proc, name="node_watcher", args=(pid,))
    watchp.daemon = daemon  # make the process daemonic to guarantee it is terminated when parent terminates
    watchp.start()
    return watchp


@contextlib.contextmanager
def process_watcher_cm(pid=None, daemon=True):
    pid = pid or os.getpid()
    watchp = multiprocessing.Process(target=watcher_proc, name="node_watcher", args=(pid,))
    watchp.daemon = daemon  # make the process daemonic to guarantee it is terminated when parent terminates
    watchp.start()
    try:
        yield watchp
    finally:
        watchp.terminate()
