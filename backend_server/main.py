"""Flask Backend Server for managing audio content.


Running Locally
---------------
First, follow the directions to install the App Engine SDK:

  https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python

Then, once that's all set, you should be able to do the following from
repository root:

  $ cd backend_server
  $ dev_appserver.py .

At this point, the endpoints should be live via localhost:

  $ curl -X GET localhost:8080/annotation/taxonomy
  $ curl -F "audio=@some_file.mp3" localhost:8080/audio/upload


Deploying to App Engine
-----------------------
For the time being, you will need to create your own App Engine project. To do
so, follow the directions here:

  https://console.cloud.google.com/freetrial?redirectPath=/start/appengine

Once this is configured, make note of your `PROJECT_ID`, because you're going
to need it.

  $ cd backend_server
  $ pip install -t lib -r requirements/setup/requirements_dev.txt
  $ appcfg.py -A <PROJECT_ID> -V v1 update .

From here, the app should be deployed to the following URL:

  http://<PROJECT_ID>.appspot.com

You can then poke the endpoints as one would expect:

  $ curl -X GET http://<PROJECT_ID>.appspot.com/annotation/taxonomy
  $ curl -F "audio=@some_file.mp3" http://<PROJECT_ID>/audio/upload


Shutting Down App Engine
------------------------
After deploying the application, you may wish to shut it down so as to not
ring up unnecessary charges / usage. Proceed to the following URL and click
all the things that say "Shutdown" for maximum certainty:

  https://console.cloud.google.com/appengine/instances?project=<PROJECT_ID>

Be sure to replace <PROJECT_ID> with the appropriate one matching the account
you've configured.
"""
import argparse
import datetime
from flask import Flask, request
import json
import logging
import requests
import os

import pybackend.storage
import pybackend.utils


logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
GCP_CONFIG = os.path.join(os.path.dirname(__file__), 'gcloud_config.json')
app.config['gcp'] = json.load(open(GCP_CONFIG))


@app.route('/')
def hello():
    return 'oh hai'


@app.route('/audio/upload', methods=['POST'])
def audio_upload():
    """
    To POST files to this endpoint:

    $ curl -F "audio=@some_file.mp3" localhost:8080/audio/upload

    TODO: Define / adopt common response schema for endpoints.
    """
    response = dict(message='nothing happened', status=400)
    if request.method == 'POST':
        audio_data = request.files['audio']
        bytestring = audio_data.stream.read()

        # Copy to cloud storage
        store = pybackend.storage.Storage(
            project_id=app.config['gcp']['project_id'],
            **app.config['gcp']['storage'])

        key = pybackend.utils.uuid(bytestring)
        fext = os.path.splitext(audio_data.filename)[-1]
        filepath = "{}{}".format(key, fext)
        store.upload(bytestring, filepath)

        # Index in datastore
        # Keep things like extension, storage platform, mimetype, etc.
        dbase = pybackend.database.Database(
            project_id=app.config['gcp']['project_id'],
            **app.config['gcp']['database'])
        record = dict(filepath=filepath,
                      created=str(datetime.datetime.now()))
        dbase.put(key, record)
        record.update(key=key)
        response.update(
            status=200, data=record,
            message="Received {} bytes of data.".format(len(bytestring)))

    return json.dumps(response)


@app.route('/annotation/submit', methods=['POST'])
def annotation_submit():
    """
    To POST data to this endpoint:

    $ curl -H "Content-type: application/json" \
        -X POST localhost:8080/annotation/submit \
        -d '{"message":"Hello Data"}'
    """
    response = dict(message='nothing happened', status=400)
    conds = [request.method == 'POST',
             request.headers['Content-Type'] == 'application/json']
    if all(conds):
        app.logger.info("Received Annotation:\n{}"
                        .format(json.dumps(request.json, indent=2)))
        # obj = json.loads(request.data)
        response['message'] = "success"
        response['status'] = 200

    return json.dumps(response)


@app.route('/annotation/taxonomy', methods=['GET'])
def annotation_taxonomy():
    """
    To fetch data at this endpoint:

    $ curl -X GET localhost:8080/annotation/taxonomy

    TODO: Clean this up per @alastair's feedback. Also warrants a response
    schema, rather than just the serialized taxonomy.
    """
    tax_url = ("https://raw.githubusercontent.com/marl/jams/master/jams/"
               "schemata/namespaces/tag/medleydb_instruments.json")
    res = requests.get(tax_url)
    tax = {}
    if res.text:
        tax = json.loads(res.text)

    return json.dumps(tax)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--local",
        action='store_true', help="Use local backend services.")
    parser.add_argument(
        "--debug",
        action='store_true',
        help="Run the Flask application in debug mode.")

    args = parser.parse_args()

    if args.local:
        config = os.path.join(os.path.dirname(__file__), 'local_config.json')
        app.config['gcp'] = json.load(open(config))

    app.run(debug=args.debug)
