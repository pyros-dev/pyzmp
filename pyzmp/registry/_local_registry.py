from __future__ import absolute_import, division, print_function

import contextlib
import logging
from io import open

import os
import tempfile
import abc
import watchdog.events
import collections
import yaml
import errno

# Used to override the default tmp directory (for tests for example)
tmpdir = None

from ._entry import ROFileEntry, RWFileEntry, EntryFactory


# TODO : Global registry with namedtuples ? CRDT ?
class FileBasedLocalRegistry(collections.MutableMapping):
    """
    A multiprocess registry
    """

    @classmethod
    def _filepath2name_gen(cls, domain_name, regdir=None):
        """
        A deterministic way to find registry files from the domain_name and a path, so it can be used in any context.
        :param domain_name: the domain name, used as extension for all registry files.
        :param regdir: regdir should be a folder that exists on all platform where zmp is used
        :return:
        """
        for f in os.listdir(regdir):
            if f.endswith(os.extsep + domain_name):
                yield os.path.basename(f)[:-len(os.extsep + domain_name)]

    @classmethod
    def _name2filepath(cls, name, domain_name, regdir=None):
        """
        A deterministic way to generate the filepath from a name and a domain_name, so it can be used in any context.
        :param name: the basename of the file
        :param domain_name: the domain name, used as extension for all registry files.
        :param regdir: regdir should be a folder that exists on all platform where zmp is used
        :return:
        """
        # trying to follow the de-facto standard way to register daemon process info (as "name.pid" file for example)
        fname = os.path.join(regdir, str(domain_name), str(name) + str(os.extsep) + "pid")
        return fname

    def __init__(self, regdir, fqdn, representer=None, constructor=None):
        """
        Initialize the registry
        :param domain_name: The name denoting the domain covered by this registry
        :param regdir: the directory where the registry is/will be. Needs to be a
        :param representer: The YAML representer
        :param constructor: The YAML constructor
        """

        self.representer = representer
        self.constructor = constructor

        self.fqdn = fqdn
        self.regdir = os.path.join(regdir, *reversed(self.fqdn.split('.')))

        #self.owned_entry = RWFileEntry(self._name2filepath(os.getpid(), self.domain_name, regdir=self.regdir))

        #self.entry_handler = EntryHandler(self.regdir)
        #self.entry_handler.take_ownership(self.owned_entry)

    def expose(self, **kwargs):
        """
        registering data as YAML in file, using the PID as the filename
        :param kwargs: data to register
        :return:
        """

        # self.myentry =

        attrfname = self._name2filepath(os.getpid(), self.domain_name, regdir=self.regdir)
        try:
            with open(attrfname, "w") as fh:
                # Note : we use yaml as a codec
                yaml.dump({k: v for k, v in kwargs.items()}, fh, default_flow_style=False)
        except IOError as ioe:
            if ioe.errno == errno.ENOENT:  # No such file or directory
                # TODO : handle all possible cases
                os.makedirs(os.path.dirname(attrfname))
                # now we can try again...
                with open(attrfname, "w") as fh:
                    yaml.dump({k: v for k, v in kwargs.items()}, fh, default_flow_style=False)

    def conceal(self):
        pidfname = self._name2filepath(os.getpid(), self.domain_name, regdir=self.regdir)
        os.remove(pidfname)

    @contextlib.contextmanager
    def exposed(self, **kwargs):
        # advertise itself
        self.expose(**kwargs)

        # Do not yield until we are register (otherwise noone can find us, there is no point.)
        yield

        try:
            # concealing itself
            # Note this will not be done if the process is killed or crash...
            self.conceal()
        except KeyError:
            pass  # already removed, we can ignore this

    def __getitem__(self, item):
        fname = self._name2filepath(item, self.domain_name, regdir=self.regdir)

        return ROEntry(item, registry)

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

    def __iter__(self):
        for name in self._filepath2name_gen(self.domain_name, regdir=self.regdir):

            yield name

    def __len__(self):
        return len([a for a in self._filepath2name_gen(self.domain_name, regdir=self.regdir)])

    def __str__(self):
        return str({n: getattr(self, n) for n in self})

    def __repr__(self):
        return str({n: getattr(self, n) for n in self})


