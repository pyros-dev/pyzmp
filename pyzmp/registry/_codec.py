from __future__ import absolute_import, division, print_function

import collections
from io import open

import os
import yaml

"""
Module allowing to GRAFT folder hierarchy with files mapping trees
"""


def depth(d, level=1):
    if not isinstance(d, dict) or not d:
        return level
    return max(depth(d[k], level + 1) for k in d)


class YAMLHierarchyEncoder(object):
    """
    An encoder that stores a mapping as a folder/files hierarchy
    """
    def __init__(self):
        pass

    def dump(self, data, path, filekey='file', **kwargs):
        """
        Dumping data into a path (file or directory)
        :param data : the data
        :param path : the path to save the data in
        :param filekey: the key indicating the mapping should be a set of files, instead of a directory hierarchy.
        Any higher level key will be represented as a directory, potentially containing other directories.
        :param kwargs: extra args
        :return:
        """
        # enforcing some useful defaults
        kwargs.setdefault('default_flow_style', False)
        kwargs.setdefault('allow_unicode', True)
        kwargs.setdefault('explicit_start', True)

        # remove unexisting keys mercilessly
        for d in os.listdir(path):
            if d not in data:
                os.remove(os.path.join(path, d))

        for k, v in data.items():
            if k == filekey and isinstance(v, collections.Mapping):
                # filekey is skipped here,
                # so it should be explicit enough for a user viewing the file hierarchy...
                for kk, vv in v.items():
                    self.dumpfile(vv, os.path.join(path, kk), **kwargs)
            else:
                if not isinstance(v, collections.Mapping):
                    self.dumpfile(v, os.path.join(path, k), **kwargs)
                else:
                    # recurse
                    newdir = os.path.join(path, k)
                    os.makedirs(newdir)
                    self.dump(v, newdir, filekey=filekey, **kwargs)

    def dumpfile(self, data, filepath, **kwargs):
        with open(filepath, "w", encoding='utf8') as fh:
            yaml.dump(data, fh, **kwargs)


class YAMLHierarchyDecoder(object):
    """
    A decoder that retrieve a mapping from a folder/files hierarchy
    """
    def __init__(self):
        super(YAMLHierarchyDecoder, self).__init__()

    def load(self, path, filekey='file', **kwargs):
        """
        Loading mapping data from a path hierarchy
        :param path: the path
        :param filekey: the key to be added to indicate file transition
        :param kwargs: extra args
        :return:
        """
        if os.path.isfile(path):
            return {filekey: self.loadfile(path, **kwargs)}
        elif os.path.isdir(path):
            # recurse
            pathlist = os.listdir(path)
            return {p: self.load(os.path.join(path, p), **kwargs) for p in pathlist}
        else:
            # Same behavior as when trying to access a non existing key in a dictionary
            return KeyError(path)

    def loadfile(self, filepath, **kwargs):
        with open(filepath, "r") as fh:
           return yaml.load(fh, **kwargs)



# TODO : JSON ?
