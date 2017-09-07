from __future__ import absolute_import, division, print_function

import contextlib
import hashlib
import logging
from io import open

import os
import tempfile
import abc

import sys
import watchdog.events
import watchdog.observers
import collections
import yaml
import errno

from ._fswatcher import WatchedFile

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

    def filedump(self):
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
    This process is supposed to be the only one allowed to create/modify/delete it.
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

        # We don't use super, since we need to init multiple base classes
        WatchedFile.__init__(
            self,
            filepath=filepath,
            on_created=on_created, on_modified=on_modified, on_moved=on_moved, on_deleted=on_deleted
        )
        RWEntry.__init__(
            self,
            data={}
        )

    def filedump(self):
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
        super(RWFileEntry, self).on_instance_created()

    def on_modified(self):
        self.expected_modify -= 1
        if self.expected_modify < 0:
            self.unexpected_modify += 1
        super(RWFileEntry, self).on_instance_modified()

    def on_moved(self):
        self.expected_move -= 1
        if self.expected_move < 0:
            self.unexpected_move += 1
        super(RWFileEntry, self).on_instance_moved()

    def on_deleted(self):
        self.expected_delete -= 1
        if self.expected_delete < 0:
            self.unexpected_delete += 1
        super(RWFileEntry, self).on_instance_deleted()
        # after delete we have no data available
        self._data = {}

    @property
    def conflict(self):
        return self.unexpected_create or self.unexpected_modify or self.unexpected_move or self.unexpected_delete


class EntryFactory(watchdog.events.FileSystemEventHandler):
    """
    An Event Handler for a set of entries
    """
    def __init__(self, path):
        self.path = path
        self.watched = {}  # all entries/files we know about

        # Can also be in another class/instance
        self.observer = watchdog.observers.Observer()
        self.observer.schedule(self, path, recursive=True)
        self.observer.start()

    # TODO : context manager instead ?
    def __del__(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()

    # direct control flow
    def create(self, relpath):
        """
        Watching this entry means that any event that has not been granted before will trigger a conflict marker
        An entry marked with a conflict means that an unexpected event occured -> data cannot be trusted anymore.
        :param entry:
        :return:
        """
        fullpath = os.path.join(self.path, relpath)
        entry = RWFileEntry(filepath=fullpath)

        return entry

    def watch(self, relpath, on_created=None, on_deleted=None, on_modified=None, on_moved=None):
        """
        Watching this entry means that any event that has not been granted before will trigger a conflict marker
        An entry marked with a conflict means that an unexpected event occurred -> data cannot be trusted anymore.
        :param relpath: relative path of the entry to watch
        :return:
        """
        fullpath = os.path.join(self.path, relpath)
        entry = ROFileEntry(filepath=fullpath,
                            on_created=on_created,
                            on_modified=on_modified,
                            on_deleted=on_deleted,
                            on_moved=on_moved)

        self.watched[entry.filepath] = entry

        return entry

    # inverted control flow
    def on_any_event(self, event):
        print(event)

    def on_moved(self, event):
        e = self.watched.get(event.src_path)
        if e is not None:
            e.on_moved()

    def on_created(self, event):
        e = self.watched.get(event.src_path)
        if e is not None:
            e.on_created()

    def on_deleted(self, event):
        e = self.watched.get(event.src_path)
        if e is not None:
            e.on_deleted()

    def on_modified(self, event):
        """ triggered when the current directory is modified """
        e = self.watched.get(event.src_path)
        if e is not None:
            e.on_modified()
