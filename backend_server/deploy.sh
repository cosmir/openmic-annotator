#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Please provide a project for deployment."
    exit 1;
fi

sed "s/<YOUR_PROJECT_ID>/$1/" gcloud_config.json > .config.json

# Run the test suite, tank deployment on failure.
py.test tests
echo "All tests pass -- deploying"

# LIBDIR=lib
# rm -rf $LIBDIR
# pip install . -t $LIBDIR

# gcloud app deploy
