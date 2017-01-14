import pytest

import flask
import flask_oauthlib.client as client

import pybackend.oauth as OA


@pytest.fixture()
def dummy_app():
    app = flask.Flask("dummy_app")
    app.testing = True
    with app.test_client() as flk:
        return flk


@pytest.fixture()
def dummy_oauth(dummy_app):
    return client.OAuth(dummy_app)


class DummyClient(object):
    def tokengetter(self, *args, **kwargs):
        pass


def test_BaseClient___init__():

    with pytest.raises(NotImplementedError):
        OA.BaseClient(None, None, 'id', 'secret')

    class TestBaseClient(OA.BaseClient):
        def _build_client(self):
            return DummyClient()

    bc = TestBaseClient(None, None, 'id', 'secret')
    assert bc is not None


def test_Google___init__(dummy_oauth):
    bc = OA.Google(dummy_oauth, flask.session, 'id', 'secret')
    assert bc is not None


def test_Spotify___init__(dummy_oauth):
    bc = OA.Spotify(dummy_oauth, flask.session, 'id', 'secret')
    assert bc is not None
