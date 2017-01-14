import pytest

from io import BytesIO
import json
import os
import requests.status_codes
import werkzeug.datastructures as DS

import pybackend.database
import pybackend.storage
import pybackend.urilib
import pybackend.utils as utils

from main import store_raw_audio, fetch_audio_data


@pytest.fixture
def cloud_cfg():
    config = os.path.join(os.path.dirname(__file__), os.pardir,
                          'local_config.json')
    return json.load(open(config, 'r'))


@pytest.fixture
def app(cloud_cfg):
    import main
    main.app.config.update(cloud=cloud_cfg)
    main.app.testing = True
    return main.app.test_client()


def test_store_raw_audio(app, cloud_cfg):
    audio = DS.FileStorage(stream=BytesIO(b'my file contents'),
                           filename='blah.wav')

    store = pybackend.storage.Storage(
        project=cloud_cfg['project'], **cloud_cfg['storage'])
    db = pybackend.database.Database(
        project=cloud_cfg['project'], **cloud_cfg['database'])

    res = store_raw_audio(db, store, audio)
    assert res['uri'].startswith("audio:")


def test_fetch_audio_data(app, cloud_cfg):
    bts = b'my file contents'
    audio = DS.FileStorage(stream=BytesIO(bts),
                           filename='blah.wav')

    store = pybackend.storage.Storage(
        project=cloud_cfg['project'], **cloud_cfg['storage'])
    db = pybackend.database.Database(
        project=cloud_cfg['project'], **cloud_cfg['database'])

    res = store_raw_audio(db, store, audio)
    gid = pybackend.urilib.split(res['uri'])[1]
    data, fext = fetch_audio_data(db, store, gid)
    assert data == bts


def test_audio_upload(app):
    data = dict(audio=(BytesIO(b'my file contents'), 'blah.wav'))
    r = app.post('/api/v0.1/audio', data=data)
    assert r.status_code == requests.status_codes.codes.OK


def test_audio_upload_method_not_allowed(app):
    r = app.get('/api/v0.1/audio')
    assert r.status_code == requests.status_codes.codes.METHOD_NOT_ALLOWED


def test_audio_upload_bad_filetype(app):
    data = dict(audio=(BytesIO(b'new file contents'), 'blah.exe'))
    r = app.post('/api/v0.1/audio', data=data)
    assert r.status_code == requests.status_codes.codes.BAD_REQUEST


def test_audio_get(app):
    # First we'll generate data...
    content = b'my new file contents'
    data = dict(audio=(BytesIO(content), 'blah.wav'))
    r = app.post('/api/v0.1/audio', data=data)
    assert r.status_code == requests.status_codes.codes.OK
    uri = json.loads(r.data.decode('utf-8'))['uri']

    gid = pybackend.urilib.split(uri)[1]
    # Now let's go looking for it
    r = app.get('/api/v0.1/audio/{}'.format(gid))
    assert r.status_code == requests.status_codes.codes.OK
    assert r.data == content


def test_audio_get_no_resource(app):
    r = app.get('/api/v0.1/audio/{}'.format("definitelydoesntexist"))
    assert r.status_code == requests.status_codes.codes.NOT_FOUND


def test_audio_post_fails(app):
    data = dict(audio=(BytesIO(b'my new file contents'), 'blah.wav'))
    r = app.post('/api/v0.1/audio/{}'.format("abc"), data=data)
    assert r.status_code == requests.status_codes.codes.METHOD_NOT_ALLOWED


def test_annotation_submit(app):
    r = app.post('/api/v0.1/annotation/submit',
                 data=json.dumps(dict(foo='bar')),
                 content_type='application/json')
    assert r.status_code == requests.status_codes.codes.OK


@pytest.mark.skipif(not utils.check_connection(), reason='No internet')
def test_annotation_taxonomy(app):
    r = app.get('/api/v0.1/annotation/taxonomy')
    assert r.status_code == requests.status_codes.codes.OK


def test_task_get(app):
    r = app.get('/api/v0.1/task')
    assert r.status_code == requests.status_codes.codes.OK
