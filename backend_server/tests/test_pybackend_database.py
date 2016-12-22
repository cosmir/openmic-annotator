import flask
import pytest
import json
import os

import pybackend.database as D

TEST_GCP_PROJECT = os.environ.get('TEST_GCP_PROJECT', None)


@pytest.fixture()
def json_file(tmpdir):
    return os.path.join(str(tmpdir), 'json_file.json')


def test_LocalClient___init__():
    db = D.LocalClient('my-project')
    assert db
    assert db.get('a:1234') is None


def test_LocalClient_put_get():
    uri = 'a:1234'
    db = D.LocalClient('my-project')
    assert db
    assert db.get(uri) is None

    exp_rec = dict(x=1, y='13')
    db.put(uri, exp_rec)
    act_rec = db.get(uri)
    assert act_rec == exp_rec


def test_LocalClient_read(json_file):
    uri = 'a:1234'
    exp_rec = dict(x=1, y='13')
    collec = {uri: exp_rec}
    with open(json_file, 'w') as fp:
        json.dump(collec, fp)

    db = D.LocalClient('my-project', filepath=json_file, mode=D.READ)
    act_rec = db.get(uri)
    assert act_rec == exp_rec

    uri2 = 'b:1235'
    db.put(uri2, dict(x=12049, y='blah blah'))
    db = D.LocalClient('my-project', filepath=json_file, mode=D.READ)

    assert db.get(uri2) is None


def test_LocalClient_write(json_file):
    uri = 'a:1234'
    exp_rec = dict(x=1, y='13')
    collec = {uri: exp_rec}
    with open(json_file, 'w') as fp:
        json.dump(collec, fp)

    db = D.LocalClient('my-project', filepath=json_file, mode=D.WRITE)
    assert db.get(uri) is None

    uri2 = 'b:5678'
    db.put(uri2, exp_rec)
    db = D.LocalClient('my-project', filepath=json_file, mode=D.READ)
    assert db.get(uri2) == exp_rec


def test_LocalClient_append(json_file):
    uri1 = 'g:1357'
    exp_rec = dict(x=1, y='13')
    collec = {uri1: exp_rec}
    with open(json_file, 'w') as fp:
        json.dump(collec, fp)

    db = D.LocalClient('my-project', filepath=json_file, mode=D.APPEND)
    assert db.get(uri1) == exp_rec

    uri2 = 'apple:158902'
    rec2 = dict(x='asdlkfj', y=[13])
    db.put(uri2, rec2)

    db = D.LocalClient('my-project', filepath=json_file, mode=D.APPEND)
    assert db.get(uri1) == exp_rec
    assert db.get(uri2) == rec2


def test_LocalClient_delete(json_file):
    uri = 'g:9876'
    exp_rec = dict(x=1, y='13')
    collec = {uri: exp_rec}
    with open(json_file, 'w') as fp:
        json.dump(collec, fp)
    db = D.LocalClient('my-project', filepath=json_file, mode=D.APPEND)
    assert db.get(uri) == exp_rec
    db.delete(uri)
    assert db.get(uri) is None


@pytest.fixture()
def sample_client(json_file):
    uri = 'animal:1h2j34'
    exp_rec = dict(x=1, y='13')
    collec = {uri: exp_rec}
    with open(json_file, 'w') as fp:
        json.dump(collec, fp)
    return D.LocalClient('my-project', filepath=json_file, mode=D.READ)


def test_LocalClient_uris(sample_client):
    uris = list(sample_client.uris())
    assert len(uris) == 1
    assert sample_client.get(uris[0]) == dict(x=1, y='13')


def test_GClient___init__():
    assert D.GClient('my-proj') is not None


@pytest.mark.skipif(
    TEST_GCP_PROJECT is None,
    reason="Environment variable `TEST_GCP_PROJECT` is unset; "
           "unable to test DataStore")
def test_GClient__client():
    db = D.GClient(TEST_GCP_PROJECT)
    assert db._client is not None


@pytest.mark.skipif(
    TEST_GCP_PROJECT is None,
    reason="Environment variable `TEST_GCP_PROJECT` is unset; "
           "unable to test DataStore")
def test_GClient_put_get():
    uri = 'book:asdf1234'
    record = dict(title='my favorite book', author='aristotle')
    db = D.GClient(TEST_GCP_PROJECT)
    db.put(uri, record)
    assert db.get(uri) == record


@pytest.mark.skipif(
    TEST_GCP_PROJECT is None,
    reason="Environment variable `TEST_GCP_PROJECT` is unset; "
           "unable to test DataStore")
def test_GClient_uris():

    uri = 'book:asdf123456789'
    record = dict(title='a lot of words', author='tolstoy')
    db = D.GClient(TEST_GCP_PROJECT)
    db.put(uri, record)

    for uri in db.uris():
        break
    assert uri

    for uri in db.uris(kind='book'):
        break
    assert "book:" in uri


def test_Database_local(json_file):
    db = D.Database('my-project', backend='local',
                    filepath=json_file, mode=D.APPEND)
    assert db
    uri = 'a:1582934'
    db.put(uri, dict(name='ringo'))
    assert db.get(uri)
