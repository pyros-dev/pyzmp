from __future__ import absolute_import, division, print_function

from .functor import Functor


class Applicative(Functor):
    """
    Represents a functor "context" which contains a function as a value rather than
    a type like integers, strings, etc.
    """

    __slots__ = []  # we inherit value from Container, and keep a tiny object.

    def __init__(self, fun):
        """ Stores `function` as the functors value. """
        super(Applicative, self).__init__(fun)

    def amap(self, functor_value):
        """
        Applies the function stored in the functor to the value inside `functor_value`
        returning a new functor value.
        """
        raise NotImplementedError

    def __and__(self, functor_value):
        """ The `amap` operator. """
        return self.amap(functor_value)
