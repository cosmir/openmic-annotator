import pytest

from io import BytesIO
import json
import os
import requests.status_codes

import pybackend.utils as utils


@pytest.fixture
def app():
    import main
    config = os.path.join(os.path.dirname(__file__), os.pardir,
                          'local_config.json')
    main.app.config['cloud'] = json.load(open(config, 'r'))
    main.app.testing = True
    with main.app.test_client() as client:
        # This forces the app to pass authentication; however, it doesn't (yet)
        # let us test that authenticated routes are blocked.
        with client.session_transaction() as sess:
            sess['access_token'] = ('fluflu', None)
        return client


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
    gid = json.loads(r.data.decode('utf-8'))['gid']

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
