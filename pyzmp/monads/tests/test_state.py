# --------------------------------------------------------
# (c) Copyright 2014 by Jason DeLaat.
# Licensed under BSD 3-clause licence.
# --------------------------------------------------------

import unittest
from pyzmp.monads.state import State
from pyzmp.monads.reader import Reader
from pyzmp.monads.tests.monad_tester import MonadTester
from pyzmp.monads.functor import unit


class TestStateFunctor(MonadTester):
    def testFunctorLaws(self):
        self.given_monad(unit(State, 8))
        self.ensure_first_functor_law_holds()
        self.ensure_second_functor_law_holds()


class TestStateApplicative(MonadTester):
    def __init__(self, x):
        super(TestStateApplicative, self).__init__(x)
        self.set_class_under_test(State)

    def testApplicativeLaws(self):
        self.given_monad(unit(State, 8))
        self.ensure_first_applicative_law_holds()
        self.ensure_second_applicative_law_holds()
        self.ensure_third_applicative_law_holds()
        self.ensure_fourth_applicative_law_holds()
        self.ensure_fifth_applicative_law_holds()


class TestStateMonad(MonadTester):
    def __init__(self, x):
        super(TestStateMonad, self).__init__(x)
        self.set_class_under_test(State)

    def monad_function_f(self, x):
        return State(lambda st: (x + 10, st + 1))

    def monad_function_g(self, x):
        return State(lambda st: (x * 5, st + 2))

    def testMonadLaws(self):
        self.given_monad(unit(State, 8))
        self.ensure_first_monad_law_holds()
        self.ensure_second_monad_law_holds()
        self.ensure_third_monad_law_holds()


class TestStateEquality(MonadTester):
    def testMonadComparisonExceptionWithTwoIdenticalStates(self):
        self.given_monads(unit(State, 8), unit(State, 8))
        self.ensure_comparison_raises_exception()

    def testMonadComparisonExceptionWithTwoDifferentStates(self):
        self.given_monads(unit(State, 8), unit(State, 9))
        self.ensure_comparison_raises_exception()

    def testMonadComparisonExceptionWithDifferentTypes(self):
        self.given_monads(unit(State, 8), Reader(8))
        self.ensure_comparison_raises_exception()


if __name__ == "__main__":
    unittest.main()

