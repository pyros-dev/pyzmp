from __future__ import absolute_import, division, print_function

"""
Continuation Monad
"""

from .monad import Monad, do, fid, done
from .util import compose, identity


class Continuation(Monad):

    def __init__(self, function_or_value):
        """
        The Continuation Monad.
        
        If `functionOrValue` is a function, it is stored directly.
        However, if it is a value -- 7 for example -- then a function taking a single argument
        which always returns that value is created and that function is stored as the Functor's
        value.
        
        The Continuation monad represents suspended computations in continuation-passing style (CPS)    
        """

        if callable(function_or_value):
            func = function_or_value
        else:
            func = lambda _: function_or_value

        super(Continuation, self).__init__(func)

    def bind(self, fun):
        r"""Chain continuation passing functions.
        Haskell: m >>= k = Cont $ \c -> runCont m $ \a -> runCont (k a) c
        """
        return Continuation(lambda cont: self(lambda x: fun(x).run(cont)))

    def fmap(self, fn):
        """Map a function over a continuation.
        Haskell: fmap f m = Cont $ \c -> runCont m (c . f)
        """
        return Continuation(lambda c: self(compose(c, fn)))

    def amap(self, functor_value):
        return Continuation(lambda c: functor_value(self(c)))

    def __call__(self, *args, **kwargs):
        return self.value(*args) if args else self.value

    def __eq__(self, other):
        return self(identity) == other(identity)

    def __str__(self):
        return "Cont " + str(self.getValue())

    @classmethod
    def unit(cls, val):
        return cls(lambda cont: cont(val))

    @staticmethod
    def mzero():
        return Continuation(lambda cont: None)


def call_cc(fn):
    r"""call-with-current-continuation.
    Haskell: callCC f = Cont $ \c -> runCont (f (\a -> Cont $ \_ -> c a )) c
    """
    return Continuation(lambda c: fn(lambda a: Continuation(lambda _: c(a))).run(c))

