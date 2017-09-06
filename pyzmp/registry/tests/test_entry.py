from __future__ import absolute_import, division, print_function

import unittest

import os

import errno
import pytest
import time
import yaml

from pyzmp.registry._entry import ROEntry, RWEntry, ROFileEntry, RWFileEntry, EntryFactory


class TestROEntry(unittest.TestCase):
    """
    Simple classical unittest test case of ROEntry
    """
    def setUp(self):
        self.entry = ROEntry({'key': 'value'})

    def test_len(self):
        assert len(self.entry) == 1

    def test_iter(self):
        assert 'key' in self.entry

    def test_getitem(self):
        assert self.entry['key'] == 'value'

    def test_setitem(self):
        with self.assertRaises(TypeError):
            self.entry['key'] = 'override'

    def test_delitem(self):
        with self.assertRaises(TypeError):
            del self.entry['key']


class TestRWEntry(unittest.TestCase):
    """
    Simple classical unittest test case of RWEntry
    """
    def setUp(self):
        self.entry = RWEntry({'key': 'value'})

    def test_len(self):
        assert len(self.entry) == 1

    def test_iter(self):
        assert 'key' in self.entry

    def test_getitem(self):
        assert self.entry['key'] == 'value'

    def test_setitem(self):
        self.entry['key'] = 'override'
        assert self.entry['key'] == 'override'

    def test_delitem(self):
        del self.entry['key']
        assert 'key' not in self.entry


@pytest.fixture
def entry_factory(tmpdir):
    tmpdir.chdir()
    entry_path = tmpdir.mkdir(*(reversed('host.domain'.split('.'))))
    return EntryFactory(str(entry_path))


def test_handler_watched_create(entry_factory):

    creation_detected = False
    def created():
        creation_detected = True

    entry = entry_factory.watch('test_create_path', on_create=created)

    p = os.path.join(entry_factory.path, 'test_create_path')
    assert creation_detected is False

    os.makedirs(entry.filepath)

    now = time.time()
    while time.time() - now < 5:
        if creation_detected:
            break

    assert creation_detected




# def test_handler_delete():
#     pass
#
# def test_handler_move():
#     pass
#
# def test_handler_modify():
#     pass
#
#
# def test_handler_create_conflict():
#     pass
#
# def test_handler_delete_conflict():
#     pass
#
# def test_handler_move_conflict():
#     pass
#
# def test_handler_modify_conflict():
#     pass
#
#
# @pytest.fixture
# def ro_fileentry(fileentry):
#     import yaml
#     # we need some data in there...
#     fileentry.write(yaml.dump(
#         {'answer': 42},
#         explicit_start=True,
#         default_flow_style=False
#     ))
#     yield ROFileEntry(str(fileentry))
#
#
# def test_ro_fileentry_missing(tmpdir):
#     """missing file means the entry cannot be created"""
#     with pytest.raises(FileNotFoundError) as notfound:
#         ROFileEntry(str(tmpdir.join('missing-file')))
#     assert notfound.value.errno == errno.ENOENT
#
#
# def test_ro_fileentry_moved(ro_fileentry, tmpdir):
#     assert ro_fileentry['answer'] == 42
#     os.rename(ro_fileentry.filepath, str(tmpdir.join('moved_entry')))
#     assert ro_fileentry['answer'] == 42

# def test_ro_fileentry_removed(ro_fileentry):
#     pass
#
# def test_ro_fileentry_modified(ro_fileentry):
#     pass
#
# def test_ro_fileentry_len(ro_fileentry):
#     assert len(self.entry) == 1
#
# def test_iter(self):
#     assert 'key' in self.entry
#
# def test_getitem(self):
#     assert self.entry['key'] == 'value'
#
# def test_setitem(self):
#     with self.assertRaises(TypeError):
#         self.entry['key'] = 'override'
#
# def test_delitem(self):
#     with self.assertRaises(TypeError):
#         del self.entry['key']

@pytest.fixture
def rw_fileentry(fileentry):
    return RWFileEntry(fileentry)

# class TestEntry(object):
#
#
#     def test_entry_write(self):
#
#
#     def test_store_erase(self, tmpdir):
#
#         answer_reg = FileBasedRegistry("myentry", regdir=tmpdir)
#
#         with pytest.raises(KeyError) as e_info:
#             answer_reg["myanswer"]
#
#             answer_reg.expose("myanswer", 42)
#
#         assert answer_reg["myanswer"] == 42
#
#         answer_reg.conceal("myanswer")
#
#         with pytest.raises(KeyError) as e_info:
#             answer_reg["myanswer"]
#
#     def test_access(self, tmpdir):
#         # testing discovery from the same process
#         # : testing from different process (more complex test setup)
#         entry_reg = FileBasedRegistry("myentry", regdir=tmpdir)
#
#         entry2_reg = FileBasedRegistry("myentry2", regdir=tmpdir)
#
#         entry_reg.expose("mydataA", {'key': 'value'})
#
#         d = entry2_reg.discover("myentry").get("mydataA")
#
#         assert d == {'key': 'value'}



if __name__ == '__main__':
    pytest.main(['-s', '-x', __file__])
