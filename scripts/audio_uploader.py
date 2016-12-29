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

import os
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import signal
import subprocess