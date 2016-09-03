import pytest
import os

import pybackend.storage as S


def test_LocalData___init__(tmpdir):
    assert S.LocalData('foo', str(tmpdir)) is not None


def test_LocalData_path(tmpdir):
    name = 'foobar'
    ldata = S.LocalData(name, str(tmpdir))
    assert ldata.path.endswith(name)


def test_LocalBlob_upload_from_string(tmpdir):
    blob = S.LocalBlob('foobaz.json', str(tmpdir))
    sdata = "hooo boy, hooeee"
    blob.upload_from_string(sdata, "application/octet-stream")
    assert os.path.exists(blob.path)


def test_LocalBucket_blob(tmpdir):
    bucket = S.LocalBucket('foobizbaz', str(tmpdir))
    key = "barbar.json"
    blob = bucket.blob(key)
    assert os.path.exists(bucket.path)
    assert blob.path.endswith(key)


def test_LocalClient___init__(tmpdir):
    pass


def test_LocalClient_get_bucket(tmpdir):
    pass


def test_Storage___init__(tmpdir):
    pass


def test_Storage_client(tmpdir):
    pass


def test_Storage_upload(tmpdir):
    pass
