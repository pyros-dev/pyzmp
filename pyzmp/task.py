from __future__ import absolute_import, division, print_function


from concurrent.futures import Future

"""
A Task is a completely serializable, atomic, unit of computing, that can be transferred between Threads (and therefore Processes).

"""


class Task(Future):  # TODO : link with asyncio on py3
    pass  # TODO
