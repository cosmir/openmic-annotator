"""Flask Backend Server for managing audio content.

Please see README.md for instructions.

Starting Locally
----------------
You have two options:

  $ python main.py --port 8080 --local --debug

Or, to use GCP backend by default:

  $ dev_appserver.py .


Endpoints
---------
  - /audio : POST
  - /audio/<uri> : GET
  - /annotation/submit : POST
  - /annotation/taxonomy : GET
"""

import argparse
import datetime
from flask import Flask, request, Response, jsonify
from flask import send_file
from flask_cors import CORS
import io
import json
import logging
import mimetypes
import random
import requests
import os
import tempfile

import pybackend.database
import pybackend.models
import pybackend.storage
import pybackend.urilib
import pybackend.utils


logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

# TODO: One of the following
#  - Whitelist localhost and `SOURCE` below.
#  - Use AppEngine for delivery of the annotator HTML.
CORS(app)

# Set the cloud backend
CLOUD_CONFIG = os.path.join(os.path.dirname(__file__), '.config.json')
app.config['cloud'] = json.load(open(CLOUD_CONFIG))

SOURCE = "https://cosmir.github.io/open-mic/"
AUDIO_EXTENSIONS = set(['wav', 'ogg', 'mp3', 'au', 'aiff'])
MAX_SUBMISSION_ATTEMPTS = 5

# Python 2.7 doesn't ship with `.json`?
mimetypes.add_type(mimetypes.guess_type("x.json")[0], '.json')


def store_raw_audio(db, store, audio, source=None):
    """Convenience function to store an audio file object through the webapp.

    TODO: Passing config parameters (or at least the db & storage) interfaces
    is probably The Right Thing to do, but aiming for RFC levels here.

    Parameters
    ----------
    app : flask.Flask
        Webapp with appropriate config data; see `./configs/local.DEFAULT.yaml`

    audio : werkzeug.datastructures.FileStorage
        Audio object referenced by a request object, when passed as a file in a
        POST request.

    source : dict, default=None
        Optional source metadata, describing where in another audio file this
        data may have been drawn from.

    Returns
    -------
    record : dict
        Object containing data about the new audio object, including but not
        limited to the `uri`.
        TODO: This response object has drifted on the audio upload branch, and
              should follow that lead.
    """
    file_ext = os.path.splitext(audio.filename)[-1][1:]
    if file_ext not in AUDIO_EXTENSIONS:
        raise ValueError('Attempted upload of unsupported filetype.')

    bytestring = audio.stream.read()
    # Copy to cloud storage

    gid = str(pybackend.utils.uuid(bytestring))
    store.put(gid, bytestring)

    # Index in datastore
    uri = pybackend.urilib.join('audio', gid)
    record = dict(file_ext=file_ext, created=str(datetime.datetime.utcnow()))
    if source:
        record['source'] = source

    db.put(uri, record)
    return dict(uri=uri,
                message="Received {} bytes of data.".format(len(bytestring)))


def fetch_audio_data(app, gid):
    dbase = pybackend.database.Database(
        project=app.config['cloud']['project'],
        **app.config['cloud']['database'])

    uri = pybackend.urilib.join('audio', gid)
    entity = dbase.get(uri)
    data, fext = b'', None
    if entity:
        store = pybackend.storage.Storage(
            project=app.config['cloud']['project'],
            **app.config['cloud']['storage'])

        data = store.get(entity['gid'])
        app.logger.debug("Downloaded {} bytes".format(len(data)))
        fext = entity['file_ext']
    return data, fext


@app.route('/api/v0.1/audio', methods=['POST'])
def audio_upload():
    """
    To POST files to this endpoint:

    $ curl -F "audio=@some_file.mp3" localhost:8080/api/v0.1/audio

    TODOs:
      - Store user data (who uploaded this? IP address?)
      - File metadata
    """
    audio = request.files['audio']
    store = pybackend.storage.Storage(
        project=app.config['cloud']['project'],
        **app.config['cloud']['storage'])
    db = pybackend.database.Database(
        project=app.config['cloud']['project'],
        **app.config['cloud']['database'])
    record = store_raw_audio(app, audio)
    resp = Response(uri=record['uri'], status=200,
                    mimetype=mimetypes.types_map[".json"])
    resp.headers['Link'] = SOURCE
    return resp


