from __future__ import absolute_import, division, print_function

import pyzmp.monads as monads
#from pymonad import Maybe, Just, Nothing, curry
import pytest


# def test_failable_monad_():
#     @curry
#     def fdiv(a, b):
#         return a / b
#
#     # @monads.do(monads.Failable)
#     # def with_failable(first_divisor):
#     #     val1 = yield fdiv(2.0, first_divisor)
#     #     val2 = yield fdiv(3.0, 1.0)
#     #     val3 = yield fdiv(val1, val2)
#     #     monads.mreturn(val3)
#
#     def with_maybe(first_divisor):
#         val1 = fdiv * Just(2.0) & first_divisor
#         val2 = fdiv * Just(3.0) & Just(1.0)
#         val3 = fdiv * Just(val1) & Just(val2)
#
#         monads.mreturn(val3)
#
#
#     assert with_maybe(0.0) == Nothing()
#     assert with_maybe(1.0) == Just(0.66666666666666)



import unittest
from pyzmp.monads.maybe import Maybe, Just, First, Last, _Nothing, Nothing
from pyzmp.monads.reader import Reader
from pyzmp.monads.tests.monad_tester import MonadTester
from pyzmp.monads.tests.monoid_tester import MonoidTester


class TestJustFunctor(MonadTester):
    def __init__(self, x):
        super(TestJustFunctor, self).__init__(x)
        self.set_class_under_test(Just)

    def testFunctorLaws(self):
        self.given(8)
        self.ensure_first_functor_law_holds()
        self.ensure_second_functor_law_holds()


class TestNothingFunctor(MonadTester):
    def __init__(self, x):
        super(TestNothingFunctor, self).__init__(x)
        self.set_class_under_test(_Nothing)

    def testFunctorLaws(self):
        self.given(None)
        self.ensure_first_functor_law_holds()
        self.ensure_second_functor_law_holds()


class TestJustApplicative(MonadTester):
    def __init__(self, x):
        super(TestJustApplicative, self).__init__(x)
        self.set_class_under_test(Just)

    def testApplicativeLaws(self):
        self.given(8)
        self.ensure_first_applicative_law_holds()
        self.ensure_second_applicative_law_holds()
        self.ensure_third_applicative_law_holds()
        self.ensure_fourth_applicative_law_holds()
        self.ensure_fifth_applicative_law_holds()


class TestNothingApplicative(MonadTester):
    def __init__(self, x):
        super(TestNothingApplicative, self).__init__(x)
        self.set_class_under_test(_Nothing)

    def testApplicativeLaws(self):
        self.given(None)
        self.ensure_first_applicative_law_holds()
        self.ensure_second_applicative_law_holds()
        self.ensure_third_applicative_law_holds()
        self.ensure_fourth_applicative_law_holds()
        self.ensure_fifth_applicative_law_holds()


class TestJustMonad(MonadTester):
    def __init__(self, x):
        super(TestJustMonad, self).__init__(x)
        self.set_class_under_test(Just)

    def monad_function_f(self, x):
        return Just(x + 10)

    def monad_function_g(self, x):
        return Just(x * 5)

    def testMonadLaws(self):
        self.given(8)
        self.ensure_first_monad_law_holds()
        self.ensure_second_monad_law_holds()
        self.ensure_third_monad_law_holds()


class TestNothingMonad(MonadTester):
    def __init__(self, x):
        super(TestNothingMonad, self).__init__(x)
        self.set_class_under_test(_Nothing)

    def monad_function_f(self, x):
        return Just(x + 10)

    def monad_function_g(self, x):
        return Just(x * 5)

    def testMonadLaws(self):
        self.given(None)
        self.ensure_first_monad_law_holds()
        self.ensure_second_monad_law_holds()
        self.ensure_third_monad_law_holds()


