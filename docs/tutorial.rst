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
    Traceback (most recent call last):
    42
    >>>

So here we have a very basic example of a communication between different processes through ZMQ.

TODO : example using delegation

A current limitation however is that discover currently works out of the box only from the same python interpreter.
As a result we have to rely on a process manager running in the same interpreter.

A later version will provide an API to make this, between two different interpreters, trivial, so that process management can be done somewhere else.




