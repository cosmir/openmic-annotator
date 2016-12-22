#!/usr/bin/env python
"""Run a local demo of the server-annotator system.

Performs the following:
- Starts the backend CMS server
- Uploads some audio content
- Starts serving the web-app
- Holds until the user shuts down the demo.

Note: It is advisable to use a private / incognito browser session to avoid
caching behavior, which can cause the web app to use stale source files.
"""
from __future__ import print_function

from builtins import input
import os
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import signal
import subprocess
import sys

HTTP_SERVER = {2: 'SimpleHTTPServer',
               3: 'http.server'}[sys.version_info.major]


def kill(*proccesses):
    for proc in proccesses:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)


def run():
    server = subprocess.Popen(['python', 'backend_server/main.py', '--port',
                               '8080', '--local', '--debug'],
                              stdout=subprocess.PIPE, preexec_fn=os.setsid)

    # Test that the server is on; will raise an exception after enough attempts
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(total=8, backoff_factor=0.1))
    session.mount('http://', adapter)
    try:
        session.get('http://localhost:8080')
    except requests.exceptions.ConnectionError:
        kill(server)
        raise EnvironmentError(
            "Unable to confirm that the server started successfully.")

    fnames = ["267508__mickleness__3nf.ogg",
              "345515__furbyguy__strings-piano.ogg"]
    for fn in fnames:
        fpath = os.path.abspath("./data/audio/{}".format(fn))
        subprocess.check_output(
            ["curl", '-F', 'audio=@{}'.format(fpath),
             'localhost:8080/api/v0.1/audio'])

    webapp = subprocess.Popen(['python', '-m', HTTP_SERVER],
                              stdout=subprocess.PIPE, preexec_fn=os.setsid)

    print("Now serving at: http://localhost:8000/docs/annotator.html")
    input("Press return to exit.")
    kill(server, webapp)


if __name__ == '__main__':
    run()
