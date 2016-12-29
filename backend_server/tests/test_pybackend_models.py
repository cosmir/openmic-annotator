import pytest
import json
import pybackend.models as M


def test_BaseRecord___init__():
    rec = M.BaseRecord()
    assert len(rec.serialized_keys) == 0


class DummyRecord(M.BaseRecord):
    serialized_keys = ['a']


def test_DummyRecord_flatten():
    a = dict(x=13, y=['d', 'e', 'f'])
    b = "fluflu"
    rec = DummyRecord(a=a, b=b)
    flatrec = rec.flatten()

    assert isinstance(flatrec['a'], str)
    assert isinstance(rec['a'], dict)
    assert flatrec['b'] == rec['b'] == b


def test_DummyRecord_expand():
    a = dict(x=13, y=['d', 'e', 'f'])
    aflat = json.dumps(a)
    b = "fluflu"

    rec = DummyRecord.from_flat(**{'a': aflat, 'b': b})
    assert rec['a'] == a
    assert rec['b'] == b
