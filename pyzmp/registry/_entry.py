from __future__ import absolute_import, division, print_function

import contextlib
import hashlib
import logging
from io import open

import os
import tempfile
import abc

import sys

import time
import watchdog.events
import watchdog.observers
import collections
import yaml
import errno

from ._fswatcher import WatchedFile, OwnedFile, FileEventHandler, FileWatcher
from ._codec import YAMLDecoder, YAMLEncoder, YAMLHierarchyEncoder, YAMLHierarchyDecoder


"""
Module containing classes to aggregate information from a filesystem
into a mapping, that can be modified directly, but also get notified
of change happening underneath (not triggered by our process)...

The file content has to be a YAML mapping.
"""


# Used to override the default tmp directory (for tests for example)
tmpdir = None


def maybe_function(fun):
    """Use to enforce lazyness"""
    return fun if callable(fun) else lambda: fun


class EntryConflict(Exception):
    pass


class ROEntry(collections.Mapping):
    """
    Class abstracting the mapping (read-only) interface to an entry in the registry
    """

    def __init__(self, data=None, repr_decoder=None):
        """
        :param data: data (iterable) to provide mapping interface for (or nothing if it is to be retrieved later)
        :param repr_decoder: simple readable repr
        """
        self._data = data  # None marks a unloaded Entry
        self._repr_decoder = repr_decoder or YAMLDecoder()
        super(ROEntry, self).__init__()

    def __getitem__(self, item):
        return self._data[item]

    def __iter__(self):
        for d in self._data:
            yield d

    def __len__(self):
        return len(self._data)

    def __str__(self):
        return self._repr_decoder.load(self)

    def __repr__(self):
        return self._repr_decoder.load(self)


class RWEntry(collections.MutableMapping):
    """
    Class abstracting the mapping (mutable) interface to an entry in the registry
    We do NOT inherit from ROEntry, trying to prevent multiple inheritance diamond issues in children.
    """
    def __init__(self, data, repr_decoder=None):
        """
        :param data: data (iterable) to provide mapping interface for
        :param repr_decoder: simple readable repr
        """
        self._data = data  # enforcing data to be there from the initialization
        self._repr_decoder = repr_decoder or YAMLDecoder()
        super(RWEntry, self).__init__()

    def __getitem__(self, item):
        return self._data[item]

    def __iter__(self):
        for d in self._data:
            yield d

    def __len__(self):
        return len(self._data)

    def __str__(self):
        return self._repr_decoder.load(self)

    def __repr__(self):
        return self._repr_decoder.load(self)

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]


class ROFileEntry(WatchedFile, ROEntry):
    """
    Class representing one Read-Only entry (file) in the registry
    """
    def __init__(self, hier_decoder, on_created=None, on_modified=None, on_moved=None, on_deleted=None):

        # a member to indicate if a conflict has been detected for this FileEntry
        self.conflict = False

        # We dont use super, since we need to init multiple base classes
        WatchedFile.__init__(
            self,
            hier_decoder=hier_decoder,
            on_created=on_created, on_modified=on_modified, on_moved=on_moved, on_deleted=on_deleted
        )
        ROEntry.__init__(
            self,
            data=self.decoder.load()  # initializing data with current file content
        )

    def __getitem__(self, item):
        if self.conflict:
            raise EntryConflict()
        return super(ROFileEntry, self).__getitem__(item)

    def __iter__(self):
        if self.conflict:
            raise EntryConflict()
        yield super(ROFileEntry, self).__iter__()

    def __len__(self):
        if self.conflict:
            raise EntryConflict()
        return super(ROFileEntry, self).__len__()


