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
