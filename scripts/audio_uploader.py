#!/usr/bin/env python
"""Upload a number of audio files

"""
from __future__ import print_function

import argparse
import datetime
import joblib
import json
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests
from six.moves.urllib.parse import urlparse


def upload(fpath, url):
    start = datetime.datetime.now()
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(total=8, backoff_factor=0.02))
    session.mount('{}://'.format(urlparse(url).scheme), adapter)

    response = session.post(url, files=dict(audio=open(fpath, 'rb')))
    end = datetime.datetime.now()
    elapsed = end - start
    return dict(status=response.status_code, time_elapsed=str(elapsed),
                start_time=str(start), filename=fpath)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "filelist", type=str,
        help="Port on which to serve.")
    parser.add_argument(
        "upload_url", type=str,
        help="URL endpoint for uploading audio.")
    now = datetime.datetime.now()
    parser.add_argument(
        "--log_file", type=str,
        default='upload_log-{}.json'.format(now.strftime("%Y%m%d-%H%M%S")),
        help="URL endpoint for uploading audio.")
    parser.add_argument(
        "--verbose", type=int, default=0,
        help="Verbosity level for the uploader.")
    parser.add_argument(
        "--n_jobs", type=int, default=-2,
        help="Number of parallel jobs to run; -1 for all, -2 for all but one.")

    args = parser.parse_args()
    filepaths = json.load(open(args.filelist))
    stats = joblib.Parallel(n_jobs=args.n_jobs, verbose=args.verbose)(
        joblib.delayed(upload)(fpath, args.upload_url) for fpath in filepaths)
    with open(args.log_file, 'w') as fp:
        json.dump(stats, fp)
