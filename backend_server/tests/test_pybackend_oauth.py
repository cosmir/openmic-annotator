import pytest

import flask
import flask_oauthlib.client as client

import pybackend.oauth as OA


@pytest.fixture()
def dummy_oauth(sample_app):
    return client.OAuth(sample_app)


class DummyClient(object):
    def tokengetter(self, *args, **kwargs):
        pass


def test_BaseClient___init__(sample_app):

    with pytest.raises(NotImplementedError):
        OA.BaseClient(None, None, 'id', 'secret')

    class TestBaseClient(OA.BaseClient):
        NAME = "test-base-client"

        def _build_client(self):
            return DummyClient()

        def user(self):
            return {'me': 'abcd'}

    bc = TestBaseClient(sample_app, flask.session, 'id', 'secret')
    assert bc is not None
    assert bc.user is not None


def test_Google___init__(dummy_oauth):
    bc = OA.Google(dummy_oauth, flask.session, 'id', 'secret')
    assert bc is not None


def test_Spotify___init__(dummy_oauth):
    bc = OA.Spotify(dummy_oauth, flask.session, 'id', 'secret')
    assert bc is not None


def test_OAuth___init__(sample_app):
    sample_app.config = dict(
        oauth=dict(spotify=dict(client_id='foo', client_secret='shhh'),
                   google=dict(client_id='bar', client_secret='dontell')))
    oauth = OA.OAuth(sample_app, flask.session)
    assert oauth is not None


def test_OAuth_get(sample_app):
    sample_app.config = dict(
        oauth=dict(spotify=dict(client_id='foo', client_secret='shhh'),
                   google=dict(client_id='bar', client_secret='dontell')))
    oauth = OA.OAuth(sample_app, flask.session)
    for name in ["spotify", "google"]:
        assert oauth.get(name)
