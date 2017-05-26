from __future__ import absolute_import, division, print_function

import unittest

from pyzmp.monads.tests.monoid_tester import *

from pyzmp.monads.monoid import Monoid


class TestNaturalMonoidFloat(MonoidTester):
    """
    The Float "Natural" Monoid just uses normal python numbers with:
        mzero = 0, and
        mplus = +
    It's not necessary to use a special class to use them.
    """

    def test_monoid_plus_zero(self):
        self.given_monoid(8.1)
        self.ensure_monoid_plus_zero_equals(self.monoid)

    def test_zero_plus_monoid(self):
        self.given_monoid(8.1)
        self.ensure_zero_plus_monoid_equals(self.monoid)

    def test_monoid_associativity(self):
        self.given_monoids(8.1, 2.4, 3.5)
        self.ensure_associativity()


class TestNaturalMonoidInteger(MonoidTester):
    """
    The Integer "Natural" Monoid just uses normal python numbers with:
        mzero = 0, and
        mplus = +
    It's not necessary to use a special class to use them.
    """

    def test_monoid_plus_zero(self):
        self.given_monoid(8)
        self.ensure_monoid_plus_zero_equals(self.monoid)

    def test_zero_plus_monoid(self):
        self.given_monoid(8)
        self.ensure_zero_plus_monoid_equals(self.monoid)

    def test_monoid_associativity(self):
        self.given_monoids(8, 2, 3)
        self.ensure_associativity()


class TestNaturalMonoidString(MonoidTester):
    """
    The String "Natural" Monoid just uses normal python strings with:
        mzero = "", and
        mplus = +
    It's not necessary to use a special class to use them.
    """

    def test_monoid_plus_zero(self):
        self.given_monoid("hello")
        self.ensure_monoid_plus_zero_equals(self.monoid)

    def test_zero_plus_monoid(self):
        self.given_monoid("hello")
        self.ensure_zero_plus_monoid_equals(self.monoid)

    def test_monoid_associativity(self):
        self.given_monoids("hello", "cruel", "world!")
        self.ensure_associativity()


class TestNaturalMonoidList(MonoidTester):
    """
    The List "Natural" Monoid just uses normal python lists with:
        mzero = [], and
        mplus = +
    It's not necessary to use a special class to use them.
    """

    def test_monoid_plus_zero(self):
        self.given_monoid([1, 2, 3])
        self.ensure_monoid_plus_zero_equals(self.monoid)

    def test_zero_plus_monoid(self):
        self.given_monoid([1, 2, 3])
        self.ensure_zero_plus_monoid_equals(self.monoid)

    def test_monoid_associativity(self):
        self.given_monoids([1, 2, 3], [4, 5, 6], [7, 8, 9])
        self.ensure_associativity()


class TestCustomMonoid(MonoidTester):
    """
    User defined Monoids need to over-ride mzero and mplus.
    """

    def test_monoid_plus_zero(self):
        self.given_monoid(Product(3))
        self.ensure_monoid_plus_zero_equals(self.monoid)

    def test_zero_plus_monoid(self):
        self.given_monoid(Product(3))
        self.ensure_zero_plus_monoid_equals(self.monoid)

    def test_monoid_associativity(self):
        self.given_monoids(Product(3), Product(4), Product(5))
        self.ensure_associativity()


class TestNotAMonoid(unittest.TestCase):
    def test_should_raise_TypeError(self):
        self.assertRaises(TypeError, mzero, {1: 1})


class Test_mconcat(MonoidTester):
    def test_mconcat_on_natural_monoid(self):
        self.given_monoids(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        self.ensure_mconcat_equals(55)

    def test_mconcat_on_custom_monoid(self):
        self.given_monoids(Product(2), Product(3), Product(4), Product(5))
        self.ensure_mconcat_equals(Product(120))


class Test_mzero(MonoidTester):
    def test_mzero_with_integers(self):
        self.given_monoid(8)
        self.get_mzero()
        self.ensure_mzero_is(0)

    def test_mzero_with_floats(self):
        self.given_monoid(8.1)
        self.get_mzero()
        self.ensure_mzero_is(0)

    def test_mzero_with_strings(self):
        self.given_monoid("hello")
        self.get_mzero()
        self.ensure_mzero_is("")

    def test_mzero_with_lists(self):
        self.given_monoid([1, 2, 3])
        self.get_mzero()
        self.ensure_mzero_is([])

    def test_mzero_with_custom(self):
        self.given_monoid(Product(3))
        self.get_mzero()
        self.ensure_mzero_is(Product(1))

    def test_mzero_with_class_int(self):
        self.given_monoid(int)
        self.get_mzero()
        self.ensure_mzero_is(0)

    def test_mzero_with_class_float(self):
        self.given_monoid(float)
        self.get_mzero()
        self.ensure_mzero_is(0)

    def test_mzero_with_class_str(self):
        self.given_monoid(str)
        self.get_mzero()
        self.ensure_mzero_is("")

    def test_mzero_with_class_list(self):
        self.given_monoid(list)
        self.get_mzero()
        self.ensure_mzero_is([])

    def test_mzero_with_custom_class(self):
        self.given_monoid(Product)
        self.get_mzero()
        self.ensure_mzero_is(Product(1))

if __name__ == "__main__":
    unittest.main()
