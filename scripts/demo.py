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

import argparse
from builtins import input
import logging
import os
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import signal
import subprocess
import sys

HTTP_SERVER = {2: 'SimpleHTTPServer',
               3: 'http.server'}[sys.version_info.major]
WEBAPP_PORT = 8000
SERVER_PORT = 8080


def kill(*proccesses):
    for proc in proccesses:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)


def run(wport, sport):
    # Some sanity checks
    assert os.path.isdir("docs") and os.path.isdir("backend_server"), \
        "This script must be launched from OpenMic's root directory."
    assert os.path.isdir("audio-annotator"), \
        "Audio Annotator not found: please run:\n\t" \
        "git submodule update --init"

    # Run the server
    cmd = "python {} --port {} --local {}".format(
        os.path.join('backend_server', 'main.py'), sport, '--debug')
    server = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE,
                              preexec_fn=os.setsid)

    # Test that the server is on; will raise an exception after enough attempts
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(total=8, backoff_factor=0.1))
    session.mount('http://', adapter)
    try:
        session.get('http://localhost:{}'.format(sport))
    except requests.exceptions.ConnectionError:
        kill(server)
        raise EnvironmentError(
            "Unable to confirm that the server started successfully.")

    # Upload audio to the server
    fnames = ["267508__mickleness__3nf.ogg",
              "345515__furbyguy__strings-piano.ogg"]
    for fn in fnames:
        fpath = os.path.abspath(os.path.join('data', 'audio', fn))
        requests.post('http://localhost:{}/api/v0.1/audio'.format(sport),
                      files=dict(audio=open(fpath, 'rb')))

    # Run the webapp
    webapp = subprocess.Popen(['python', '-m', HTTP_SERVER, str(wport)],
                              stdout=subprocess.PIPE, preexec_fn=os.setsid)
    logging.info("Now serving at: http://localhost:{}"
                 "/docs/annotator.html".format(wport))
    try:
        input("Press return to exit.\n")
    except KeyboardInterrupt:
        # Capturing Ctrl-C, to make sure we always shutdown the server
        pass
    logging.info("Shutting down server")
    kill(server, webapp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Run a local demo of the server-annotator system.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-p",
                        dest="wport",
                        default=WEBAPP_PORT,
                        type=int,
                        help="WebApp port number")
    parser.add_argument("-sp",
                        dest="sport",
                        default=SERVER_PORT,
                        type=int,
                        help="Server port number")
    args = parser.parse_args()

    # Setup the logger
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s',
                        level=logging.INFO)

    # Call main process
    run(args.wport, args.sport)
