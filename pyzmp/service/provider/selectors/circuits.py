from __future__ import absolute_import
from __future__ import print_function

from circuits import Component, Event

# Ref : http://circuits.readthedocs.io/en/latest/tutorials/woof/index.html#overview
class hello(Event):
    """hello Event"""


class App(Component):

    def hello(self):
        print("Hello World!")

    def started(self, component):
        self.fire(hello())
        raise SystemExit(0)

App().run()