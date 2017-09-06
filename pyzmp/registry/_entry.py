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

# Used to override the default tmp directory (for tests for example)
tmpdir = None


def maybe_function(fun):
    """Use to enforce lazyness"""
    return fun if callable(fun) else lambda: fun


class ROEntry(collections.Mapping):
    """
    Class abstracting the mapping (read-only) interface to an entry in the registry
    """

    def __init__(self, data_or_loader, **kwargs):
        """
        :param data_or_loader: data (iterable) to provide mapping interface for
                               or a callable that return iterable data to provide mapping interface for
        """
        self._data_loader = maybe_function(data_or_loader)

    def __getitem__(self, item):
        return self._data_loader()[item]

    def __iter__(self):
        for d in self._data_loader():
            yield d

    def __len__(self):
        return len(self._data_loader())

    # TODO : YAML display style
    def __str__(self):
        return str({n: getattr(self, n) for n in self})

    def __repr__(self):
        return str({n: getattr(self, n) for n in self})


class RWEntry(ROEntry, collections.MutableMapping):

    def __init__(self, data_or_loader, data_dumper=None, **kwargs):
        """
        :param data_or_loader: data (iterable) to provide mapping interface for
                               or a callable that return iterable data to provide mapping interface for
        :param data_dumper: callable that take a data argument to store data after modification
        """
        super(RWEntry, self).__init__(data_or_loader)
        assert callable(data_dumper) or data_dumper is None
        self._data_dumper = data_dumper

    def __setitem__(self, key, value):
        _data = self._data_loader()
        _data[key] = value
        if self._data_dumper:
            self._data_dumper(_data)

    def __delitem__(self, key):
        _data = self._data_loader()
        del _data[key]
        if self._data_dumper:
            self._data_dumper(_data)


class FileConflictDetector:
    """
    A small class to store allowed change on a filepath
    Any change signaled that was not previously granted will trigger a conflict marker.
    Since this is supposed to be used only by an Entry, we use this to reverse the control flow.
    """
    __slots__ = [
        '_moved',
        '_created',
        '_deleted',
        '_modified',
        'conflict_move',
        'conflict_create',
        'conflict_delete',
        'conflict_modify',
        'on_move',
        'on_create',
        'on_modify',
        'on_delete',
    ]

    def __init__(self, on_move=None, on_create=None, on_modify=None, on_delete=None):
        self._created = 0
        self._modified = 0
        self._moved = 0
        self._deleted = 0

        self.conflict_move = 0
        self.conflict_create = 0
        self.conflict_delete = 0
        self.conflict_modify = 0

        self.on_move = on_move
        self.on_create = on_create
        self.on_modify = on_modify
        self.on_delete = on_delete

    @property
    def conflict_detected(self):
        return self.conflict_move or self.conflict_create or self.conflict_delete or self.conflict_modify

    # direct control flow
    def grant_create(self, num=1):
        self._created += num

    def grant_modify(self, num=1):
        self._modified += num

    def grant_move(self, num=1):
        self._moved += num

    def grant_delete(self, num=1):
        self._deleted += num

    def signal_create(self):
        self.on_create()
        if self._created <= 0:
            self.conflict_create += 1
        else:
            self._created -= 1

    def signal_modify(self):
        self.on_modify()
        if self._modified <= 0:
            self.conflict_modify += 1
        else:
            self._modified -= 1

    def signal_move(self):
        self.on_move()
        if self._moved <= 0:
            self.conflict_move += 1
        else:
            self._moved -= 1

    def signal_delete(self):
        self.on_delete()
        if self._deleted <= 0:
            self.conflict_delete += 1
        else:
            self._deleted -= 1


class UniqueFilePath:
    __slots__ = [
        'filepath'
    ]

    def __init__(self, filepath, **kwargs):
        # absolute filepath, with all symlinks resolved.
        self.filepath = os.path.realpath(filepath)

    # Using filepath as hash
    def __hash__(self):
        return hash(self.filepath.encode(sys.getdefaultencoding()))

    #  for unicity checks
    def __eq__(self, other):
        return self.filepath == other.filepath


