from __future__ import absolute_import, division, print_function, unicode_literals

import collections
import copy

EventTuple = collections.namedtuple("EventTuple", "is_leaf left right")

class EventForkException(Exception):
    pass

class Event:
    """
    This class represent an event. Currently serialized with pickle algorithm by default.
    """
    __slots__ = ['value', 'left', 'right']

    def __init__(self, val = None):
        self.value = val or 0
        self.left = None
        self.right = None

    @property
    def isLeaf(self):
        return self.left == None and self.right == None

    def __getstate__(self):
        return EventTuple(value=self.value, left=self.left, right=self.right)

    def __setstate__(self, state):
        self.value = state.value
        # make sure we always do a deep copy and avoid problems
        self.left = copy.copy(state.left)
        self.right = copy.copy(state.right)

    @staticmethod
    def join(e1, e2):
        if not e1.isLeaf and not e2.isLeaf:
            if e1.value > e2.value:
                Event.join(e2, e1)
                e1 = e2
            else:
                d = e2.value - e1.value
                e2.left.lift(d)
                e2.right.lift(d)
                Event.join(e1.left, e2.left)
                Event.join(e1.right, e1.left)

        elif e1.isLeaf and not e2.isLeaf:
            e1.setAsNode()
            Event.join(e1, e2)
        elif e2.isLeaf and not e1.isLeaf:
            e2.setAsNode()
            Event.join(e1, e2)
        elif e1.isLeaf and e2.isLeaf:
            e1.value = max(e1.value, e2.value)
        else:
            raise EventForkException("Failed fork e1: {e1} e2: {e2}".format(**locals()))
        e1.normalize()


    def normalize(self):
        """Transform itself in the normal form"""
        if not self.isLeaf and self.left.isLeaf and self.right.isLeaf and self.left.value == self.right.value:
            self.value = self.value + self.left.value
            self.setAsLeaf()
        elif not self.isLeaf:
            mm = min(self.left.value, self.right.value)
            self.lift(mm)
            self.left.drop(mm)
            self.right.drop(mm)

    # TODO : rename this
    def lift(self, val):
        self.value = self.value+ val


    @staticmethod
    def lift(val, ev):
        res= ev.clone()
        res.value = res.value + val
        return res

    def drop(self, val):
        if val <= self. value:
            self. value = self.value - val

    def height(self):
        if not self.isLeaf:
            self.left.height()
            self.right.height()
            self.value += max(self.left.value, self.right.value)
            self.setAsLeaf()


    def leq(self, e2):
        if not self.isLeaf and not e2.isLeaf:
            if self. value > e2.value return False

            xl1 = Event.lift(self. value, self.left)
            xl2 = Event.lift(e2.value, e2.left)
            if not xl1.leq(xl2): return False

            xr1 = Event.lift(self.value, self.right)
            xr2 = Event.lift(e2.value, e2.right)
            if not xr1.leq(xr2): return False

            return True
        elif not self.isLeaf and e2.isLeaf:
            if self.value > e2.value: return False

            xl1 = Event.lift(self.value, self.left)
            if not xl1.leq(e2): return False

            xr1 = Event.lift(self.value, self.right)
            if not xr1.leq(e2): return False

        elif self.isLeaf and e2.isLeaf:
            return self.value <= e2.value

        elif self.isLeaf and not e2.isLeaf:

            if self.value < e2.value:
                return True
            ev = self.clone()
            ev.setAsNode()
            return ev.leq(e2)

        return False


    def setAsLeaf(self):
        self.left = None
        self.right = None

    def setAsNode(self):
        self.left = Event(0)
        self.right = Event(0)


    def __repr__(self):
        if self.isLeaf:
            return str(self.value)
        else:
            return "(" + self.value + ", "  + self.left + ", " + self.right + ")"

    def __eq__(self, other):
        if other is None:
            return False
        if self.isLeaf and other.isLeaf:
            return self.value == other.value
        elif not self.isLeaf and not other.isLeaf:
            return self.value == other.value and self.left == other.left and self.right == other.right
        return False


