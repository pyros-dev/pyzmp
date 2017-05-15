from __future__ import absolute_import, division, print_function, unicode_literals

import os
import uuid

"""
This module provides a class to manage dictionaries - yaml files synchronisation
"""

import collections
import yaml
import logging
import contextlib
import tempfile

import fasteners

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler)


def UUID_filename(uuid):
    """
    :param uuid: The UUID for the shared resource 
    :return: the shared filename
    """
    filename = os.path.join(tempfile.gettempdir(), 'pyzmp-0', str(uuid) + '.yml')
    return filename



def filename_UUID(filepath):
    """
    :param filepath: the filename of hte shared resource 
    :return: the uuid
    """
    assert os.path.dirname(filepath) == 'pyzmp-0'
    return os.path.basename(filepath)


class YamlDict(object):
    def __init__(self, UUID=None):
        self.UUID = UUID or uuid.uuid4()
        self.filepath = UUID_filename(UUID)

    @contextlib.contextmanager
    def __call__(self, *args, **kwargs):
        with fasteners.read_locked():
        with open(self.filepath, 'r') as yfh:
            d = yaml.load(yfh)

        yield d

        with open(self.filepath, 'w') as yfh:
            yaml.dump(d, yfh, default_flow_style=False)

