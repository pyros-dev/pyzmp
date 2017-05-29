
import unittest
from pyzmp.monads.writer import NumberWriter, StringWriter, Writer
from pyzmp.monads.tests.monad_tester import MonadTester
from pyzmp.monads.maybe import Just


class TestWriterFunctor(MonadTester):
    def __init__(self, x):
        super(TestWriterFunctor, self).__init__(x)
        self.set_class_under_test(NumberWriter)

    def testFunctorLaws(self):
        self.given((8, 5))
        self.ensure_first_functor_law_holds()
        self.ensure_second_functor_law_holds()


class TestWriterApplicative(MonadTester):
    def __init__(self, x):
        super(TestWriterApplicative, self).__init__(x)
        self.set_class_under_test(NumberWriter)

    def testApplicativeLaws(self):
        self.given((8, 5))
        self.ensure_first_applicative_law_holds()
        self.ensure_second_applicative_law_holds()
        self.ensure_third_applicative_law_holds()
        self.ensure_fourth_applicative_law_holds()
        self.ensure_fifth_applicative_law_holds()


class TestWriterMonad(MonadTester):
    def __init__(self, x):
        super(TestWriterMonad, self).__init__(x)
        self.set_class_under_test(StringWriter)

    def monad_function_f(self, x):
        return Writer((x / 10, "Division successful."))

    def monad_function_g(self, x):
        return Writer((x * 10, "Multiplication successful."))

    def testMonadLaws(self):
        self.given((8, "dummy"))
        self.ensure_first_monad_law_holds()
        self.ensure_second_monad_law_holds()
        self.ensure_third_monad_law_holds()


class TestWriterAlternateConstructorForm(MonadTester):
    def testConstructors(self):
        firstConstructorForm = Writer(("value", "logMessage"))
        secondConstructorForm = Writer("value", "logMessage")
        self.assertEqual(firstConstructorForm, secondConstructorForm)


class TestWriterEquality(MonadTester):
    def testEqualityOfIdenticalTypes(self):
        self.given_monads(StringWriter(8, "log message"), StringWriter(8, "log message"))
        self.ensure_monads_are_equal()

    def testEqualityWithBaseType(self):
        self.given_monads(StringWriter(8, "log message"), Writer(8, "log message"))
        self.ensure_monads_are_equal()

    def testInequalityOfIdenticalTypesWithDifferentLog(self):
        self.given_monads(StringWriter(8, "log message"), StringWriter(8, "different message"))
        self.ensure_monads_are_not_equal()

    def testInequalityOfIdenticalTypesWithDifferentResult(self):
        self.given_monads(StringWriter(8, "log message"), StringWriter(9, "log message"))
        self.ensure_monads_are_not_equal()

    def testInequalityOfDifferentTypes(self):
        self.given_monads(StringWriter(8, "log message"), NumberWriter(8, 10))
        self.ensure_monads_are_not_equal()

    def testMonadComparisonException(self):
        self.given_monads(StringWriter(8, "log message"), Just(8))
        self.ensure_comparison_raises_exception()

if __name__ == "__main__":
    unittest.main()
