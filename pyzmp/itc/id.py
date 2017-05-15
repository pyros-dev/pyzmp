from __future__ import absolute_import, division, print_function, unicode_literals

import collections
import copy

import logging
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler)

EventTuple = collections.namedtuple("EventTuple", "is_leaf left right")

class IDSumException(Exception):
    pass



class Id:
    __slots__ = ['value', 'left', 'right']

    def __init__(self, val = None):
        self.value = val or 1
        self.left = None
        self.right = None

    @property
    def isLeaf(self):
        return self.left is None and self.right is None

    def __getstate__(self):
        return EventTuple(value=self.value, left=self.left, right=self.right)

    def __setstate__(self, state):
        self.value = state.value
        # recursively rebuilding our hierarchy...
        self.left = copy.copy(state.left)
        self.right = copy.copy(state.right)


    def split(self):
        i1 = Id()
        i2 = Id()

        if self.isLeaf and self.value == 0:  # id = 0
            _logger.warning("ID == 0 ???!!!!?")
            i1.setAsLeaf()
            i1.setValue(0)
            i2.setAsLeaf()
            i2.setValue(0)
        elif self.isLeaf and self.value == 1:  # id = 1
            i1.setAsNode()
            i1.setValue(0)
            i1.left = Id(1)
            i1.right = Id(0)

            i2.setAsNode()
            i2.setValue(0)
            i2.left = Id(0)
            i2.right = Id(1)
        else:
            if not self.isLeaf and (self.left.isLeaf and self.left.value == 0) and (not self.right.isLeaf or self.right.value == 1):  # id = (0, i)
                ip = self.right.split()

                i1.setAsNode()
                i1.value=0
                i1.left=Id(0)
                i1.right=ip[0]

                i2.setAsNode()
                i2.value=0
                i2.left=Id(0)
                i2.right=ip[1]
            elif not self.isLeaf and (not self.left.isLeaf or self.left.value == 1) and (self.right.isLeaf and self.right.value == 0):  # id = (i, 0)
                ip = self.left.split()

                i1.setAsNode()
                i1.value=0
                i1.left=ip[0]
                i1.right=Id(0)

                i2.setAsNode()
                i2.value=0
                i2.left=ip[1]
                i2.right=Id(0)

            elif not self.isLeaf and (not self.left.isLeaf or self.left.value == 1) and (not self.right.isLeaf and self.right.value == 1):  # id = (i1, i2)
                i1.setAsNode()
                i1.value = 0
                i1.left=self.left.clone()
                i1.right=Id(0)

                i2.setAsNode()
                i2.value=0
                i2.left=Id(0)
                i2.right(self.right.clone())

        res = (i1, i2)
        return res

    @staticmethod
    def sum(i1, i2):
        # sum(0, X) -> X;
		# sum(X, 0) -> X;
		# sum({L1,R1}, {L2, R2}) -> norm_id({sum(L1, L2), sum(R1, R2)}).

        if i1.isLeaf and i1.value == 0:
            i1.copy(i2)
        elif i2.isLeaf and i2.value == 0:
            # i1 is the result
            pass
        elif not i1.isLeaf and not i2.isLeaf:
            Id.sum(i1.left, i2.left)
            Id.sum(i1.right, i2.right)
            i1.normalize()
        else:
            raise IDSumException(" i1: {i1.value} i2: {i2.value}".format(**locals()))


    def normalize(self):
        if not self.isLeaf and self.left.isLeaf and self.left.value == 0 and self.right.isLeaf and self.right.value == 0:
            self.setAsLeaf()
            self.value = 0
            self.left = self.right = None
        elif not self.isLeaf and self.left.isLeaf and self.left.value == 1 and self.right.isLeaf and self.right.value == 1:
            self.setAsLeaf()
            self.value = 1
            self.left = self.right = None
        # else do nothing


	def setAsLeaf(self):
        self.left = None
        self.right = None

    def setAsNode(self):
        self.value = -1
        self.left = Id(1)
        self.right = Id(0)


    def __repr__(self):
        return str(self.value) if self.isLeaf else "(" + repr(self.left) + ", " + repr(self.right) + ")"

    def __eq__(self, other):
        if other is None:
            return False
        if self.isLeaf and other.isLeaf:
            return self.value == other.value
        if not self.isLeaf and not other.isLeaf:
            return self.left == other.left and self.right == other.right
        return False
