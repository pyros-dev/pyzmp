from __future__ import absolute_import, division, print_function, unicode_literals


import multiprocessing

"""
This is a node registry, same as DNS, but in a temporary file for our local processes.
We have one service registry for each unrelated python interpreter, but a node or service can be discovered in any registry 
The registry is created as soon as this module is imported.
"""

# Creating our UUID right now on import
import uuid
import tempfile
import yaml
import time

from .yamldict import yamldict, yamldict_tmp

registry_lock = multiprocessing.RLock()

registry_path= None

def ydict():
    if registry_path is None:
        yamldict_tmp(suffix=UUID, prefix='pyzmp')
    else:
        yamldict(registry_path)


def update_nodes(name, socket_addr, ad_period_secs=60, lifetime_factor=2):
    """
    
    """

    with yamldict()

    # find outdated nodes



    # protect against concurrent access
    with registry_lock:

        # remove outdated nodes


        # update registry with the new node
        registry.update({
            name: {
                'zmq_addr': socket_addr,
                'heartbeat': {
                    'period_secs': ad_period_secs,
                    'lifetime_factor': lifetime_factor,
                    'last_seen': time.time()
                }
            }
        })


def retrieve_foreign_nodes():



