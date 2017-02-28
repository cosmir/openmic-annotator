#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Please provide a project for deployment."
    exit 1;
fi

# Update the gcloud config template and point to it as the default.
sed "s/<YOUR_PROJECT_ID>/$1/" configs/gcloud.DEFAULT.yaml > .config.yaml

# Run the test suite, tank deployment on failure.
py.test tests
echo "All tests pass -- deploying"

LIBDIR=lib
rm -rf $LIBDIR
pip install . -t $LIBDIR

gcloud app deploy
