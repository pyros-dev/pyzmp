from __future__ import absolute_import, division, print_function

import unittest

import os

import errno
import pytest
import time
import yaml

from pyzmp.registry._codec import YAMLHierarchyEncoder, YAMLHierarchyDecoder

@pytest.fixture
def hierarchy_data():
    # TODO : hypothesis testing here ??
    return {
        'the': {
            'hierarchical': {
                'data': ['the', 'answer']
            },
            'nested': {
                'other': {
                    'dataset': {
                        'answer': 42
                    }
                }
            }
        }
    }


def test_hierarchy_encoder(hierarchy_data, tmpdir):

    encoder = YAMLHierarchyEncoder()

    encoder.dump(hierarchy_data, str(tmpdir), filekey='nested')

    # asserting the dumped hierarchy
    assert ['the'] == os.listdir(str(tmpdir))
    # note how 'nested' is skipped
    assert ['hierarchical', 'other'] == os.listdir(os.path.join(str(tmpdir), 'the'))
    # verifyind hierarchical data as directory
    assert ['data'] == os.listdir(os.path.join(str(tmpdir), 'the', 'hierarchical'))
    # verifying last level as file
    assert os.path.isfile(os.path.join(str(tmpdir), 'the', 'hierarchical', 'data'))
    # verifying list stored as file lines
    with open(os.path.join(str(tmpdir), 'the', 'hierarchical', 'data'), 'r') as fh:
        assert fh.readlines() == [
            '---' + os.linesep,
            '- the' + os.linesep,
            '- answer' + os.linesep,
        ]
    # verifying complete mapping in yaml file
    with open(os.path.join(str(tmpdir), 'the', 'other'), 'r') as fh:
        assert fh.readlines() == [
            '---' + os.linesep,
            'dataset:' + os.linesep,
            '  answer: 42' + os.linesep,
        ]


# @pytest.fixture
# def hierarchy_path(tmpdir):
#     pass
#
# def test_hierarchy_decoder(hierarchy_path):
#     pass
#
#
#
# def test_hierarchy_codec(hierarchy_data, tmpdir):
#     pass