from __future__ import absolute_import, division, print_function

import pytest

from pyzmp.registry import FileBasedRegistry

# Testing operation combinations that make sense


class TestFileBasedRegistry(object):

    def test_store_erase(self, tmpdir):

        answer_reg = FileBasedRegistry("myentry", regdir=tmpdir)

        with pytest.raises(KeyError) as e_info:
            answer_reg["myanswer"]

            answer_reg.expose("myanswer", 42)

        assert answer_reg["myanswer"] == 42

        answer_reg.conceal("myanswer")

        with pytest.raises(KeyError) as e_info:
            answer_reg["myanswer"]

    def test_access(self, tmpdir):
        # testing discovery from the same process
        # : testing from different process (more complex test setup)
        entry_reg = FileBasedRegistry("myentry", regdir=tmpdir)

        entry2_reg = FileBasedRegistry("myentry2", regdir=tmpdir)

        entry_reg.expose("mydataA", {'key': 'value'})

        d = entry2_reg.discover("myentry").get("mydataA")

        assert d == {'key': 'value'}



#TODO : test read only

if __name__ == '__main__':
    pytest.main(['-s', '-x', __file__])
