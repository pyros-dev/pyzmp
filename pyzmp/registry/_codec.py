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


class YAMLEncoder(object):
    """YAML Encoder, decoupling the object instance and the side effect, for cleaner composition."""
    def __init__(self, data, filepath, **kwargs):
        self._data = data
        self._filepath = filepath
        # enforcing some useful defaults
        kwargs.setdefault('default_flow_style', False)
        kwargs.setdefault('allow_unicode', True)
        kwargs.setdefault('explicit_start', True)
        self.settings = kwargs

    def dump(self):
        with open(self._filepath, "w", encoding='utf8') as fh:  # maybe unneeded (already in yaml pkg) ?
            yaml.dump(self._data, fh, **self.settings)


class YAMLHierarchyEncoder(object):
    """
    An encoder that stores a mapping as a folder/files hierarchy
    """
    def __init__(self, data, path, filekey, **kwargs):
        self._data = data
        self._filekey = filekey
        self._path = path
        # enforcing some useful defaults
        kwargs.setdefault('default_flow_style', False)
        kwargs.setdefault('allow_unicode', True)
        kwargs.setdefault('explicit_start', True)
        self.settings = kwargs

    def dump(self, delay_file_encode=True):
        """
        Dumping data into a path (file or directory)
        :param data : the data
        :param path : the path to save the data in
        :param filekey: the key indicating the mapping should be a set of files, instead of a directory hierarchy.
        Any higher level key will be represented as a directory, potentially containing other directories.
        :param kwargs: extra args
        :return:
        """
        # remove unexisting keys mercilessly
        for d in os.listdir(self._path):
            if d not in self._data:
                os.remove(os.path.join(self._path, d))

        returned_data = {}

        for k, v in self._data.items():
            if k == self._filekey and isinstance(v, collections.Mapping):
                # filekey is skipped here,
                # so it should be explicit enough for a user viewing the file hierarchy...
                file_encoders = {kk: YAMLEncoder(vv, os.path.join(self._path, kk), **self.settings) for kk, vv in v.items()}
                # TODO : Trick here : return the partially applied encoders (before side effects)
                # or actually finish application and trigger irreversible side-effect...
                if delay_file_encode:
                    v=file_encoders
                else:
                    v={fk: fv.dump() for fk, fv in file_encoders.items()}
            else:
                if not isinstance(v, collections.Mapping):
                    file_encoders = {k: YAMLEncoder(v, os.path.join(self._path, k), **self.settings)}
                    if delay_file_encode:
                        v=file_encoders
                    else:
                        v={fk: fv.dump() for fk, fv in file_encoders.items()}
                else:
                    # recurse
                    newdir = os.path.join(self._path, k)
                    os.makedirs(newdir)
                    v={
                        k: YAMLHierarchyEncoder(v, newdir, filekey=self._filekey, **self.settings).dump(delay_file_encode=delay_file_encode)
                    }
            returned_data.update({k: v})

        # => what should we return ???
        # TODO : check monads and effect theory...
        return returned_data


class YAMLDecoder(object):
    """YAML Decoder, decoupling the object instance and the side effect, for cleaner composition."""
    def __init__(self, filepath, **kwargs):
        self._filepath = filepath
        self.settings = kwargs

    def load(self):
        with open(self._filepath, "r") as fh:  # maybe unneeded (already in yaml pkg) ?
            return yaml.load(fh, **self.settings)


class YAMLHierarchyDecoder(object):
    """
    A decoder that retrieve a mapping from a folder/files hierarchy
    """
    def __init__(self, path, filekey, **kwargs):
        self._filekey = filekey
        self._path = path
        self.settings = kwargs

    def load(self, delay_file_decode=True):
        """
        Loading mapping data from a path hierarchy
        :param path: the path
        :param filekey: the key to be added to indicate file transition
        :param kwargs: extra args
        :return:
        """
        if os.path.isfile(self._path):
            decoder = YAMLDecoder(self._path, **self.settings)
            if delay_file_decode:
                return {self._filekey: decoder}
            else:
                return {self._filekey: decoder.load()}
        elif os.path.isdir(self._path):
            # recurse
            pathlist = os.listdir(self._path)
            return {p: YAMLHierarchyDecoder(os.path.join(self._path, p), self._filekey, **self.settings).load(delay_file_decode=delay_file_decode) for p in pathlist}
        else:
            # Something not a file and not a dir ?
            return NotImplementedError


# TODO : JSON ?