class TestMaybeEquality(MonadTester):
    def testEqualityOfIdenticalTypes(self):
        self.given_monads(Just(8), Just(8))
        self.ensure_monads_are_equal()

    def testInequalityOfIdenticalTypes(self):
        self.given_monads(Just(8), Just(9))
        self.ensure_monads_are_not_equal()

    def testInequalityOfJustAndNothing(self):
        self.given_monads(Just(8), Nothing)
        self.ensure_monads_are_not_equal()

    def testMonadComparisonExceptionWithJust(self):
        self.given_monads(Just(8), Reader(8))
        self.ensure_comparison_raises_exception()

    def testMonadComparisonExceptionWithNothing(self):
        self.given_monads(Nothing, Reader(8))
        self.ensure_comparison_raises_exception()


class TestMaybeMonoid(MonoidTester):
    def test_mzero(self):
        self.given_monoid(Maybe)
        self.get_mzero()
        self.ensure_mzero_is(Nothing)

    def test_right_identity(self):
        self.given_monoid(Just(9))
        self.ensure_monoid_plus_zero_equals(Just(9))

    def test_left_identity(self):
        self.given_monoid(Just(9))
        self.ensure_zero_plus_monoid_equals(Just(9))

    def test_associativity(self):
        self.given_monoids(Just(1), Just(2), Just(3))
        self.ensure_associativity()

    def test_mplus_with_two_just_values(self):
        self.given_monoids(Just(1), Just(2))
        self.ensure_mconcat_equals(Just(3))

    def test_mplus_with_one_just_and_one_nothing(self):
        self.given_monoids(Just(1), Nothing)
        self.ensure_mconcat_equals(Just(1))


class TestFirstMonoid(MonoidTester):
    def test_mzero(self):
        self.given_monoid(First)
        self.get_mzero()
        self.ensure_mzero_is(First(Nothing))

    def test_right_identity(self):
        self.given_monoid(First(Just(9)))
        self.ensure_monoid_plus_zero_equals(First(Just(9)))

    def test_left_identity(self):
        self.given_monoid(First(Just(9)))
        self.ensure_zero_plus_monoid_equals(First(Just(9)))

    def test_associativity(self):
        self.given_monoids(First(Just(1)), First(Just(2)), First(Just(3)))
        self.ensure_associativity()

    def test_mplus_with_two_just_values(self):
        self.given_monoids(First(Just(1)), First(Just(2)))
        self.ensure_mconcat_equals(First(Just(1)))

    def test_mplus_with_just_and_nothing(self):
        self.given_monoids(First(Just(1)), Nothing)
        self.ensure_mconcat_equals(First(Just(1)))

    def test_mplus_with_nothing_and_just(self):
        self.given_monoids(Nothing, First(Just(1)))
        self.ensure_mconcat_equals(First(Just(1)))


class TestLastMonoid(MonoidTester):
    def test_mzero(self):
        self.given_monoid(Last)
        self.get_mzero()
        self.ensure_mzero_is(Last(Nothing))

    def test_right_identity(self):
        self.given_monoid(Last(Just(9)))
        self.ensure_monoid_plus_zero_equals(Last(Just(9)))

    def test_left_identity(self):
        self.given_monoid(Last(Just(9)))
        self.ensure_zero_plus_monoid_equals(Last(Just(9)))

    def test_associativity(self):
        self.given_monoids(Last(Just(1)), Last(Just(2)), Last(Just(3)))
        self.ensure_associativity()

    def test_mplus_with_two_just_values(self):
        self.given_monoids(Last(Just(1)), Last(Just(2)))
        self.ensure_mconcat_equals(Last(Just(2)))

    def test_mplus_with_just_and_nothing(self):
        self.given_monoids(Last(Just(1)), Nothing)
        self.ensure_mconcat_equals(Last(Just(1)))

    def test_mplus_with_nothing_and_just(self):
        self.given_monoids(Nothing, Last(Just(1)))
        self.ensure_mconcat_equals(Last(Just(1)))

if __name__ == "__main__":
    unittest.main()
