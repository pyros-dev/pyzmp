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

from ._fswatcher import WatchedFile, FileEventHandler, FileWatcher

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

    def __init__(self, data):
        """
        :param data: data (iterable) to provide mapping interface for
        :param kwargs: making multiple inheritance simple
        """
        self._data = data

    def fileload(self):
        raise NotImplementedError

    def __getitem__(self, item):
        return self._data[item]

    def __iter__(self):
        for d in self._data:
            yield d

    def __len__(self):
        return len(self._data)

    # TODO : YAML display style
    def __str__(self):
        return str({n: getattr(self, n) for n in self})

    def __repr__(self):
        return str({n: getattr(self, n) for n in self})


class RWEntry(ROEntry, collections.MutableMapping):

    def __init__(self, data):
        """
        :param data: data (iterable) to provide mapping interface for
        :param kwargs: making multiple inheritance simple
        """
        super(RWEntry, self).__init__(data)
        # to force file creation asap (direct control flow)
        self.filedump()

    def __del__(self):
        # to force file deletion
        self.filedump(remove=True)

    def filedump(self, remove=False):
        raise NotImplementedError

    def __setitem__(self, key, value):
        self._data[key] = value
        self.filedump()

    def __delitem__(self, key):
        del self._data[key]
        self.filedump()


class ROFileEntry(WatchedFile, ROEntry):
    """
    Class representing one Read-Only entry (file) in the registry
    """
    def __init__(self, filepath, on_created=None, on_modified=None, on_moved=None, on_deleted=None):
        # a member to indicate if a conflict has been detected for this FileEntry
        self.conflict = False

        # We dont use super, since we need to init multiple base classes
        WatchedFile.__init__(
            self,
            filepath=filepath,
            on_created=on_created, on_modified=on_modified, on_moved=on_moved, on_deleted=on_deleted
        )
        ROEntry.__init__(
            self,
            data={}
        )

    def fileload(self):
        # Also supporting the directory case somehow... maybe not a good idea ?
        if os.path.isfile(self.filepath):
                with open(self.filepath, "r") as fh:
                    self._data = yaml.load(fh)
        elif os.path.isdir(self.filepath):
            self._data[os.path.basename(self.filepath)] = {}
        else:
            # not changing anything
            raise NotImplementedError  # does this actually happens ?

    def on_created(self):
        self.fileload()
        super(ROFileEntry, self).on_created()

    def on_modified(self):
        self.fileload()
        super(ROFileEntry, self).on_modified()

    def on_moved(self):
        # unexpected : should never be moved
        self.conflict = True
        super(ROFileEntry, self).on_moved()

    def on_deleted(self):
        self._data = {}
        super(ROFileEntry, self).on_deleted()

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


class RWFileEntry(WatchedFile, RWEntry):
    """
    Class representing one Read/Write entry (file) in the registry
    The current process is supposed to be the only one allowed to create/modify/delete it.
    """
    def __init__(self, filepath, on_created=None, on_modified=None, on_moved=None, on_deleted=None):  # TODO : on_create=on_create, on_modify=on_modify, on_delete=on_delete, on_move=on_move
        # a member to indicate if a conflict has been detected for this FileEntry
        self.unexpected_create = 0
        self.unexpected_modify = 0
        self.unexpected_move = 0
        self.unexpected_delete = 0

        self.expected_create = 0
        self.expected_modify = 0
        self.expected_move = 0
        self.expected_delete = 0

        # : the number of conflicts last time we overwrote the data
        # So we should be safe to go after that if the number of conflict doesnt increase
        self.last_conflicts = 0

        # We don't use super, since we need to init multiple base classes
        WatchedFile.__init__(
            self,
            filepath=filepath,
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
        WatchedFile.__del__(self)

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
        super(RWFileEntry, self).__setitem__(key, value)

    def __delitem__(self, key):
        self.expected_modify += 1
        super(RWFileEntry, self).__delitem__(key)

    def on_created(self):
        self.expected_create -= 1
        if self.expected_create < 0:
            self.unexpected_create += 1
        super(RWFileEntry, self).on_created()

    def on_modified(self):
        self.expected_modify -= 1
        if self.expected_modify < 0:
            self.unexpected_modify += 1
        super(RWFileEntry, self).on_modified()

    def on_moved(self):
        self.expected_move -= 1
        if self.expected_move < 0:
            self.unexpected_move += 1
        super(RWFileEntry, self).on_moved()

    def on_deleted(self):
        self.expected_delete -= 1
        if self.expected_delete < 0:
            self.unexpected_delete += 1
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
    def __init__(self, path):
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
            filepath=os.path.realpath(resolved),
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
            filepath=os.path.realpath(resolved),
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
