from __future__ import absolute_import, division, print_function


import pyzmp.monads as monads


def test_continuation_example():
    from collections import deque

    class Mailbox:
        def __init__(self):
            self.messages = deque()
            self.handlers = deque()

        def send(self, message):
            if self.handlers:
                handler = self.handlers.popleft()
                handler(message)()
            else:
                self.messages.append(message)

        def receive(self):
            return monads.callcc(self.react)

        @monads.do(monads.Continuation)
        def react(self, handler):
            if self.messages:
                message = self.messages.popleft()
                yield handler(message)
            else:
                self.handlers.append(handler)
                monads.done(monads.Continuation.zero())

    @monads.do(monads.Continuation)
    def insert(mb, values):
        for val in values:
            mb.send(val)

    @monads.do(monads.Continuation)
    def multiply(mbin, mbout, factor):
        while True:
            val = (yield mbin.receive())
            mbout.send(val * factor)

    @monads.do(monads.Continuation)
    def print_all(mb):
        while True:
            y = yield mb.receive()
            print(y)

    original = Mailbox()
    multiplied = Mailbox()

    print_all(multiplied)()
    multiply(original, multiplied, 2)()
    insert(original, [1, 2, 3])()
