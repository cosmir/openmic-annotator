import pytest
import json
import pybackend.models as M


def test_Record___init__():
    rec = M.Record(['a', 'b'])
    assert len(rec.serialized_keys) == 2


def test_Record_flatten():
    s = "fluflu"
    k1 = 'a'
    k2 = 'b'
    rec = M.Record(serialized_keys=[k1])
    rec[k1] = dict(x=13, y=['d', 'e', 'f'])
    rec[k2] = s
    flatrec = rec.flatten()

    assert isinstance(flatrec[k1], str)
    assert isinstance(rec[k1], dict)
    assert flatrec[k2] == rec[k2] == s


def test_Record_expand():
    s = "fluflu"
    k1 = 'a'
    k2 = 'b'

    data = dict(x=13, y=['d', 'e', 'f'])
    sdat = json.dumps(data)

    rec = M.Record(serialized_keys=[k1])
    rec.expand(**{k1: sdat, k2: s})

    assert rec[k1] == data
    assert rec[k2] == s
