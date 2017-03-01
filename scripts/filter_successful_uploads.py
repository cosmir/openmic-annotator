#!/usr/bin/env python
"""Filter the successfully uploaded files from a list of files.

Example
-------
$ ./scripts/filter_successful_uploads.py \
    data/audio/filelist.json \
    data/sample_upload_log.json \
    new_filelist.json

"""
from __future__ import print_function

import argparse
import json


def filter_successes(filelist, upload_results):
    """Filter the records in `filelist` that uploaded successfully in
    `upload_results`.

    Parameters
    ----------
    filelist : list
        Collection of audio file data to filter.

    upload_results : list
        Collection of audio uploader result objects.

    Returns
    -------
    remaining_files : list
        Objects in filelist that were not uploaded successfully, according to
        `upload_results`.
    """
    successful_files = set([res['filename'] for res in upload_results
                            if res['status'] == 200])
    remaining_files = [fdata for fdata in filelist
                       if fdata['filename'] not in successful_files]
    return remaining_files


def parse_log(log_file):
    """Parse a newline-separated logfile into result objects."""
    with open(log_file, 'r') as fp:
        results = [json.loads(line.strip()) for line in fp]
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "audio_files", type=str,
        help="Collection of filenames and corresponding metadata.")
    parser.add_argument(
        "log_file", type=str,
        help="Filepath to the upload results of `audio_uploader`.")
    parser.add_argument(
        "remaining_files", type=str,
        help="Filepath to the upload results of `audio_uploader`.")

    args = parser.parse_args()
    audio_files = json.load(open(args.audio_files))
    upload_results = parse_log(args.log_file)
    remaining_files = filter_successes(audio_files, upload_results)
    with open(args.remaining_files, 'w') as fp:
        json.dump(remaining_files, fp, indent=2)
