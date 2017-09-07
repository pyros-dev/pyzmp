from __future__ import absolute_import, division, print_function

import unittest

import os

import errno
import pytest
import time
import yaml

from pyzmp.registry._fswatcher import UniqueFilePath, WatchedFile, FileEventHandler, FileWatcher


def test_uniquefilepath_symlink_equal(tmpdir):
    test_dir = tmpdir.join('test_dir')
    test_dir.mkdir()

    sym_dir = tmpdir.join('symdir_dir')
    sym_dir.mksymlinkto(test_dir)

    # verifying they are considered equal
    fp1 = UniqueFilePath(str(test_dir))
    fp2 = UniqueFilePath(str(sym_dir))
    assert fp1 == fp2

    # verifying they are considered the same element.
    settest = set()
    settest.add(fp1)
    settest.add(fp2)
    assert len(settest) == 1


@pytest.fixture
def watched_directory(tmpdir):
    tmpdir.chdir()
    # somehow we cannot create multiple nested folders here...
    watched_path = tmpdir.join('watched_directory')
    watched_path.mkdir()
    return FileEventHandler(str(watched_path))


def test_handler_watched_create_dir(watched_directory):

    # hack for py2 (py3 has actual nonlocal statement)
    class Nonlocal:
        pass

    Nonlocal.creation_detected = False

    def created():
        Nonlocal.creation_detected = True

    #wp = os.path.join(watched_directory.base_path, "watched_subdir")
    #entry_path.write("{'answer': 42}")

    wd = watched_directory.watch('watched_subdir', on_created=created)

    assert Nonlocal.creation_detected is False

    with FileWatcher(watched_directory):
        # actually forcing creation (tmpdir is lazy)
        os.makedirs(wd.filepath)

        now = time.time()
        while time.time() - now < 300:
            if Nonlocal.creation_detected:
                break

        assert Nonlocal.creation_detected
#
#
# def test_handler_watched_create_file(entry_factory):
#
#     # hack for py2 (py3 has actual nonlocal statement)
#     class Nonlocal:
#         pass
#
#     Nonlocal.creation_detected = False
#
#     def created():
#         Nonlocal.creation_detected = True
#
#     entry = entry_factory.watch('test_create_file', on_created=created)
#
#     p = os.path.join(entry_factory.path, 'test_create_file')
#     assert Nonlocal.creation_detected is False
#
#     print(entry.filepath)
#     with open(entry.filepath, 'a'):
#         os.utime(entry.filepath, None)
#
#     now = time.time()
#     while time.time() - now < 300:
#         if Nonlocal.creation_detected:
#             break
#
#     assert Nonlocal.creation_detected



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
