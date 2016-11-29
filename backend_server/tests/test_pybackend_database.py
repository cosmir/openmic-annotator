import pytest
import json
import os

import pybackend.database as D


@pytest.fixture()
def json_file(tmpdir):
    return os.path.join(str(tmpdir), 'json_file.json')


def test_LocalClient___init__():
    db = D.LocalClient('my-project')
    assert db
    assert db.get('a') is None


def test_LocalClient_put_get():
    key = 'a'
    db = D.LocalClient('my-project')
    assert db
    assert db.get(key) is None

    exp_rec = dict(x=1, y='13')
    db.put(key, exp_rec)
    act_rec = db.get(key)
    assert act_rec == exp_rec


def test_LocalClient_read(json_file):
    key = 'a'
    exp_rec = dict(x=1, y='13')
    collec = {key: exp_rec}
    with open(json_file, 'w') as fp:
        json.dump(collec, fp)

    db = D.LocalClient('my-project', filepath=json_file, mode=D.READ)
    act_rec = db.get(key)
    assert act_rec == exp_rec

    db.put('b', dict(x=12049, y='blah blah'))
    db = D.LocalClient('my-project', filepath=json_file, mode=D.READ)

    assert db.get('b') is None


def test_LocalClient_write(json_file):
    key = 'a'
    exp_rec = dict(x=1, y='13')
    collec = {key: exp_rec}
    with open(json_file, 'w') as fp:
        json.dump(collec, fp)

    db = D.LocalClient('my-project', filepath=json_file, mode=D.WRITE)
    assert db.get(key) is None
    db.put('b', exp_rec)

    db = D.LocalClient('my-project', filepath=json_file, mode=D.READ)
    assert db.get('b') == exp_rec


def test_LocalClient_append(json_file):
    key = 'g'
    exp_rec = dict(x=1, y='13')
    collec = {key: exp_rec}
    with open(json_file, 'w') as fp:
        json.dump(collec, fp)

    db = D.LocalClient('my-project', filepath=json_file, mode=D.APPEND)
    assert db.get(key) == exp_rec

    key2 = 'apple'
    rec2 = dict(x='asdlkfj', y=[13])
    db.put(key2, rec2)

    db = D.LocalClient('my-project', filepath=json_file, mode=D.APPEND)
    assert db.get(key) == exp_rec
    assert db.get(key2) == rec2


def test_GClient___init__():
    assert D.GClient('my-proj')


def test_Database_local(json_file):
    db = D.Database('my-project', backend='local',
                    filepath=json_file, mode=D.APPEND)
    assert db
    db.put("a", dict(name='ringo'))
    assert db.get('a')