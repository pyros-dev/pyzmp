from __future__ import absolute_import, division, print_function

import collections
from io import open

import os

import functools

import six
import yaml

from concurrent.futures import ThreadPoolExecutor

"""
Module allowing to GRAFT folder hierarchy with files mapping trees

Design concepts : 
- One thread per process to handle File system access
- One object instance per actual resource
  => one YAMLEncoder instance for one file or one string (determined on load/dump)
  => one YAMLHierarchyEncoder for one directory (determined on initialization)
"""

# TODO : shelves + dbm.yaml (see dbm_yaml)
# TODO: a graph DB like https://networkx.github.io/ or https://github.com/arangodb/arangodb
# with file persistency as an option + a way to restart if needed.


def depth(d, level=1):
    if not isinstance(d, dict) or not d:
        return level
    return max(depth(d[k], level + 1) for k in d)


_executor = ThreadPoolExecutor(max_workers=1)  # only one thread to manage all file access for this package


class YAMLEncoder(object):
    """YAML Encoder, decoupling the object instance and the side effect, for cleaner composition."""

    def __init__(self, **kwargs):
        # setting some useful defaults
        kwargs.setdefault('default_flow_style', False)
        kwargs.setdefault('allow_unicode', True)
        kwargs.setdefault('explicit_start', True)
        self.settings = kwargs

    def dump(self, data, stream=None):
        return yaml.dump(data, stream, **self.settings)

    def future_dump(self, data, stream=None):
        """Dump data into a file asynchronously (eager)
        Maybe not really useful since for writing, we want direct control flow.
        """
        return _executor.submit(self.dump, data, stream)


class YAMLHierarchyEncoder(YAMLEncoder):
    """
    An encoder that stores a mapping as a folder/files hierarchy
    """
    def __init__(self, filekeys, **encoder_settings):
        """
        Initialising the encoder to dump data into a path (file or directory)

        :param filekeys: list of keys to encode into YAML files (and stop the hierarchy creation).
        Any higher level key will be represented as a directory, potentially containing other directories.
        By default this is an empty list, meaning
        :param kwargs: extra args
        :return:
        """
        self._filekeys = filekeys or []
        # We only need one encoder to keep settings
        self._file_encoder = YAMLEncoder(**encoder_settings)

    @property
    def settings(self):
        return self._file_encoder.settings

    # TODO Is there a simple / cleaner magic method (getattr ? getitem ?) to do this ?
    # we also dont want to be confused with the entries indexing if it makes things not obvious somehow...
    def sub(self, relpath):
        newdir = os.path.join(self._path, relpath)
        # direct controlled creation
        os.makedirs(newdir)
        return YAMLHierarchyEncoder(path=newdir, filekey=self._filekeys, **self.settings)

    def _clean_missing(self, data, stream):
        # remove unexisting keys mercilessly
        for d in os.listdir(stream):
            if d not in data:
                os.remove(os.path.join(stream, d))

    def dump(self, data, stream=None):
        """
        Dumping data into a path (file or directory). Direct control flow.
        :param data : the data
        :param stream : the path to save the data in
        :return: TODO
        """
        stream = stream or os.getcwd()  # default to current directory

        self._clean_missing(data, stream)

        returned_data = {}

        for k, v in data.items():
            if k in self._filekeys and isinstance(v, collections.Mapping):
                # the filekey is skipped here,
                # so it should be explicit enough for a user viewing the file hierarchy...
                encoded_v = {}
                for kk, vv in v.items():
                    with open(os.path.join(stream, kk), "w", encoding='utf8') as fh:
                        encoded_v[kk] = self._file_encoder.dump(vv, fh)
            else:
                if not isinstance(v, collections.Mapping):
                    with open(os.path.join(stream, k), "w", encoding='utf8') as fh:
                        encoded_v = self._file_encoder.dump(v, fh)
                else:
                    # recurse (keeping one instance per directory)
                    newdir = os.path.join(stream, k)
                    os.makedirs(newdir)
                    encoded_v = YAMLHierarchyEncoder(newdir, filekeys=self._filekeys, **self.settings).dump(v)
            returned_data.update({k: encoded_v})

        # => what should we return ???
        # TODO : check monads and effect theory...
        # TODO : check delimited continuations...
        return returned_data

    #def future_dump():

# TODO: unify codec ( check jsonpickle, marshmallow and other serialization/ data validation libs )

class YAMLDecoder(object):
    """YAML Decoder, decoupling the object instance and the side effect, for cleaner composition."""
    def __init__(self, **kwargs):
        self.settings = kwargs

    def load(self, stream=None):
        return yaml.load(stream, **self.settings)

    def future_load(self, stream):
        """Dump data into a file asynchronously (lazy)
        """
        return _executor.submit(self.load, stream)


class YAMLHierarchyDecoder(object):
    """
    A decoder that retrieve a mapping from a folder/files hierarchy
    """
    def __init__(self, filekeys, **decoder_settings):
        self._filekeys = filekeys
        self._file_decoder = YAMLDecoder(**decoder_settings)

    def load(self, stream=None):
        """
        Loading mapping data from a path hierarchy. Direct lazy control flow.
        :return:
        """

        if os.path.isfile(stream):
            with open(stream, "r") as fh:  # maybe unneeded (already in yaml pkg) ?
                data = self._file_decoder.future_load(fh)
        elif os.path.isdir(stream):
            # recurse (keeping one instance per directory)
            pathlist = os.listdir(stream)
            data = {p: YAMLHierarchyDecoder(self._filekeys, **self._file_decoder.settings).load(os.path.join(stream, p)) for p in pathlist}
        else:
            # Something not a file and not a dir ?
            return NotImplementedError

        return data

# TODO : JSON ? / BSON -> mongoDB ? / Local Redis ? -> SQLalchemy ?
# Reminder : might need to persist on crash & restart
