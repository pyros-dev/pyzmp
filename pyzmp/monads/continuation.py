from __future__ import absolute_import, division, print_function

"""
Continuation Monad
"""

from .monad import Monad, do, fid, done


class Continuation(Monad):
    def __init__(self, run):
        self.run = run

    def __call__(self, cont=fid):
        return self.run(cont)

    def bind(self, bindee):
        return Continuation(lambda cont: self.run(lambda val: bindee(val).run(cont)))

    @classmethod
    def unit(cls, val):
        return cls(lambda cont: cont(val))

    @classmethod
    def zero(cls):
        return cls(lambda cont: None)


def callcc(usecc):
    return Continuation(lambda cont: usecc(lambda val: Continuation(lambda _: cont(val))).run(cont))
