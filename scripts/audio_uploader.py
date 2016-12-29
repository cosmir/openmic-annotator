#!/usr/bin/env python
"""Upload a number of audio files and metadata to the backend CMS.

Example
-------
$ ./scripts/audio_uploader.py \
    data/audio/filelist.json \
    http://localhost:8080/api/v0.1/audio \
    --verbose 50 \
    --n_jobs -1

Note
----
The JSON object input to this script should be an array of objects, containing
values for `filename` and `metadata`:

```
  [
    {
      "filename": "foo.ogg",
      "metadata": {"source": "internet", "genre": "noise"}
    },
    ...
  ]
```

See `data/audio/filelist.json` for a more complete example.
"""
from __future__ import print_function

import argparse
import datetime
import joblib
import json
import logging
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests
from six.moves.urllib.parse import urlparse

logger = logging.basicConfig(level=logging.DEBUG)


def upload(filename, metadata, url):
    """Upload an audio file and corresponding metadata to the CMS.

    Parameters
    ----------
    filename : str
        Path to an audio file on disk.

    metadata : dict
        Object containing arbitrary metadata matching this audio file.

    url : str
        Destination for uploading data.

    Returns
    -------
    response : obj
        Dictionary containing data about the upload event, including the URI of
        the newly minted object.
    """
    start = datetime.datetime.now()
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(total=8, backoff_factor=0.02))
    session.mount('{}://'.format(urlparse(url).scheme), adapter)

    response = session.post(
        url,
        data=metadata,
        files=dict(audio=open(filename, 'rb'))
    )
    end = datetime.datetime.now()
    elapsed = end - start
    return dict(status=response.status_code, time_elapsed=str(elapsed),
                start_time=str(start), filename=filename, **response.json())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "audio_files", type=str,
        help="Collection of filenames and corresponding metadata.")
    parser.add_argument(
        "upload_url", type=str,
        help="URL endpoint for uploading audio.")
    now = datetime.datetime.now()
    parser.add_argument(
        "--log_file", type=str,
        default='upload_log-{}.json'.format(now.strftime("%Y%m%d-%H%M%S")),
        help="Filepath for writing response data as JSON.")
    parser.add_argument(
        "--verbose", type=int, default=0,
        help="Verbosity level for the uploader.")
    parser.add_argument(
        "--n_jobs", type=int, default=-2,
        help="Number of parallel jobs to run; -1 for all, -2 for all but one.")

    args = parser.parse_args()
    audio_files = json.load(open(args.audio_files))
    results = joblib.Parallel(n_jobs=args.n_jobs, verbose=args.verbose)(
        joblib.delayed(upload)(url=args.upload_url, **record)
        for record in audio_files)

    with open(args.log_file, 'w') as fp:
        json.dump(results, fp, indent=2)
