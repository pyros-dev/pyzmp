from __future__ import absolute_import, division, print_function

from .container import Container


class Functor(Container):
    """
    Represents a type of values which can be "mapped over."
    Following design of https://github.com/fnl/pymonad/blob/master/pymonad/Functor.py
    """

    __slots__ = []  # we inherit value from Container, and keep a tiny object.

    def __init__(self, value):
        """ Stores 'value' as the contents of the Functor. """
        super(Functor, self).__init__(value)

    def __eq__(self, other):
        return self.value == other.value

    def fmap(self, function):
        """ Applies 'function' to the contents of the functor and returns a new functor value. """
        raise NotImplementedError("'fmap' not defined.")

    def __rlshift__(self, aFunction):
        """ 
        The 'fmap' operator.
        The following are equivalent:

            aFunctor.fmap(aFunction)
            aFunction << aFunctor

        """

        return self.fmap(aFunction)

    @classmethod
    def unit(cls, value):
        """ Returns an instance of the Functor with 'value' in a minimum context.  """
        raise NotImplementedError


def unit(cls, value):
    """ Calls the 'unit' method of 'cls' with 'value'.  """
    return cls.unit(value)
