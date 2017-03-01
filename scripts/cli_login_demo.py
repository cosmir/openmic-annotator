#!/usr/bin/env python
"""Demonstrate the OAuth login process for commandline tools.

Example
-------
$ ./scripts/cli_login_demo.py http://localhost:8080

"""
from __future__ import print_function

import argparse
from builtins import input
import os
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from six.moves.urllib.parse import urlparse
import webbrowser


def demo(base_url):
    """Login through a third-party OAuth handler and print some stats.

    Parameters
    ----------
    base_url : str
        Base URL of the CMS server.
    """
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.02))
    session.mount('{}://'.format(urlparse(base_url).scheme), adapter)

    wb = webbrowser.get()
    login_url = os.path.join(base_url, "login?complete=no")
    session.get(login_url)
    wb.open(login_url)

    auth_url = input("Enter the URL returned after authentication:")
    response = session.get(auth_url.replace("complete=no", 'complete=yes'))
    assert response.status_code == 200

    print(session.get(os.path.join(base_url, 'me')).content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "base_url", type=str,
        help="Base URL of the server.")

    args = parser.parse_args()
    demo(args.base_url)
