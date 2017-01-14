"""Consolidated OAuth interfaces to third-party authentication."""

import flask_oauthlib.client as client

GOOGLE = 'google'
SPOTIFY = 'spotify'


def google_app(oauth, client_id, client_secret):
    return oauth.remote_app(
        GOOGLE,
        consumer_key=client_id,
        consumer_secret=client_secret,
        request_token_params={'scope': 'email'},
        base_url='https://www.googleapis.com/oauth2/v1/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
    )


def spotify_app(oauth, client_id, client_secret):
    return oauth.remote_app(
        SPOTIFY,
        consumer_key=client_id,
        consumer_secret=client_secret,
        base_url='https://www.spotify.com/account/',
        authorize_url='https://accounts.spotify.com/authorize?'
                      'scope=user-read-email',
        access_token_url='https://accounts.spotify.com/api/token',
        request_token_url=None,
        request_token_params=dict(show_dialog=True),
        access_token_method='POST')


APPS = {
    GOOGLE: google_app,
    SPOTIFY: spotify_app,
}


class OAuth(object):

    def __init__(self, app, session):
        """Create a multi-OAuth interface.

        Parameters
        ----------
        app : flask.Flask
            Identifier of the running Flask application.

        session : flask.session
            View of the current session.
        """
        self.oauth = client.OAuth(app)
        self.session = session
        self.apps = dict()
        for name, kwargs in app.config['oauth'].items():
            self.apps[name] = APPS[name](self.oauth, **kwargs)
            self.apps[name].tokengetter(self._tokengetter)

    def get(self, name, default=None):
        """Get an interface to a 3rd-party OAuth app, e.g. 'google'."""
        return self.apps.get(name, default)

    def _tokengetter(self):
        return self.session.get('access_token')
