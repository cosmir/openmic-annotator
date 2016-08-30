import pytest


@pytest.fixture
def app():
    import main
    main.app.testing = True
    return main.app.test_client()


def test_index(app):
    r = app.get('/')
    assert r.status_code == 200


@pytest.mark.skipif(True, reason="writeme")
def test_audio_upload(app):
    r = app.get('/audio/upload')
    assert r.status_code == 200


@pytest.mark.skipif(True, reason="writeme")
def test_audio_upload(app):
    r = app.get('/annotation/submit')
    assert r.status_code == 200


@pytest.mark.skipif(True, reason="writeme")
def test_audio_upload(app):
    r = app.get('/annotation/taxonomy')
    assert r.status_code == 200