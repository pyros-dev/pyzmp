from __future__ import absolute_import, division, print_function

from .monad import Monad


class Reader(Monad):
    """ Represents a Functor for functions allowing authors to map functions over other functions. """

    def __init__(self, function_or_value):
        """
        Stores or creates a function as the Functor's value.
    
        If `functionOrValue` is a function, it is stored directly.
        However, if it is a value -- 7 for example -- then a function taking a single argument
        which always returns that value is created and that function is stored as the Functor's
        value.
    
        In general, you won't create `Reader` instances directly. Instead use the @curry
        decorator when defining functions. `Reader` may not function as expected if
        non-curried functions are used.
    
        """

        if callable(function_or_value):
            func = function_or_value
        else:
            func = lambda _: function_or_value

        super(Reader, self).__init__(func)

    def __call__(self, *args):
        """
        Applies arguments to the curried function.
    
        Returns the result of the function if all arguments are passed. If fewer than
        the full argument set is passed in, returns a curried function which expects the
        remaining arguments. For example, a function ``func`` which takes 3 arguments can be
        called in any of the following ways:
            func(1, 2, 3)
            func(1, 2)(3)
            func(1)(2, 3)
            func(1)(2)(3)
    
        """
        value = self.value
        for a in args:
            try:
                value = value(a)
            except TypeError:
                raise TypeError("Too many arguments supplied to curried function.")

        if callable(value):
            return Reader(value)
        else:
            return value

    def __lshift__(self, func):
        return func.fmap(self)

    def fmap(self, fun):
        """
        Maps `aFunction` over the function stored in the Functor itself.
    
        Mapping a function over another function is equivalent to function composition.
        In other words,::
    
            composedFunc = curriedFunc1 << curriedFunc2
            composedFunc(parameter)
    
        is equivalent to::
    
            composedFunc = lambda x: curriedFunc1(curriedFunc2(x))
            composedFunc(parameter)
    
        Both ``curriedFunc1`` and ``curriedFunc2`` must take only a single argument
        but either, or both, can be partially applied so they have only a single argument
        remaining.
    
        """
        return Reader(lambda x: fun(self.value(x)))

    def amap(self, functor_value):
        """ Applies function stored in the functor to `functorValue` creating a new function. """
        return Reader(lambda x: self(x)(functor_value(x)))

    def bind(self, fun):
        """ Threads a single value through multiple function calls. """
        return Reader(lambda x: fun(self.value(x))(x))

    @classmethod
    def unit(cls, value):
        return Reader(lambda _: value)


def curry(fun):
    """
    Turns a normal python function into a curried function.
    
    Most easily used as a decorator when defining functions:
        @curry
        def add(x, y): return x + y
    
    """
    def build_reader(arg_values, num_args):
        if num_args == 0:
            return fun(*arg_values)
        else:
            def recurse(x):
                return build_reader(arg_values + [x], num_args - 1)
            return recurse
    return Reader(build_reader([], fun.__code__.co_argcount))
