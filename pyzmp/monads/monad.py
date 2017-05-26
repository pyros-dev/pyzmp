from __future__ import absolute_import, division, print_function

"""
Base Monad and @do syntax
"""

import types

from .applicative import Applicative


class Monad(Applicative):
    """
    Represents a "context" in which calculations can be executed.
    
    You won't create `Monad` instances directly. Instead, sub-classes implement
    specific contexts. Monads allow you to bind together a series of calculations
    while maintaining the context of that specific monad.
    
    """

    __slots__ = []  # we inherit value from Container, and keep a tiny object.

    def __init__(self, value):
        """ Wraps `value` in the Monad's context. """
        super(Monad, self).__init__(value)

    def bind(self, fun):
        """ Applies `function` to the result of a previous monadic calculation. """
        raise NotImplementedError

    def __rshift__(self, fun):
        """
        The 'bind' operator. The following are equivalent::
    
            monadValue >> someFunction
            monadValue.bind(someFunction)
    
        """
        if callable(fun):
            result = self.bind(fun)
            if not isinstance(result, Monad):
                raise TypeError("Operator '>>' must return a Monad instance.")
            return result
        else:
            if not isinstance(fun, Monad):
                raise TypeError("Operator '>>' must return a Monad instance.")
            return self.bind(lambda _: fun)



# class Monad:
#     def bind(self, func):
#         raise NotImplementedError
#
#     def __rshift__(self, bindee):
#         return self.bind(bindee)
#
#     def __add__(self, bindee_without_arg):
#         return self.bind(lambda _: bindee_without_arg())


def make_decorator(func, *dec_args):
    def decorator(undecorated):
        def decorated(*args, **kargs):
            return func(undecorated, args, kargs, *dec_args)

        decorated.__name__ = undecorated.__name__
        return decorated

    decorator.__name__ = func.__name__
    return decorator


def make_decorator_with_args(func):
    def decorator_with_args(*dec_args):
        return make_decorator(func, *dec_args)

    return decorator_with_args


decorator = make_decorator
decorator_with_args = make_decorator_with_args


@decorator_with_args
def do(func, func_args, func_kargs, Monad):
    @handle_monadic_throws(Monad)
    def run_maybe_iterator():
        itr = func(*func_args, **func_kargs)

        if isinstance(itr, types.GeneratorType):
            @handle_monadic_throws(Monad)
            def send(val):
                try:
                    # here's the real magic
                    monad = itr.send(val)
                    return monad.bind(send)
                except StopIteration:
                    return Monad.unit(None)

            return send(None)
        else:
            # not really a generator
            if itr is None:
                return Monad.unit(None)
            else:
                return itr

    return run_maybe_iterator()


@decorator_with_args
def handle_monadic_throws(func, func_args, func_kargs, Monad):
    try:
        return func(*func_args, **func_kargs)
    except MonadReturn as ret:
        return Monad.unit(ret.value)
    except Done as done:
        assert isinstance(done.monad, Monad)
        return done.monad


class MonadReturn(Exception):
    def __init__(self, value):
        self.value = value
        Exception.__init__(self, value)


class Done(Exception):
    def __init__(self, monad):
        self.monad = monad
        Exception.__init__(self, monad)


def mreturn(val):
    raise MonadReturn(val)


def done(val):
    raise Done(val)


def fid(val):
    return val