class ROFileEntry(UniqueFilePath, ROEntry):
    """
    Class representing one Read-Only entry (file) in the registry
    """
    def __init__(self, filepath, on_create=None, on_modify=None, on_delete=None, on_move=None):
        # a member to indicate if a conflict has been detected for this FileEntry
        self.conflict_guard = FileConflictDetector(on_create=on_create, on_modify=on_modify, on_delete=on_delete, on_move=on_move)

        def fileentry_loader():
            with open(self.filepath, "r") as fh:
                data = yaml.load(fh)
            return data

        super(ROFileEntry, self).__init__(filepath=filepath, data_or_loader=fileentry_loader)

    @property
    def conflict(self):
        return self.conflict_guard.conflict_detected


class RWFileEntry(UniqueFilePath, RWEntry):
    """
    Class representing one Read/Write entry (file) in the registry
    This process is supposed to be the only one allowed to create/modify/delete it.
    """
    def __init__(self, filepath, **data):  # TODO : on_create=on_create, on_modify=on_modify, on_delete=on_delete, on_move=on_move
        # a member to indicate if a conflict has been detected for this FileEntry
        self.conflict_guard = FileConflictDetector()

        def fileentry_loader():
            with open(self.filepath, "r") as fh:
                data = yaml.load(fh)
            return data

        def fileentry_dumper(data):
            with open(self.filepath, "w", encoding='utf8') as fh:
                yaml.dump(data, fh, default_flow_style=False, allow_unicode=True)

        super(RWFileEntry, self).__init__(filepath=filepath, data_or_loader=fileentry_loader, data_dumper=fileentry_dumper)

    @property
    def conflict(self):
        return self.conflict_guard.conflict_detected

    def __setitem__(self, key, value):
        #self.conflict_detector.expect_modify()
        super(RWFileEntry, self).__setitem__(key, value)

    def __delitem__(self, key):
        #self.conflict_detector.expect_modify()
        super(RWFileEntry, self).__delitem__(key)


class EntryFactory(watchdog.events.FileSystemEventHandler):
    """
    An Event Handler for a set of entries
    """
    def __init__(self, path):
        self.path = path
        self.watched = set()  # all entries we know about

        # Can also be in another class/instance
        self.observer = watchdog.observers.Observer()
        self.observer.schedule(self, path)
        self.observer.start()

    # TODO : context manager instead ?
    def __del__(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()

    # direct control flow
    def create(self, filepath):
        """
        Watching this entry means that any event that has not been granted before will trigger a conflict marker
        An entry marked with a conflict means that an unexpected event occured -> data cannot be trusted anymore.
        :param entry:
        :return:
        """
        entry = RWEntry(filepath)

        return entry

    def watch(self, filepath, on_create=None, on_delete=None, on_modify=None, on_move=None):
        """
        Watching this entry means that any event that has not been granted before will trigger a conflict marker
        An entry marked with a conflict means that an unexpected event occurred -> data cannot be trusted anymore.
        :param entry:
        :return:
        """
        entry = ROFileEntry(filepath, on_create=on_create, on_modify=on_modify, on_delete=on_delete, on_move=on_move)

        self.watched.add(entry)

        return entry

    # inverted control flow
    def on_any_event(self, event):
        print(event)

    def on_moved(self, event):
        e = get_entry(event)
        try:
            self.owned[e.path].grant_move()
        finally:  # in all cases
            try:
                self.watched[e.path].signal_move(self.conflict_marker)
            except KeyError:
                pass  # if we are not watching this path, we do not care.

    def on_create(self, event):
        e = get_entry(event)
        try:
            self.owned[e.path].grant_create()
        finally:  # in all cases
            try:
                self.watched[e.path].signal_create(self.conflict_marker)
            except KeyError:
                pass  # if we are not watching this path, we do not care.

    def on_deleted(self, event):
        e = get_entry(event)
        try:
            self.owned[e.path].grant_deleted()
        finally:  # in all cases
            try:
                self.watched[e.path].signal_deleted(self.conflict_marker)
            except KeyError:
                pass  # if we are not watching this path, we do not care.

    def on_modified(self, event):
        e = get_entry(event)
        try:
            self.owned[e.path].grant_modify()
        finally:  # in all cases
            try:
                self.watched[e.path].signal_modify(self.conflict_marker)
            except KeyError:
                pass  # if we are not watching this path, we do not care.
