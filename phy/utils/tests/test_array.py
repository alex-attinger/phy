# -*- coding: utf-8 -*-

"""Tests of array utility functions."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import numpy as np
from numpy.testing import assert_array_equal as ae
from pytest import raises

from ..array import (_unique, _normalize, _index_of, _as_array, _as_tuple,
                     chunk_bounds, excerpts, data_chunk,
                     PartialArray, _partial_shape,
                     _range_from_slice)
from ...datasets.mock import artificial_spike_clusters


#------------------------------------------------------------------------------
# Test utility functions
#------------------------------------------------------------------------------

def test_range_from_slice():
    """Test '_range_from_slice'."""

    class _SliceTest(object):
        """Utility class to make it more convenient to test slice objects."""
        def __init__(self, **kwargs):
            self._kwargs = kwargs

        def __getitem__(self, item):
            if isinstance(item, slice):
                return _range_from_slice(item, **self._kwargs)

    with raises(ValueError):
        _SliceTest()[:]
    with raises(ValueError):
        _SliceTest()[1:]
    ae(_SliceTest()[:5], [0, 1, 2, 3, 4])
    ae(_SliceTest()[1:5], [1, 2, 3, 4])

    with raises(ValueError):
        _SliceTest()[::2]
    with raises(ValueError):
        _SliceTest()[1::2]
    ae(_SliceTest()[1:5:2], [1, 3])

    with raises(ValueError):
        _SliceTest(start=0)[:]
    with raises(ValueError):
        _SliceTest(start=1)[:]
    with raises(ValueError):
        _SliceTest(step=2)[:]

    ae(_SliceTest(stop=5)[:], [0, 1, 2, 3, 4])
    ae(_SliceTest(start=1, stop=5)[:], [1, 2, 3, 4])
    ae(_SliceTest(stop=5)[1:], [1, 2, 3, 4])
    ae(_SliceTest(start=1)[:5], [1, 2, 3, 4])
    ae(_SliceTest(start=1, step=2)[:5], [1, 3])
    ae(_SliceTest(start=1)[:5:2], [1, 3])

    ae(_SliceTest(length=5)[:], [0, 1, 2, 3, 4])
    with raises(ValueError):
        _SliceTest(length=5)[:3]
    ae(_SliceTest(length=5)[:10], [0, 1, 2, 3, 4])
    ae(_SliceTest(length=5)[:5], [0, 1, 2, 3, 4])
    ae(_SliceTest(start=1, length=5)[:], [1, 2, 3, 4, 5])
    ae(_SliceTest(start=1, length=5)[:6], [1, 2, 3, 4, 5])
    with raises(ValueError):
        _SliceTest(start=1, length=5)[:4]
    ae(_SliceTest(start=1, step=2, stop=5)[:], [1, 3])
    ae(_SliceTest(start=1, stop=5)[::2], [1, 3])
    ae(_SliceTest(stop=5)[1::2], [1, 3])


def test_unique():
    """Test _unique() function"""
    _unique([])

    n_spikes = 1000
    n_clusters = 10
    spike_clusters = artificial_spike_clusters(n_spikes, n_clusters)
    ae(_unique(spike_clusters), np.arange(n_clusters))


def test_normalize():
    """Test _normalize() function."""

    n_channels = 10
    positions = 1 + 2 * np.random.randn(n_channels, 2)

    positions_n = _normalize(positions)
    assert positions_n.min() >= -1
    assert positions_n.max() <= 1


def test_index_of():
    """Test _index_of."""
    arr = [36, 42, 42, 36, 36, 2, 42]
    lookup = _unique(arr)
    ae(_index_of(arr, lookup), [1, 2, 2, 1, 1, 0, 2])


def test_as_tuple():
    assert _as_tuple(3) == (3,)
    assert _as_tuple((3,)) == (3,)
    assert _as_tuple(None) is None
    assert _as_tuple((None,)) == (None,)
    assert _as_tuple((3, 4)) == (3, 4)
    assert _as_tuple([3]) == ([3], )
    assert _as_tuple([3, 4]) == ([3, 4], )


def test_as_array():
    ae(_as_array(3), [3])
    ae(_as_array([3]), [3])
    ae(_as_array(3.), [3.])
    ae(_as_array([3.]), [3.])

    with raises(ValueError):
        _as_array(map)


#------------------------------------------------------------------------------
# Test chunking
#------------------------------------------------------------------------------

def test_chunk_bounds():
    chunks = chunk_bounds(200, 100, overlap=20)

    assert next(chunks) == (0, 100, 0, 90)
    assert next(chunks) == (80, 180, 90, 170)
    assert next(chunks) == (160, 200, 170, 200)


def test_chunk():
    data = np.random.randn(200, 4)
    chunks = chunk_bounds(data.shape[0], 100, overlap=20)

    with raises(ValueError):
        data_chunk(data, (0, 0, 0))

    assert data_chunk(data, (0, 0)).shape == (0, 4)

    # Chunk 1.
    ch = next(chunks)
    d = data_chunk(data, ch)
    d_o = data_chunk(data, ch, with_overlap=True)

    assert np.array_equal(d_o, data[0:100])
    assert np.array_equal(d, data[0:90])

    # Chunk 2.
    ch = next(chunks)
    d = data_chunk(data, ch)
    d_o = data_chunk(data, ch, with_overlap=True)

    assert np.array_equal(d_o, data[80:180])
    assert np.array_equal(d, data[90:170])


def test_excerpts_1():
    bounds = [(start, end) for (start, end) in excerpts(100,
                                                        n_excerpts=3,
                                                        excerpt_size=10)]
    assert bounds == [(0, 10), (45, 55), (90, 100)]


def test_excerpts_2():
    bounds = [(start, end) for (start, end) in excerpts(10,
                                                        n_excerpts=3,
                                                        excerpt_size=10)]
    assert bounds == [(0, 10)]


#------------------------------------------------------------------------------
# Test PartialArray
#------------------------------------------------------------------------------

def test_partial_shape():
    assert _partial_shape((5, 3), 1) == (5,)
    assert _partial_shape((5, 3), (1,)) == (5,)
    assert _partial_shape((5, 10, 2), 1) == (5, 10)
    with raises(ValueError):
        _partial_shape((5, 10, 2), (1, 2))
    assert _partial_shape((5, 10, 3), (1, 2)) == (5,)
    assert _partial_shape((5, 10, 3), (slice(None, None, None), 2)) == (5, 10)
    assert _partial_shape((5, 10, 3), (slice(1, None, None), 2)) == (5, 9)
    assert _partial_shape((5, 10, 3), (slice(1, 5, None), 2)) == (5, 4)
    assert _partial_shape((5, 10, 3), (slice(4, None, 3), 2)) == (5, 2)


def test_partial_array():
    # 2D array.
    arr = np.random.rand(5, 2)

    ae(PartialArray(arr)[:], arr)

    pa = PartialArray(arr, 1)
    assert pa.shape == (5,)
    ae(pa[0], arr[0, 1])
    ae(pa[0:2], arr[0:2, 1])
    ae(pa[[1, 2]], arr[[1, 2], 1])
    with raises(ValueError):
        pa[[1, 2], 0]

    # 3D array.
    arr = np.random.rand(5, 3, 2)

    pa = PartialArray(arr, (2, 1))
    assert pa.shape == (5,)
    ae(pa[0], arr[0, 2, 1])
    ae(pa[0:2], arr[0:2, 2, 1])
    ae(pa[[1, 2]], arr[[1, 2], 2, 1])
    with raises(ValueError):
        pa[[1, 2], 0]

    pa = PartialArray(arr, (1,))
    assert pa.shape == (5, 3)
    ae(pa[0, 2], arr[0, 2, 1])
    ae(pa[0:2, 1], arr[0:2, 1, 1])
    ae(pa[[1, 2], 0], arr[[1, 2], 0, 1])
    with raises(ValueError):
        pa[[1, 2]]

    # Slice and 3D.
    arr = np.random.rand(5, 10, 2)

    pa = PartialArray(arr, (slice(1, None, 3), 1))
    assert pa.shape == (5, 3)
    ae(pa[0], arr[0, 1::3, 1])
    ae(pa[0:2], arr[0:2, 1::3, 1])
    ae(pa[[1, 2]], arr[[1, 2], 1::3, 1])
