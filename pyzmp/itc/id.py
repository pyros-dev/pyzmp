from __future__ import absolute_import, division, print_function, unicode_literals

import collections
import copy

import logging
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler)

IdNodeTuple = collections.namedtuple("IdNodeTuple", "left right")
IdLeafTuple = collections.namedtuple("IdLeafTuple", "value")


class IDSumException(Exception):
    pass


# TODO : find better implementation (optimized for pypy)


class IdNode:
    __slots__ = ['left', 'right']

    def __init__(self, left, right):
        self.left = left
        self.right = right

    @property
    def isLeaf(self):
        return False

    def __getstate__(self):
        return IdNodeTuple(left=self.left, right=self.right)

    def __setstate__(self, state):
        # recursively rebuilding our hierarchy...
        self.left = copy.copy(state.left)
        self.right = copy.copy(state.right)

    def normalize(self):
        """normalize and Id field. applies only to IdNode and return an IdLeaf if possible"""
        # norm((0, 0)) = 0
        # norm((1, 1)) = 1
        # norm(i) = i
        if self.left.isLeaf and self.left.value == 0 and self.right.isLeaf and self.right.value == 0:
            return IdLeaf(0)
        elif self.left.isLeaf and self.left.value == 1 and self.right.isLeaf and self.right.value == 1:
            return IdLeaf(1)
        return self

    def __repr__(self):
        return "(" + repr(self.left) + ", " + repr(self.right) + ")"

    def __eq__(self, other):
        if other is None:
            return False
        return self.left == other.left and self.right == other.right

    def split(self):
        """
        Splitting the Id
        :return: tuple of two ids
        """
        if (self.left.isLeaf and self.left.value == 0) and (not self.right.isLeaf or self.right.value == 1):  # id = (0, i)
            ip = self.right.split()
            i1 = IdNode(IdLeaf(0), ip[0])
            i2 = IdNode(IdLeaf(0), ip[1])

        elif (not self.left.isLeaf or self.left.value == 1) and (self.right.isLeaf and self.right.value == 0):  # id = (i, 0)
            ip = self.left.split()
            i1 = IdNode(ip[0], IdLeaf(0))
            i2 = IdNode(ip[1], IdLeaf(0))

        elif (not self.left.isLeaf or self.left.value == 1) and (not self.right.isLeaf or self.right.value == 1):  # id = (i1, i2)
            i1 = IdNode(copy.copy(self.left), IdLeaf(0))
            i2 = IdNode(IdLeaf(0), copy.copy(self.right))

        res = IdNode(i1, i2)
        return res

    def __add__(self, other):
        if other.isLeaf and other.value == 0:
            pass
        elif not other.isLeaf:
            self.left = self.left + other.left
            self.right = self.right + other.right
            self.normalize()
        else:
            raise IDSumException(" i1: {i1.value} i2: {i2.value}".format(**locals()))

        return self


class IdLeaf:
    __slots__ = ['value']

    def __init__(self, val=1):
        self.value = val

    @property
    def isLeaf(self):
        return True

    def __getstate__(self):
        return IdLeafTuple(value=self.value)

    def __setstate__(self, state):
        self.value = state.value

    def split(self):
        """
        Splitting the Id
        :return: tuple of two ids
        """
        if self.value == 0:  # id = 0
            _logger.warning("ID == 0 ???!!!!?")
            i1 = IdLeaf(0)
            i2 = IdLeaf(0)
        elif self.value == 1:  # id = 1
            i1 = IdNode(IdLeaf(1), IdLeaf(0))
            i2 = IdNode(IdLeaf(0), IdLeaf(1))

        res = IdNode(i1, i2)
        return res

    def __add__(self, other):
        # sum(0, X) -> X;
        # sum(X, 0) -> X;
        # sum({L1,R1}, {L2, R2}) -> norm_id({sum(L1, L2), sum(R1, R2)}).

        if self.value == 0:
            return other
        elif other.isLeaf and other.value == 0:
            return self
        else:
            raise IDSumException(" i1: {i1.value} i2: {i2.value}".format(**locals()))

    def __repr__(self):
        return str(self.value)

    def __eq__(self, other):
        if other is None:
            return False
        try:
            return self.value == other.value
        except AttributeError:  # other doesnt have value attribute
            return False
