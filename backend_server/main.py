"""Flask Backend Server for managing audio content.

Please see README.md for instructions.

Starting Locally
----------------
You have two options:

  $ python main.py --local --debug

Or, to use GCP backend by default:

  $ dev_appserver.py .


Endpoints
---------
  - /audio/upload : POST
  - /audio/<uri> : GET
  - /annotation/submit : POST
  - /annotation/taxonomy : GET
"""

import argparse
import datetime
from flask import Flask, request, Response
from flask import send_file
import io
import json
import logging
import requests
import os

import pybackend.database
import pybackend.mime
import pybackend.storage
import pybackend.utils


logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

# Set the cloud backend
# TODO: This should be controlled by `app.yaml`, right?
CLOUD_CONFIG = os.path.join(os.path.dirname(__file__), 'gcloud_config.json')
app.config['cloud'] = json.load(open(CLOUD_CONFIG))

SOURCE = "https://cosmir.github.io/open-mic/"


@app.route('/')
def hello():
    return 'oh hai'


@app.route('/audio/upload', methods=['POST'])
def audio_upload():
    """
    To POST files to this endpoint:

    $ curl -F "audio=@some_file.mp3" localhost:8080/audio/upload

    TODOs:
      - Store user data (who uploaded this? IP address?)
      -
    """

    data = json.dumps(dict(message='Invalid request'))
    status = 400
    if request.method == 'POST':
        audio_data = request.files['audio']
        bytestring = audio_data.stream.read()

        # Copy to cloud storage
        store = pybackend.storage.Storage(
            project_id=app.config['cloud']['project_id'],
            **app.config['cloud']['storage'])

        uri = str(pybackend.utils.uuid(bytestring))
        fext = os.path.splitext(audio_data.filename)[-1]
        filepath = "{}{}".format(uri, fext)
        store.upload(bytestring, filepath)

        # Index in datastore
        # Keep things like extension, storage platform, mimetype, etc.
        dbase = pybackend.database.Database(
            project_id=app.config['cloud']['project_id'],
            **app.config['cloud']['database'])
        record = dict(filepath=filepath,
                      created=str(datetime.datetime.now()))
        dbase.put(uri, record)
        record.update(
            uri=uri,
            message="Received {} bytes of data.".format(len(bytestring)))
        status = 200
        data = json.dumps(record)

    resp = Response(data, status=status,
                    mimetype=pybackend.mime.MIMETYPES['json'])
    resp.headers['Link'] = SOURCE
    return resp


@app.route('/audio/<uri>', methods=['GET'])
def audio_download(uri):
    """
    To GET responses from this endpoint:

    $ curl -XGET localhost:8080/audio/bbdde322-c604-4753-b828-9fe8addf17b9
    """

    # Create the null response.
    data = json.dumps(dict(message='Resource not found for `{}`'.format(uri)))
    resp = Response(data, status=404,
                    mimetype=pybackend.mime.MIMETYPES['json'])

    if request.method == 'GET':
        dbase = pybackend.database.Database(
            project_id=app.config['cloud']['project_id'],
            **app.config['cloud']['database'])

        entity = dbase.get(uri)
        if entity is None:
            app.logger.info("Resource not found: {}".format(uri))

        else:
            store = pybackend.storage.Storage(
                project_id=app.config['cloud']['project_id'],
                **app.config['cloud']['storage'])

            data = store.download(entity['filepath'])
            app.logger.debug("Returning {} bytes".format(len(data)))

            resp = send_file(
                io.BytesIO(data),
                attachment_filename=entity['filepath'],
                mimetype=pybackend.mime.mimetype_for_file(entity['filepath']))

    resp.headers['Link'] = SOURCE
    return resp


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
        "--port", type=int, default=8080,
        help="Port on which to serve.")
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
        app.config['cloud'] = json.load(open(config))

    app.run(debug=args.debug, port=args.port)
