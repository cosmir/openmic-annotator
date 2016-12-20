#!/usr/bin/python
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

import os
import signal
import subprocess
import time


def run():
    server = subprocess.Popen(['python', 'backend_server/main.py', '--port',
                               '8080', '--local', '--debug'],
                              stdout=subprocess.PIPE, preexec_fn=os.setsid)
    time.sleep(4)
    fnames = ["267508__mickleness__3nf.ogg",
              "345515__furbyguy__strings-piano.ogg"]
    for fn in fnames:
        fpath = os.path.abspath("./data/audio/{}".format(fn))
        subprocess.check_output(
            ["curl", '-F', 'audio=@{}'.format(fpath),
             'localhost:8080/api/v0.1/audio'])

    webapp = subprocess.Popen(['python', '-m', 'http.server'],
                              stdout=subprocess.PIPE, preexec_fn=os.setsid)
    print("Now serving at: http://localhost:8000/docs/annotator.html")
    try:
        input("Press return to exit.")
    except:
        pass
    os.killpg(os.getpgid(server.pid), signal.SIGTERM)
    os.killpg(os.getpgid(webapp.pid), signal.SIGTERM)


if __name__ == '__main__':
    run()
