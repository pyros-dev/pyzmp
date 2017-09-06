from __future__ import absolute_import, print_function

import os
import tempfile

from ._local_registry import FileBasedLocalRegistry

# TODO : https://github.com/biesnecker/hachiko instead of watchdog (prioritise asyncio style)

# Declaring the unique registry for this interpreter
# It will use the same path than other interpreter processes
registry = FileBasedLocalRegistry(os.path.join(tempfile.gettempdir()), "localhost.zmp")
# TODO : /var/run instead ?

__all__ = [
    'FileBasedRegistry'
]
