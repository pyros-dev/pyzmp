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

from ._codec import YAMLHierarchyDecoder, YAMLHierarchyEncoder
"""
Module containing classes to be notified of file system events
And plug some custom behavior on any filepath, on any event. 
"""


class UniqueFilePath:
    """
    Represents a resolved filepath, and implements unicity check for it.
    """
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
    """
    Represents a file that we are currently "watching"
    We are notified of events happening to it, and can react to it.
    Also has a decoder member to be able to load the file content on-demand (or on callback)
    """
    __slots__ = [
        'decoder',
        'filekey',
        'on_instance_created',
        'on_instance_modified',
        'on_instance_moved',
        'on_instance_deleted',
    ]

    def __init__(self, hier_decoder, filekey, on_created=None, on_modified=None, on_moved=None, on_deleted=None):

        assert isinstance(hier_decoder, (YAMLHierarchyDecoder,))  # we can add other accepted decoders here...

        # Decoder instance to be able to translate file content into entry content
        self.decoder = hier_decoder

        super(WatchedFile, self).__init__(
            filepath=self.decoder._path,  # unique
        )

        self.filekey = filekey

        if on_created:
            self.on_instance_created = on_created

        if on_modified:
            self.on_instance_modified = on_modified

        if on_moved:
            self.on_instance_moved = on_moved

        if on_deleted:
            self.on_instance_deleted = on_deleted

    # direct control flow
    def load(self):
        return self.decoder.load(filekey=self.filekey)

    # inverted control flow
    def on_created(self):
        data = self.decoder.load(filekey=self.filekey)
        if callable(self.on_instance_created):
            self.on_instance_created(data)
        return data

    def on_modified(self):
        data = self.decoder.load(filekey=self.filekey)
        if callable(self.on_instance_modified):
            self.on_instance_modified(data)
        return data

    def on_moved(self):
        raise NotImplementedError
        # unexpected : should never be moved
        self.conflict = True
        if callable(self.on_instance_moved):
            self.on_instance_moved()
        else:
            pass

    def on_deleted(self):
        data = None   # or {} ??
        if callable(self.on_instance_deleted):
            self.on_instance_deleted()
        return data


class OwnedFileConflict(Exception):
    """
    Represents an exception for when the OwnedFile got modified but not by the current process...
    """
    pass


class OwnedFile(WatchedFile):
    """
    Class representing one Read/Write entry (file) in the registry
    The current process is supposed to be the only one allowed to create/modify/delete it.
    So we keep track of expected and unexpected events.
    """
    __slots__ = [
        'encoder',
        'unexpected_create',
        'unexpected_modify',
        'unexpected_move',
        'unexpected_delete',
        'expected_create',
        'expected_modify',
        'expected_move',
        'expected_delete',
    ]

    def __init__(self, hier_decoder, hier_encoder, on_created=None, on_modified=None, on_moved=None,
                 on_deleted=None):  # TODO : on_create=on_create, on_modify=on_modify, on_delete=on_delete, on_move=on_move

        super(OwnedFile, self).__init__(
            hier_decoder=hier_decoder,
            on_created=on_created, on_modified=on_modified, on_moved=on_moved, on_deleted=on_deleted
        )

        assert isinstance(hier_encoder, (YAMLHierarchyEncoder,))  # we can add other accepted encoders here...

        # Encoder instance to be able to translate entry content into file content
        self.encoder = hier_encoder

        # a member to indicate if a conflict has been detected for this FileEntry
        self.unexpected_create = 0
        self.unexpected_modify = 0
        self.unexpected_move = 0
        self.unexpected_delete = 0

        # expecting one create event if the path does not exist yet
        self.expected_create = 1 if not os.path.exists(self.encoder._path) else 0
        self.expected_modify = 0
        self.expected_move = 0
        self.expected_delete = 0

    # direct control flow
    def dump(self, data, filekey):
        # TODO : expect modification here ?
        # what should we return here ?
        return self.encoder.dump(data=data)

    # inverted control flow
    def on_created(self):
        self.expected_create -= 1
        if self.expected_create < 0:
            self.unexpected_create += 1
        super(OwnedFile, self).on_created()

    def on_modified(self):
        self.expected_modify -= 1
        if self.expected_modify < 0:
            self.unexpected_modify += 1
        super(OwnedFile, self).on_modified()

    def on_moved(self):
        self.expected_move -= 1
        if self.expected_move < 0:
            self.unexpected_move += 1
        super(OwnedFile, self).on_moved()

    def on_deleted(self):
        self.expected_delete -= 1
        if self.expected_delete < 0:
            self.unexpected_delete += 1
        super(OwnedFile, self).on_deleted()


class FileHierarchyWatcher(watchdog.events.FileSystemEventHandler):

    def __init__(self, hier_decoder):
        """
        Handles Events on a File Hierarchy
        :param hierarchy_decoder: the decoder to be used when a watched file is modified,
        to update its data loaded in memory.
        """
        # base path must exist before we can handle events on it
        assert os.path.isdir(base_path)
        self.base_path = base_path
        self.watched = {}
        self.hier_decoder = hier_decoder

        #: managing our own observer instance
        self.observer = watchdog.observers.Observer()
        self.observer.schedule(self, self.hier_decoder._path, recursive=True)

    # usable as a context manager
    def __enter__(self):
        self.observer.start()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.observer.stop()
        self.observer.join()
        assert not self.observer.is_alive()

    def watch(self, relpath, on_created=None, on_deleted=None, on_modified=None, on_moved=None):
        """
        """
        resolved = os.path.join(self.base_path, relpath)
        self.watched[relpath] = WatchedFile(
            hier_decoder=YAMLHierarchyDecoder(path=os.path.realpath(resolved)),
            on_created=on_created,
            on_modified=on_modified,
            on_deleted=on_deleted,
            on_moved=on_moved
        )

        return self.watched[relpath]

    def create_and_watch(self, relpath, on_created=None, on_deleted=None, on_modified=None, on_moved=None):
        resolved = os.path.join(self.base_path, relpath)
        self.watched[relpath] = OwnedFile(
            hier_decoder=YAMLHierarchyDecoder(path=os.path.realpath(resolved)),
            hier_encoder=YAMLHierarchyEncoder(path=os.path.realpath(resolved)),
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




