import pytest

from io import BytesIO
import json
import requests.status_codes

import pybackend.utils as utils


def test_audio_upload(sample_app):
    data = dict(audio=(BytesIO(b'my file contents'), 'blah.wav'))
    r = sample_app.post('/api/v0.1/audio', data=data)
    assert r.status_code == requests.status_codes.codes.OK


def test_audio_upload_method_not_allowed(sample_app):
    r = sample_app.get('/api/v0.1/audio')
    assert r.status_code == requests.status_codes.codes.METHOD_NOT_ALLOWED


def test_audio_upload_bad_filetype(sample_app):
    data = dict(audio=(BytesIO(b'new file contents'), 'blah.exe'))
    r = sample_app.post('/api/v0.1/audio', data=data)
    assert r.status_code == requests.status_codes.codes.BAD_REQUEST


def test_audio_get(sample_app):
    # First we'll generate data...
    content = b'my new file contents'
    data = dict(audio=(BytesIO(content), 'blah.wav'))
    r = sample_app.post('/api/v0.1/audio', data=data)
    assert r.status_code == requests.status_codes.codes.OK
    gid = json.loads(r.data.decode('utf-8'))['gid']

    # Now let's go looking for it
    r = sample_app.get('/api/v0.1/audio/{}'.format(gid))
    assert r.status_code == requests.status_codes.codes.OK
    assert r.data == content


def test_audio_get_no_resource(sample_app):
    r = sample_app.get('/api/v0.1/audio/{}'.format("definitelydoesntexist"))
    assert r.status_code == requests.status_codes.codes.NOT_FOUND


def test_audio_post_fails(sample_app):
    data = dict(audio=(BytesIO(b'my new file contents'), 'blah.wav'))
    r = sample_app.post('/api/v0.1/audio/{}'.format("abc"), data=data)
    assert r.status_code == requests.status_codes.codes.METHOD_NOT_ALLOWED


def test_annotation_submit(sample_app):
    r = sample_app.post('/api/v0.1/annotation/submit',
                        data=json.dumps(dict(foo='bar')),
                        content_type='application/json')
    assert r.status_code == requests.status_codes.codes.OK


@pytest.mark.skipif(not utils.check_connection(), reason='No internet')
def test_annotation_taxonomy(sample_app):
    r = sample_app.get('/api/v0.1/annotation/taxonomy')
    assert r.status_code == requests.status_codes.codes.OK


def test_task_get(sample_app):
    r = sample_app.get('/api/v0.1/task')
    assert r.status_code == requests.status_codes.codes.OK
