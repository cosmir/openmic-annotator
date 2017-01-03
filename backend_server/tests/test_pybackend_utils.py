from __future__ import print_function
import pytest

import pybackend.utils


def test_utils_uuid():
    data = 'blahblah'
    # Expected hash determined by inspection
    exp = "42d388f8-b1db-497f-aaf7-dab487f11290"
    uuid1 = pybackend.utils.uuid(data)
    assert uuid1 == pybackend.utils.uuid(data)
    assert str(uuid1) == exp
    assert uuid1 != pybackend.utils.uuid('foobar')


def test_check_connection():
    assert not pybackend.utils.check_connection("http://blahblah")
    assert pybackend.utils.check_connection("http://google.com")


def test_mimetype_for_file():
    fnames = ['x.json', 'x.monkey']
    mtypes = ['application/json', 'application/octet-stream']
    for fn, m in zip(fnames, mtypes):
        assert pybackend.utils.mimetype_for_file(fn) == m