class RWFileEntry(OwnedFile, RWEntry):
    """
    Class representing one Read/Write entry (file) in the registry
    The current process is supposed to be the only one allowed to create/modify/delete it.

    Note : this class cannot inherit from ROFileEntry to prevent multiple inheritance issues.
    Therefore some code is duplicated here... A 'clean' solution might be too complex for maintenance however...
    """
    def __init__(self, hier_decoder, file_encoder, on_created=None, on_modified=None, on_moved=None, on_deleted=None):

        assert isinstance(file_encoder, (YAMLHierarchyEncoder,))  # we can add other accepted encoders here...
        assert isinstance(hier_decoder, (YAMLHierarchyDecoder,))  # we can add other accepted decoders here...

        # Encoder instance to be able to translate entry content into file content
        self.encoder = file_encoder
        self.decoder = hier_decoder

        # : the number of conflicts last time we overwrote the data
        # So we should be safe to go after that if the number of conflict doesnt increase
        self.last_conflicts = 0

        # We don't use super, since we need to init multiple base classes
        OwnedFile.__init__(
            self,
            file_encoder=file_encoder,
            hier_decoder=hier_decoder,
            on_created=on_created, on_modified=on_modified, on_moved=on_moved, on_deleted=on_deleted
        )
        self.expected_create += 1
        RWEntry.__init__(
            self,
            data={}
        )

    def __del__(self):
        # preventing late conflict in case somebody checks
        self.expected_delete += 1
        RWEntry.__del__(self)
        OwnedFile.__del__(self)

    def fileload(self):
        if self.conflicts <= self.last_conflicts:
            super(RWFileEntry, self).fileload()
        else:
            raise EntryConflict("Conflict has been detected on {0}, preventing loading from file.".format(self.filepath))

    def filedump(self, remove=False):
        self.last_conflicts = self.conflicts  # memorizing the past conflicts before overriding
        if remove:
            os.remove(self.filepath)
        else:
            with open(self.filepath, "w", encoding='utf8') as fh:
                yaml.dump(self._data, fh, default_flow_style=False, allow_unicode=True)

    def __setitem__(self, key, value):
        self.expected_modify += 1
        RWEntry.__setitem__(key, value)
        self.filedump(remove=False)

    def __delitem__(self, key):
        self.expected_modify += 1
        RWEntry.__delitem__(key)
        self.filedump(remove=True)

    def on_created(self):
        super(RWFileEntry, self).on_created()
        self.fileload()

    def on_modified(self):
        super(RWFileEntry, self).on_modified()
        self.fileload()

    def on_moved(self):
        # unexpected : should never be moved
        super(RWFileEntry, self).on_moved()

    def on_deleted(self):
        super(RWFileEntry, self).on_deleted()
        # after delete we have no data available
        self._data = {}

    @property
    def conflicts(self):
        return self.unexpected_create + self.unexpected_modify + self.unexpected_move + self.unexpected_delete


class EntryFactory(FileEventHandler, FileWatcher):
    """
    An Event Handler for a set of entries
    """
    def __init__(self, path, filekey):
        #: the key that mark the transition to file storage in the mapping
        self.filekey = filekey
        super(EntryFactory, self).__init__(base_path=path)

    # direct control flow
    def create(self, relpath, on_created=None, on_deleted=None, on_modified=None, on_moved=None):
        """
        Watching this entry means that any event that has not been granted before will trigger a conflict marker
        An entry marked with a conflict means that an unexpected event occured -> data cannot be trusted anymore.
        :param entry:
        :return:
        """
        resolved = os.path.join(self.base_path, relpath)
        self.watched[relpath] = RWFileEntry(
            hier_decoder=YAMLHierarchyDecoder(resolved, filekey=self.filekey),
            file_encoder=YAMLHierarchyEncoder(resolved, filekey=self.filekey),
            on_created=on_created,
            on_modified=on_modified,
            on_deleted=on_deleted,
            on_moved=on_moved
        )

        # TODO : in fswatcher instead ???
        # enforcing direct control flow
        # This has to be outside of __init__ to be able to receive the callback...
        while self.watched[relpath].expected_create > 0:
            time.sleep(.1)

        # TODO raise exception if creation didn't happen with warning:
        # => everything is likely broken, just give up already.

        return self.watched[relpath]

    def destroy(self, relpath):
        # TODO : in fswatcher instead ???
        # explicit resource (file/entry) management
        # enforcing direct control flow
        p = self.watched[relpath]
        self.watched.pop(relpath)
        while p.expected_delete > 0:
            time.sleep(.1)

    # inverted control flow
    def expect(self, relpath, on_created=None, on_deleted=None, on_modified=None, on_moved=None):
        """
        Watching this entry means that any event that has not been granted before will trigger a conflict marker
        An entry marked with a conflict means that an unexpected event occured -> data cannot be trusted anymore.
        :param entry:
        :return:
        """
        resolved = os.path.join(self.base_path, relpath)
        self.watched[relpath] = ROFileEntry(
            hier_decoder=YAMLHierarchyDecoder(resolved, filekey=self.filekey),
            on_created=on_created,
            on_modified=on_modified,
            on_deleted=on_deleted,
            on_moved=on_moved
        )

        # indirect control flow

        return self.watched[relpath]

    def on_any_event(self, event):
        print(event)

    def on_moved(self, event):
        # TODO : check for ambiguity (symlinks ?)
        if event.src_path == self.base_path:
            # moving this directory ?!?!!?
            pass
        super(EntryFactory, self).on_moved(event)

    def on_created(self, event):
        # TODO : check for ambiguity (symlinks ?)
        if event.src_path == self.base_path:
            # creating this directory ?!?!!?
            pass
        super(EntryFactory, self).on_created(event)

    def on_deleted(self, event):
        # TODO : check for ambiguity (symlinks ?)
        if event.src_path == self.base_path:
            # deleting this directory ?!?!!?
            pass
        super(EntryFactory, self).on_deleted(event)

    def on_modified(self, event):
        # TODO : check for ambiguity (symlinks ?)
        if event.src_path == self.base_path:
            # modifying this directory ?!?!!?
            # TODO : maybe we need to handle something ?
            pass
        super(EntryFactory, self).on_modified(event)


class EntryWatcher(FileWatcher):
    pass
