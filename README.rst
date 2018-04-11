PyZMP
=====


.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - |travis| |requires| |landscape|
    * - Python
      - |version| |downloads| |wheel| |supported-versions| |supported-implementations|
    * - ROS
      -  **Indigo** |ros_indigo_pkg| **Jade** |ros_jade_pkg| **Kinetic** |ros_kinetic_pkg|

.. |docs| image:: https://readthedocs.org/projects/pyzmp/badge/?style=flat
    :target: https://readthedocs.org/projects/pyzmp
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/asmodehn/pyzmp.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/asmodehn/pyzmp

.. |requires| image:: https://requires.io/github/asmodehn/pyzmp/requirements.svg?branch=master
    :alt: Requirements Status
    :target: hhttps://requires.io/github/asmodehn/pyzmp/requirements/?branch=master

.. |landscape| image:: https://landscape.io/github/asmodehn/pyzmp/master/landscape.svg?style=flat
    :target: hhttps://landscape.io/github/asmodehn/pyzmp/master
    :alt: Code Quality Status

.. |version| image:: https://img.shields.io/pypi/v/pyzmp.svg?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/pyzmp

.. |downloads| image:: https://img.shields.io/pypi/dm/pyzmp.svg?style=flat
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/pyzmp

.. |wheel| image:: https://img.shields.io/pypi/wheel/pyzmp.svg?style=flat
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/pyzmp

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/pyzmp.svg?style=flat
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/pyzmp

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/pyzmp.svg?style=flat
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/pyzmp

.. |ros_indigo_pkg| image:: https://travis-ci.org/asmodehn/pyzmp-rosrelease.svg?branch=release/indigo/pyzmp
    :alt: ROS Indigo Build
    :target: https://travis-ci.org/asmodehn/pyzmp-rosrelease/branches

.. |ros_jade_pkg| image:: https://travis-ci.org/asmodehn/pyzmp-rosrelease.svg?branch=release/jade/pyzmp
    :alt: ROS Jade Build
    :target: https://travis-ci.org/asmodehn/pyzmp-rosrelease/branches

.. |ros_kinetic_pkg| image:: https://travis-ci.org/asmodehn/pyzmp-rosrelease.svg?branch=release/kinetic/pyzmp
    :alt: ROS Kinetic Build
    :target: https://travis-ci.org/asmodehn/pyzmp-rosrelease/branches

.. end-badges




PyZMP is a multiprocess library based on ZeroMQ.

The aim is to make experimenting with multiprocess and distributed architecture more solid and overall easier.
If at all possible, the goal is to arrive at a minimal set of concepts, that makes solid and efficient distributed system easy to build.

Distributed systems models, as per wikipedia https://en.wikipedia.org/wiki/Distributed_computing#Models, can be classified as:

- Parallel algorithms in shared-memory model: This seems applicable in distributed software using a consensus algorithm as the shared memory.
- Parallel algorithms in message-passing model: This seems applicable in distributed software relying mostly on dataflow architecture, where the implementor can decide on the network structure
- Distributed algorithms in message-passing model: This seems to be the most widely used currently, (web backend model, relying on services available from multiple places for example)

We will focus on the latter first, while keeping in mind it is likely just a special case of the second (network cannot be controlled, algorithm on each node has to be the same).
A good exercise here is how to keep a representation of the distribution coherent on each node, despite potential network partition that cna occur.

Doing an Analysis on existing distributed software architecture is likely a very broad task, but we can focus on just a few here, at least as a first step.
These should be enough to implement any of the distributed systems models cited above:

- service / RPC oriented architectures ( usually implemented via https://en.wikipedia.org/wiki/Request%E2%80%93response )
- dataflow architecture ( usually implemented via https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern )

with different views for the user, more or less transparently :
- make a request / send a task and (asynchronously or not) wait the response/result
- receive dataflow from somewhere and send dataflow to somewhere else

Additionally, an interesting endeavour could be to see how https://en.wikipedia.org/wiki/Control_theory applies to such distributed systems (message passing <=> charge transfer).

Note : This is currently a personal perspective that likely require more thorough analysis, so feel free to send a Pull Request.


Repository structure
--------------------

This repository has a few main branches:

- master : main branch, python dev workflow, releasing version tags into a pip package.

Apart from these we follow a `feature branching workflow <https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow>`_


How to use
----------

Install
```
pip install pyzmp
```

Run self tests
```
pyzmp
```

How to develop
--------------

Clone this repository
```
git clone http://github.com/asmodehn/pyzmp
```

Create you virtualenv to workon using virtualenvwrapper
```
mkvirtualenv pyzmpenv
```

Install all dependencies via dev-requirements
```
pip install -r dev-requirements.txt
```

Run self tests
```
pyzmp
```

Run all tests (with all possible configurations) with tox
```
tox
```

Note : Tox envs are recreated every time to ensure consistency.
So it s better to develop while in a non-tox-managed venv.


Tutorials and examples
----------------------
A good example showing use of pyzmp, `simple RPC client/server example <http://pyzmp.readthedocs.io/en/latest/tutorial.html#simple-rpc-client-server-example>`_

tutorials implementing `multi node communication <https://github.com/dhirajdhule/pyzmp_tutorials>`_ (under development)

Roadmap
-------

Distributed software means software being executed in different "nodes" and collaboration via communication through different "channels":

- Node : A code executing entity. Can be a process, a thread, or a group of nodes communicating together.
- Channels : A way to make two or more node communicate in a way that allow them to collaborate.

This will allow us to structure our software in a network graph.
PYZMP aims to be the foundation on which such a network graph can be easily, and confidently, built and used.

Implementation Priorities :

1. Local multiprocess first (we force data partition without forcing connections/sockets management)
2. Multiple concurrency implementation (Thread (all kinds), entity-component as a monothread implementation)
3. Remote concurrency (managing remote connections)

Type of Distributed Architecture that can be built with pyzmp:

1) Service(RPC) based architecture http://zguide.zeromq.org/page:all#Ask-and-Ye-Shall-Receive :

- It s a well proven way of architecture a distributed software, since it is the prevalent model used in the web architecture (REST, HTTP, RPC, etc.)
- There are some constraints in the way this must be implemented to work.
- There are more constraints if we want to implement it in a way that is easy to use.

2) DataFlow based architecture http://zguide.zeromq.org/page:all#Getting-the-Message-Out :

- It s a quite heavily used distributed architecture (topics, XMPP, ROS, etc.)
- There are some constraints in the way this must be implemented to work.
- There are more constraints if we want to implement it in a way that is easy to use.
- It is theoretically more complex to grasp than the service based architecture, therefore will be dealt with at a later time.

3) TBD : depending on analysis of existing system and what can be necessary to existing architecture, we will see what comes up.


Constraints:

- we want to be able to control where is executed what (no full transparency of the distribution)
- we want to create a solid platform on which other distributed algorithms can be implemented
- usual distributed algorithms ( cache, proxy, feedback ) should be super easy to implement, and will eventually be provided here as examples, or part of a larger "toolbox".
- We should minimize our software complexity on order to build a stable and easily maintainable system. A consensus algorithm (raft) would be very useful to implement distributed algorithms, but should be built outside of pyzmp. However pyzmp might need it to be able to function properly...

