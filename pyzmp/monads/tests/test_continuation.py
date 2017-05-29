from __future__ import absolute_import, division, print_function

import collections

import unittest
from pyzmp.monads.maybe import Maybe, Just, First, Last, _Nothing, Nothing
from pyzmp.monads.monad import do, done
from pyzmp.monads.functor import unit
from pyzmp.monads.continuation import Continuation, call_cc
from pyzmp.monads.tests.monad_tester import MonadTester
from pyzmp.monads.tests.monoid_tester import MonoidTester


class TestContinuationFunctor(MonadTester):
    def __init__(self, x):
        super(TestContinuationFunctor, self).__init__(x)
        self.set_class_under_test(Continuation)

    def testFunctorLaws(self):
        self.given(8)
        self.ensure_first_functor_law_holds()
        self.ensure_second_functor_law_holds()


class TestContinuationApplicative(MonadTester):
    def __init__(self, x):
        super(TestContinuationApplicative, self).__init__(x)
        self.set_class_under_test(Continuation)

    def testApplicativeLaws(self):
        self.given(8)
        self.ensure_first_applicative_law_holds()
        self.ensure_second_applicative_law_holds()
        self.ensure_third_applicative_law_holds()
        self.ensure_fourth_applicative_law_holds()
        self.ensure_fifth_applicative_law_holds()


class ContinuationTests(unittest.TestCase):
    class Mailbox:

        def __init__(self):
            self.messages = collections.deque()
            self.handlers = collections.deque()

        def send(self, message):
            if self.handlers:
                handler = self.handlers.popleft()
                handler(message)()
            else:
                self.messages.append(message)

        def receive(self):
            return call_cc(self.react)

        @do(Continuation)
        def react(self, handler):
            if self.messages:
                message = self.messages.popleft()
                yield handler(message)
            else:
                self.handlers.append(handler)
                done(Continuation.mzero())

    def testDo(self):

        @do(Continuation)
        def insert(mb, values):
            for val in values:
                mb.send(val)

        @do(Continuation)
        def multiply(mbin, mbout, factor):
            while True:
                val = (yield mbin.receive())
                mbout.send(val * factor)

        @do(Continuation)
        def print_all(mb):
            while True:
                y = yield mb.receive()
                print(y)

        original = ContinuationTests.Mailbox()
        multiplied = ContinuationTests.Mailbox()

        print_all(multiplied)()
        multiply(original, multiplied, 2)()
        insert(original, [1, 2, 3])()

    # def testContinuationFunctor(self):
    #     comp1 = neg << sub(4)
    #     comp2 = sub(4) << neg
    #     comp3 = neg << sub(4) << neg
    #     self.assertEqual(comp1(3), -1)
    #     self.assertEqual(comp2(3), 7)
    #     self.assertEqual(comp3(3), -7)
    #
    # def testContinuationApplicative(self):
    #     x = add << mul(5) & mul(6)
    #     self.assertEqual(x(5), 55)
    #
    # def testContinuationMonad(self):
    #     x = (mul(2) >> (lambda a: add(10) >> (lambda b: Reader(a + b))))
    #     self.assertEqual(x(3), 19)


class TestContinuationUnit(unittest.TestCase):
    def testUnitOnContinuation(self):
        self.assertEqual(Continuation.unit(8)(lambda _: 42), 8)
        self.assertEqual(unit(Continuation, 8)(lambda _: 42), 8)

# def test_continuation_example():
#     from collections import deque
#
#     class Mailbox:
#         def __init__(self):
#             self.messages = deque()
#             self.handlers = deque()
#
#         def send(self, message):
#             if self.handlers:
#                 handler = self.handlers.popleft()
#                 handler(message)()
#             else:
#                 self.messages.append(message)
#
#         def receive(self):
#             return monads.callcc(self.react)
#
#         @monads.do(monads.Continuation)
#         def react(self, handler):
#             if self.messages:
#                 message = self.messages.popleft()
#                 yield handler(message)
#             else:
#                 self.handlers.append(handler)
#                 monads.done(monads.Continuation.zero())
#
#     @monads.do(monads.Continuation)
#     def insert(mb, values):
#         for val in values:
#             mb.send(val)
#
#     @monads.do(monads.Continuation)
#     def multiply(mbin, mbout, factor):
#         while True:
#             val = (yield mbin.receive())
#             mbout.send(val * factor)
#
#     @monads.do(monads.Continuation)
#     def print_all(mb):
#         while True:
#             y = yield mb.receive()
#             print(y)
#
#     original = Mailbox()
#     multiplied = Mailbox()
#
#     print_all(multiplied)()
#     multiply(original, multiplied, 2)()
#     insert(original, [1, 2, 3])()