@app.route('/api/v0.1/audio/<gid>', methods=['GET'])
def audio_download(gid):
    """
    To GET responses from this endpoint:

    $ curl -XGET localhost:8080/audio/bbdde322-c604-4753-b828-9fe8addf17b9
    """
    data, fext = fetch_audio_data(app, gid)
    if data:
        filename = os.path.extsep.join([gid, fext])
        resp = send_file(
            io.BytesIO(data),
            attachment_filename=filename,
            mimetype=pybackend.utils.mimetype_for_file(filename))
    else:
        msg = "Resource not found: {}".format(uri)
        app.logger.info(msg)
        resp = Response(
            json.dumps(dict(message=msg)),
            status=404)

    resp.headers['Link'] = SOURCE
    return resp


@app.route('/api/v0.1/annotation', methods=['POST'])
def annotation_submit():
    """
    To POST data to this endpoint:

    $ curl -H "Content-type: application/json" \
        -X POST localhost:8080/annotation \
        -d '{"request_id": "xyz", "tags": ["a"]}'
    """
    if request.headers['Content-Type'] != 'application/json':
        raise ValueError("Invalid content type.")

    app.logger.info("Received Annotation:\n{}"
                    .format(json.dumps(request.json, indent=2)))

    user_id = session.get('user_id', 'anonymous')
    # Fetch the request object and validate this submission.
    request_uri = pybackend.urilib.join('request', request_gid)
    entity = db.get(request_uri)
    if not entity:
        raise ValueError("Invalid `request_id`.")

    request = pybackend.models.TaskRequest.from_flat(**entity)
    if request['user_id'] != user_id:
        raise ValueError("You are not authorized to submit data for this "
                         "request_id.")
    elif request['expires'] < (datetime.datetime.utcnow()):
        raise ValueError("The submission period for this task has expired.")
        # TODO: Redirect?
    elif len(request['attempts']) > MAX_SUBMISSION_ATTEMPTS:
        raise ValueError("This request has exceeded its valid number of "
                         "submissions.")
    elif request['complete']:
        raise ValueError("An annotation has already been accepted for this "
                         "request.")
    # TODO: Does the task have an answer to compare with?

    # Alright! The submission has passed all the tests.
    # Do a thing with the annotation
    # Return some progress stats?
    data = json.dumps(dict(message='Success!'))
    status = 200

    db = pybackend.database.Database(
        project=app.config['cloud']['project'],
        **app.config['cloud']['database'])
    annot = pybackend.models.AnnotationResponse.template(
        response=request.json,
        task_uri=task_uri,
        request_uri=request_uri,
        user_id=user_id)

    annot_gid = str(pybackend.utils.uuid(json.dumps(annot)))
    annot_uri = pybackend.urilib.join('annotation', annot_gid)
    db.put(annot_uri, annot.flatten())

    resp = Response(
        data, status=status, mimetype=mimetypes.types_map[".json"])
    resp.headers['Link'] = SOURCE
    return resp


@app.route('/api/v0.1/taxonomy/<key>', methods=['GET'])
def annotation_taxonomy():
    """
    To fetch data at this endpoint:

    $ curl -X GET localhost:8080/taxonomy/instrument_taxonomy_v0
    """
    instruments = pybackend.taxonomy.get(key)
    status = 200 if instruments else 400

    resp = Response(json.dumps(instruments), status=status)
    resp.headers['Link'] = SOURCE
    return resp


