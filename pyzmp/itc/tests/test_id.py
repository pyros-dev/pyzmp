from __future__ import absolute_import, division, print_function, unicode_literals

import copy

import pyzmp.itc.id as id

import pytest


def test_init():
    i = id.IdLeaf()
    assert i.value == 1 and i.isLeaf

    j = id.IdLeaf(0)

    node = id.IdNode(i, j)
    assert node.left == i and node.right == j and not node.isLeaf


def test_eq():
    """Test that the equality depends on the value tree only"""
    i1 = id.IdLeaf()
    i2 = id.IdLeaf()

    assert i1 == i2

    i1 = id.IdLeaf()
    i2 = id.IdLeaf(0)

    assert i1 != i2

    i3 = id.IdLeaf()
    i2 = id.IdNode(i3, id.IdLeaf())

    assert i1 != i2

    i1 = id.IdNode(i3, id.IdLeaf())

    assert i1 == i2


def test_copy():
    i0 = id.IdLeaf()
    i1 = id.IdLeaf(1)

    i2 = copy.copy(i0)
    assert i2.value == i0.value

    i2 = copy.copy(i1)
    assert i2.value == i1.value

    i3 = id.IdNode(i0, i1)

    i4 = copy.copy(i3)
    # values in subtrees are equal
    assert i4.left.value == i0.value
    assert i4.right.value == i1.value

    # therefore subtrees are also equal
    assert i4.left == i0
    assert i4.right == i1


def test_normalize():
    # we should normalize to 0
    i1 = id.IdNode(id.IdLeaf(0), id.IdLeaf(0))
    i1 = i1.normalize()
    assert i1.isLeaf and i1.value == 0

    # we should normalize to 1
    i2 = id.IdNode(id.IdLeaf(1), id.IdLeaf(1))
    i2 = i2.normalize()
    assert i2.isLeaf and i2.value == 1

    # we cannot normalize
    i3 = id.IdNode(id.IdLeaf(0), id.IdLeaf(1))
    i3 = i3.normalize()
    assert not i3.isLeaf

    i4 = id.IdNode(id.IdLeaf(1), id.IdLeaf(0))
    i4 = i4.normalize()
    assert not i4.isLeaf



def test_split():
    i1 = id.Id(0)
    assert i1.split() == id.IdNode(id.idLeaf(0), id.IdLeaf(0))

    i1 = id.Id(1)
    assert i1.split() == id.IdNode(id.IdNode(id.idLeaf(1), id.IdLeaf(0)), id.IdNode(id.idLeaf(0), id.IdLeaf(1)))




    i2 = id.Id(42)
    i2.left = id.Id(2)

    assert i2.split() == i


def test_sum():
    ia = id.IdLeaf(1)
    ib = id.IdLeaf(0)


if __name__ == '__main__':
    pytest.main(['-s', '-x', __file__])
