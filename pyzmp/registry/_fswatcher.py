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

"""
Module containing classes to be notified of file system events
And plug some custom behavior on any filepath, on any event. 
"""


class UniqueFilePath:
    __slots__ = [
        'filepath',
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


class WatchedFile(UniqueFilePath):

    def __init__(self, filepath, on_created=None, on_modified=None, on_moved=None, on_deleted=None):

        super(WatchedFile, self).__init__(
            filepath=filepath,  # unique
        )

        if on_created:
            self.on_instance_created = on_created

        if on_modified:
            self.on_instance_modified = on_modified

        if on_moved:
            self.on_instance_moved = on_moved

        if on_deleted:
            self.on_instance_deleted = on_deleted

    def __del__(self):
        self.on_instance_created = None
        self.on_instance_modified = None
        self.on_instance_moved = None
        self.on_instance_deleted = None

    def on_created(self):
        if callable(self.on_instance_created):
            self.on_instance_created()
        else:
            pass

    def on_modified(self):
        if callable(self.on_instance_modified):
            self.on_instance_modified()
        else:
            pass

    def on_moved(self):
        if callable(self.on_instance_moved):
            self.on_instance_moved()
        else:
            pass

    def on_deleted(self):
        if callable(self.on_instance_deleted):
            self.on_instance_deleted()
        else:
            pass

# TODO class Owned File ??????


class FileEventHandler(watchdog.events.FileSystemEventHandler):

    def __init__(self, base_path):
        # base path must exist before we can handle events on it
        assert os.path.isdir(base_path)
        self.base_path = base_path
        self.watched = {}

    def watch(self, relpath, on_created=None, on_deleted=None, on_modified=None, on_moved=None):
        """
        """
        resolved = os.path.join(self.base_path, relpath)
        self.watched[relpath] = WatchedFile(
            filepath=os.path.realpath(resolved),
            on_created=on_created,
            on_modified=on_modified,
            on_deleted=on_deleted,
            on_moved=on_moved
        )

        return self.watched[relpath]

    # inverted control flow
    def on_any_event(self, event):
        print(event)

    def on_moved(self, event):
        # TODO : check for ambiguity (symlinks ?)
        relpath = os.path.relpath(event.src_path, self.base_path)
        e = self.watched.get(relpath)
        if e is not None:
            e.on_moved()

    def on_created(self, event):
        # TODO : check for ambiguity (symlinks ?)
        relpath = os.path.relpath(event.src_path, self.base_path)
        e = self.watched.get(relpath)
        if e is not None:
            e.on_created()

    def on_deleted(self, event):
        # TODO : check for ambiguity (symlinks ?)
        relpath = os.path.relpath(event.src_path, self.base_path)
        e = self.watched.get(relpath)
        if e is not None:
            e.on_deleted()

    def on_modified(self, event):
        """ triggered when the current directory is modified """
        # TODO : check for ambiguity (symlinks ?)
        relpath = os.path.relpath(event.src_path, self.base_path)
        e = self.watched.get(relpath)
        if e is not None:
            e.on_modified()


class FileWatcher(object):

    def __init__(self, *handlers):
        self.handlers = handlers

        self.observer = watchdog.observers.Observer()
        for h in self.handlers:
            self.observer.schedule(h, h.base_path, recursive=True)

    def __enter__(self):
        self.observer.start()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.observer.stop()
        self.observer.join()
        assert not self.observer.is_alive()



