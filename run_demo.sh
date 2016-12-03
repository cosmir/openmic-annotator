#!/bin/bash

# Start the backend server
python backend_server/main.py --port 8080 --local --debug &
CMS_PID=$!
sleep 4s

# Ingest the audio data
curl -F "audio=@data/audio/267508__mickleness__3nf.ogg" \
    localhost:8080/api/v0.1/audio

curl -F "audio=@data/audio/345515__furbyguy__strings-piano.ogg" \
    localhost:8080/api/v0.1/audio

sleep 1s
python -m http.server &
HTTP_PID=$!

sleep 1s
# Wait
echo "\n\nAnnotator serving at: http://localhost:8000/docs/annotator.html"
read  -n 1 -p " >> Press any key to exit:\n\n"

# Clean-up
kill $CMS_PID;
kill $HTTP_PID;
