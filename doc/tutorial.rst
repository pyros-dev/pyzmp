pyzmp tutorial
==============

Setup
-----

First, we need to prepare the environment::

    mkvirtualenv pyzmp
    pip install .

Simple RPC client / server example
----------------------------------

Here is an example using inheritance from pyzmp.Node::

    (pyzmp)alexv@AlexV-Linux:~/Projects/pyzmp$ python
    Python 2.7.6 (default, Jun 22 2015, 17:58:13)
    [GCC 4.8.2] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import pyzmp
    WARNING:root:ZMQ : Protobuf message implementation not found. Using pickle based protocol
    >>> class ServerNode(pyzmp.Node):
    ...     def __init__(self, name):
    ...             super(ServerNode, self).__init__(name)
    ...             self.the_answer= 42
    ...             self.provides(self.question)
    ...     def question(self):
    ...             return self.the_answer
    ...
    >>> srv = ServerNode("srv")
    >>> srv.start()
    [srv] Node started as [6532 <= ipc:///tmp/zmp-srv-tVEvI_/services.pipe]
    True

In another terminal you can overview the processes running::

    alexv@AlexV-Linux:~$ pstree -cap 6532
    python,6532
      ├─{python},6539
      └─{python},6540

Back into the same python intrepreter::

    >>> question = pyzmp.discover("question")
    >>> question
    <pyzmp.service.Service object at 0x7fc1607215d0>
    >>> question.call()
    42
    >>>

So here we have a very basic example of a communication between different processes through ZMQ.

Simple RPC client / server example with context management
----------------------------------------------------------

A pyzmp Node is also a context manager (since there is a resource to initialize and cleanup : the process),
which means you can shorten your code, and prevent leaving useless processes behind. The previous example can be rewritten ::

    Python 2.7.12 (default, Dec  4 2017, 14:50:18)
    [GCC 5.4.0 20160609] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import pyzmp
    WARNING:root:ZMQ : Protobuf message implementation not found. Using pickle based protocol
    >>> class ServerNode(pyzmp.Node):
    ...     def __init__(self, name):
    ...             super(ServerNode, self).__init__(name)
    ...             self.the_answer = 42
    ...             self.provides(self.question)
    ...     def question(self):
    ...             return self.the_answer
    ...
    >>> with ServerNode("srv") as srv:
    ...     question = pyzmp.discover("question")
    ...     question.call()
    ...
    [srv] Proc started as [5393]
    42
    Shutdown initiated
    >>>

Here the srv process was started when entering the "with:" block, and was terminated when exiting it.

Simple RPC client / server example with delegation
--------------------------------------------------
Often having hierarchy will make your code more complex, and difficult to evolve when requirements change.
So you can also use pyzmp.Node as a delegate.


Disclaimer : currently BROKEN : see https://github.com/asmodehn/pyzmp/issues/36
You should implement your own context manager, which is what you want to do most of the time to control initialization anyway::

    >>> class ServerNode(object):
    ...     def __init__(self, name):
    ...         self.node = pyzmp.Node(name)
    ...         self.the_answer = 42
    ...         self.node.provides(self.question)
    ...     def question(self):
    ...         return self.the_answer
    ...     def __enter__(self):
    ...         return self.node.__enter__()
    ...     def __exit__(self ,type, value, traceback):
    ...         return self.node.__exit__(type, value, traceback)
    ...
    >>> with ServerNode("srv") as srv:
    ...     question = pyzmp.discover("question")
    ...     question.call()
    ...
    [srv] Proc started as [5973]
    Shutdown initiated




Context managers are used only in the child process, but enter() and exit() calls are in order which provide deterministic behavior,
by contrast to multiprocess communication which is by default indeterministic.

A current limitation however is that discover currently works out of the box only from the same python interpreter.
As a result we have to rely on a process manager running in the same interpreter.

A later version will provide an API to make this simple, even between two different interpreters, so that process management can be done somewhere else.