@app.route('/api/v0.1/task', methods=['POST'])
def create_task():
    """

    Body Data
    ---------
    parent : str
        URI of the parent to build an observation task over.

    time : number > 0
        Start time of the observation task.

    duration : number > 0
        Duration of the observation task.

    taxonomy : str
        A taxonomy key; see `pybackend.taxonomy.get` for more info.

    feedback : str, default='none'

    visualization : str, default=waveform

    Response
    --------
    uri : str
        A URI for the generated task.
    """
    app.logger.info("json: {}".format(request.json))
    track_uri = request.json['parent']

    source = dict(uri=track_uri,
                  time=request.json['time'],
                  duration=request.json['duration']),

    if request.files['audio']:
        record = store_raw_audio(app, request.files['audio'], source)
    else:
        # TODO: Trim the source audio
        raise NotImplementedError(
            "Unclear how to trim OGG files in AppEngine; "
            "maybe we don't have to?")

    task = pybackend.models.Task.template(
        audio_uri=record['uri'], source=source,
        taxonomy=request.json['taxonomy'],
        feedback=request.json.get('feedback', 'none'),
        visualization=request.json.get('visualization', 'waveform'))

    gid = str(pybackend.utils.uuid(json.dumps(task)))
    task_uri = pybackend.urilib.join('task', gid)
    db.put(task_uri, task.flatten())

    # TODO: Maybe don't return this? depends on who can create them...
    return jsonify(dict(uri=task_uri))


# TODO: It's not clear that we want this route to be public.
@app.route('/api/v0.1/task/<gid>', methods=['GET'])
def get_task():
    """
    To fetch data at this endpoint:

    $ curl -X GET localhost:8080/task/<gid>
    """
    db = pybackend.database.Database(
        project=app.config['cloud']['project'],
        **app.config['cloud']['database'])

    uri = pybackend.urilib.join('task', gid)
    entity = db.get(uri)
    if not entity:
        raise ValueError("No task exists for the given gid: {}".format(gid))

    task = pybackend.models.Task.from_flat(**entity)
    audio_url = "{scheme}://{netloc}/api/v0.1/audio/{gid}".format(
        gid=pybackend.urilib.split(task_record['audio_uri'])[1],
        **app.config['cloud']['annotator'])

    tax = pybackend.taxonomy.get(task['payload'].pop('taxonomy'))
    data = json.dumps(dict(audio_url=audio_url, taxonomy=tax,
                           **task['payload']))
    app.logger.debug("Returning:\n{}".format(data))
    resp = Response(data)
    resp.headers['Link'] = SOURCE
    return resp


@app.route('/api/v0.1/task', methods=['GET'])
def request_task():
    """
    To fetch data at this endpoint:

    $ curl -X GET localhost:8080/task
    """
    db = pybackend.database.Database(
        project=app.config['cloud']['project'],
        **app.config['cloud']['database'])

    # Get the URI of the highest priority task
    # TODO: User conditional?
    query = db.query(filter=('kind', 'task'),
                     sortby=['priority'], order='descending')
    query.filter_keys()
    task_uri = next(query)
    if not track_uri:
        raise ValueError("No tasks exists!")

    # Build a request object
    # TODO: This *should* be sufficiently unique, but some kind of salt / rng
    #       couldn't hurt.
    task_request = pybackend.models.TaskRequest(
        user_id=session.get('user_id', 'anonymous'),
        task_uri=task_uri, expires=600)

    request_gid = str(pybackend.utils.uuid(json.dumps(task_request)))
    request_uri = pybackend.urilib.join('request', request_gid)

    # TODO: Database objects should try to flatten (and maybe expand?) records
    #       on their own.
    db.put(request_uri, task_request.flatten())

    # Retrieve the actual task data & build a unique response.
    # TODO: Give `get` a strict field to raise its own errors. (Flask recovers
    #       from exceptions well, right?)
    entity = db.get(task_uri)
    if not entity:
        # This should never happen, unless a task is deleted between the above
        # query and now.
        raise ValueError("No entity exists for the given uri: {}"
                         "".format(task_uri))

    task = pybackend.models.Task.from_flat(**entity)
    audio_url = "{scheme}://{netloc}/api/v0.1/audio/{gid}".format(
        gid=pybackend.urilib.split(task['audio_uri'])[1],
        **app.config['cloud']['annotator'])

    tax = pybackend.taxonomy.get(task['payload'].pop('taxonomy'))
    data = json.dumps(dict(request_id=request_gid, audio_url=audio_url,
                           taxonomy=tax, **task['payload']))
    app.logger.debug("Returning:\n{}".format(data))
    resp = Response(data)
    resp.headers['Link'] = SOURCE
    return resp


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
