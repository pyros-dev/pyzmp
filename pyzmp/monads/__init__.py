from __future__ import absolute_import, division, print_function
"""
Monad implementation as a way to get async-like code, even on py27.

TODO: improve and rely on existing monad package, when one stable and maintained implementation 
working for python 2.7 (and py3) will be found.
"""


# Ref : http://www.valuedlessons.com/2008/01/monads-in-python-with-nice-syntax.html
# https://blogs.msdn.microsoft.com/wesdyer/2007/12/22/continuation-passing-style/
# https://bitbucket.org/jason_delaat/pymonad
# https://github.com/justanr/pynads
# https://github.com/dbrattli/OSlash
#

from .monad import Monad, do, mreturn, done, fid
from .maybe import Maybe, Just, Nothing
from .statechanger import StateChanger, get_state, change_state
from .continuation import Continuation, callcc

__all__ = [
    'Monad', 'do', 'mreturn', 'done', 'fid',
    'Maybe', 'Just', 'Nothing',
    'StateChanger', 'get_state', 'change_state',
    'Continuation', 'callcc'
]
