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


def depth(d, level=1):
    if not isinstance(d, dict) or not d:
        return level
    return max(depth(d[k], level + 1) for k in d)


executor = ThreadPoolExecutor(max_workers=1)  # only one thread to manage all file access for this package


class YAMLEncoder(object):
    """YAML Encoder, decoupling the object instance and the side effect, for cleaner composition."""

    def __init__(self, **kwargs):
        # enforcing some useful defaults
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
        return executor.submit(self.dump, data, stream)


class YAMLHierarchyEncoder(object):
    """
    An encoder that stores a mapping as a folder/files hierarchy
    """
    def __init__(self, path, filekey, **kwargs):
        """
        Dumping data into a path (file or directory)
        :param data : the data
        :param path : the path to save the data in
        :param filekey: the key indicating the mapping should be a set of files, instead of a directory hierarchy.
        Any higher level key will be represented as a directory, potentially containing other directories.
        :param kwargs: extra args
        :return:
        """
        self._path = path
        self._filekey = filekey
        # enforcing some useful defaults
        kwargs.setdefault('default_flow_style', False)
        kwargs.setdefault('allow_unicode', True)
        kwargs.setdefault('explicit_start', True)
        self.settings = kwargs
        # We only need one encoder to keep settings
        self._file_encoder = YAMLEncoder(**self.settings)

    # TODO Is there a simple / cleaner magic method (getattr ? getitem ?) to do this ?
    # we also dont want to be confused with the entries indexing if it makes things not obvious somehow...
    def sub(self, relpath):
        newdir = os.path.join(self._path, relpath)
        # direct controlled creation
        os.makedirs(newdir)
        return YAMLHierarchyEncoder()



    def _clean_missing(self, data):
        # remove unexisting keys mercilessly
        for d in os.listdir(self._path):
            if d not in data:
                os.remove(os.path.join(self._path, d))

    def dump(self, data):
        """
        Dumping data into a path (file or directory). Direct control flow.
        :param data : the data
        :return: TODO
        """
        self._clean_missing(data)

        returned_data = {}

        for k, v in data.items():
            if k == self._filekey and isinstance(v, collections.Mapping):
                # filekey is skipped here,
                # so it should be explicit enough for a user viewing the file hierarchy...
                encoded_v = {}
                for kk, vv in v.items():
                    with open(os.path.join(self._path, kk), "w", encoding='utf8') as fh:
                        encoded_v[kk] = self._file_encoder.dump(vv, fh)
            else:
                if not isinstance(v, collections.Mapping):
                    with open(os.path.join(self._path, k), "w", encoding='utf8') as fh:
                        encoded_v = self._file_encoder.dump(v, fh)
                else:
                    # recurse (keeping one instance per directory)
                    # TODO : loop to avoid recreating instance of hierarchy encoder
                    newdir = os.path.join(self._path, k)
                    os.makedirs(newdir)
                    encoded_v = YAMLHierarchyEncoder(newdir, filekey=self._filekey, **self.settings).dump(v)
            returned_data.update({k: encoded_v})

        # => what should we return ???
        # TODO : check monads and effect theory...
        return returned_data

    def future_dump():



class YAMLDecoder(object):
    """YAML Decoder, decoupling the object instance and the side effect, for cleaner composition."""
    def __init__(self, **kwargs):
        self.settings = kwargs

    def load(self, stream=None):
        return yaml.load(stream, **self.settings)

    def future_load(self, stream):
        """Dump data into a file asynchronously (lazy)
        """
        return executor.submit(self.load, stream)


class YAMLHierarchyDecoder(object):
    """
    A decoder that retrieve a mapping from a folder/files hierarchy
    """
    def __init__(self, path, filekey, **kwargs):
        self._filekey = filekey
        self._path = path
        self.settings = kwargs
        self._file_decoder = YAMLDecoder(**self.settings)

    def load(self):
        """
        Loading mapping data from a path hierarchy. Direct lazy control flow.
        :return:
        """
        if os.path.isfile(self._path):
            with open(self._path, "r") as fh:  # maybe unneeded (already in yaml pkg) ?
                data = self._file_decoder.future_load(fh)
        elif os.path.isdir(self._path):
            # recurse (keeping one instance per directory)
            pathlist = os.listdir(self._path)
            data = {p: YAMLHierarchyDecoder(os.path.join(self._path, p), self._filekey, **self.settings).load() for p in pathlist}
        else:
            # Something not a file and not a dir ?
            return NotImplementedError

        return data

# TODO : JSON ?
