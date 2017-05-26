from __future__ import absolute_import, division, print_function

"""
StateChanger Monad
"""

from .monad import Monad, do, mreturn, fid


class StateChanger(Monad):
    def __init__(self, run):
        self.run = run

    def bind(self, bindee):
        run0 = self.run

        def run1(state0):
            (result, state1) = run0(state0)
            return bindee(result).run(state1)

        return StateChanger(run1)

    @classmethod
    def unit(cls, val):
        return cls(lambda state: (val, state))


def get_state(view=fid):
    return change_state(fid, view)


def change_state(changer, view=fid):
    def make_new_state(old_state):
        new_state = changer(old_state)
        viewed_state = view(old_state)
        return (viewed_state, new_state)

    return StateChanger(make_new_state)

