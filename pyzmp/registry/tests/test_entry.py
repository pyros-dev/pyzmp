from __future__ import absolute_import, division, print_function

import unittest

import os

import errno
import pytest
import time
import yaml

from pyzmp.registry._entry import ROEntry, RWEntry, ROFileEntry, RWFileEntry, EntryFactory, EntryWatcher


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
        # we define it to avoid raising NotImplementedError
        def fakedump(self, remove=False):
            pass
        RWEntry.filedump = fakedump
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
    # somehow we cannot create multiple nested folders here...
    entry_path = tmpdir.join('domain_host')
    # actually forcing directory creation (tmpdir is lazy)
    entry_path.mkdir()
    return EntryFactory(str(entry_path))


def test_yaml_rw_entry(entry_factory):
    # hack for py2 (py3 has actual nonlocal statement)
    class Nonlocal:
        pass

    Nonlocal.creation_detected = False
    Nonlocal.move_detected = False
    Nonlocal.modification_detected = False
    Nonlocal.deletion_detected = False

    def created():
        Nonlocal.creation_detected = True

    def moved():
        Nonlocal.move_detected = True

    def modified():
        Nonlocal.modification_detected = True

    def deleted():
        Nonlocal.deletion_detected = True

    with EntryWatcher(entry_factory):

        time.sleep(1)
        
        # direct control flow
        rwentry = entry_factory.create('rw_entry.yaml', on_created=created, on_moved=moved, on_modified=modified, on_deleted=deleted)


        return

        while not Nonlocal.creation_detected:
            time.sleep(1)
        assert Nonlocal.creation_detected


        # direct control flow : modify
        rwentry['answer'] = 42


        assert rwentry['answer'] == 42
        while not Nonlocal.modification_detected:
            time.sleep(1)
        assert Nonlocal.modification_detected

        Nonlocal.modification_detected = False
        # inverted control flow : modified is conflict
        with open('rw_entry.yaml', 'w') as fh:
            yaml.dump({'answer_typo': 42}, fh)

        while not Nonlocal.modification_detected:
            time.sleep(1)
        assert Nonlocal.modification_detected
        assert rwentry.conflicts

        # it is ignored when checking the data:
        assert 'answer_typo' not in rwentry

        # Even if there was conflict we can override it
        # we are still the controller here (good or bad idea ? we could also give up and maybe suicide...)
        Nonlocal.modification_detected = False
        rwentry['another'] = 'smthg'

        while not Nonlocal.modification_detected:
            time.sleep(1)
        assert Nonlocal.modification_detected

        assert 'answer_typo' not in rwentry
        assert rwentry['answer'] == 42
        assert rwentry['another'] == 'smthg'

        # TODO move
        # TODO delete
    assert True


def yaml_ro_entry(entry_factory):
    # hack for py2 (py3 has actual nonlocal statement)
    class Nonlocal:
        pass

    Nonlocal.creation_detected = False
    Nonlocal.move_detected = False
    Nonlocal.modification_detected = False
    Nonlocal.deletion_detected = False

    def created():
        Nonlocal.creation_detected = True

    def moved():
        Nonlocal.move_detected = True

    def modified():
        Nonlocal.modification_detected = True

    def deleted():
        Nonlocal.deletion_detected = True

    ro_entry = entry_factory.expect('ro_entry.yaml')

    with open('ro_entry.yaml', 'w') as fh:
        yaml.dump({'answer': 42}, fh)

    # inverted control flow
    assert Nonlocal.creation_detected

    assert rwentry['answer'] == 42

    # direct control flow : modify
    rwentry['answer'] = 666

    assert Nonlocal.modification_detected

    # inverted control flow : modify
    with open('rw_entry.yaml', 'w') as fh:
        yaml.dump({'answer_typo': 42}, fh)

    assert Nonlocal.modification_detected
    assert rwentry.conflict

    # TODO : raise exception ?
    assert rwentry['answer_typo'] == 42


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
