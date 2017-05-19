from __future__ import absolute_import, division, print_function

import multiprocessing
import mmap
import uuid

import yaml
import collections
import dataset



# specialized nodes registry for now... enough.
# TODO : CRDT types...
class NodeRegistry():
    def __init__(self, id=None):
        self.id = id or uuid.uuid4()
        self.db = dataset.connect('sqlite://file:testf?mode=memory:'.format(self.id))

        self.nodes = self.db['nodes']

    def add(self, name, address):
        res= self.nodes.insert(dict(name=name, address=address))
        # we only return True or False. the (local) unique key is not useful for us.
        return res is not None

    def rem(self, name):
        res = self.nodes.delete(name=name)
        return res

    # TODO : "expect" to callback only when a matching name is found

    def get(self, name):
        res = self.nodes.find_one(name=name)
        return res

    def get_all(self):
        res = self.nodes.all()
        return res

    def freeze(self, filename):
        pass
        # TODO


