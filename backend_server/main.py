import json
import logging
import urllib2

from flask import Flask, request

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)


@app.route('/')
def hello():
    return 'How do you know she is a witch?'


@app.route('/audio/upload', methods=['POST'])
def audio_upload():
    """
    To POST data to this endpoint:

    $ curl -F "audio=@some_file.mp3" localhost:8080/audio/upload

    """
    response = dict(message='nothing happened', status=400)
    if request.method == 'POST':
        afile = request.files['audio']
        audio_bytes = afile.stream.read()
        response['message'] = ("Received {} bytes of data."
                               .format(len(audio_bytes)))
        response['status'] = 200

    return json.dumps(response)


@app.route('/annotation/submit', methods=['POST'])
def annotation_submit():
    return None


@app.route('/annotation/taxonomy', methods=['GET'])
def annotation_taxonomy():
    tax_url = ("https://raw.githubusercontent.com/marl/jams/master/jams/"
               "schemata/namespaces/tag/medleydb_instruments.json")
    res = urllib2.urlopen(tax_url)
    sdata = res.read()
    tax = None
    if sdata:
        tax = json.loads(sdata)

    return json.dumps(tax)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
