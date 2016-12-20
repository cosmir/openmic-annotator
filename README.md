# Open-MIC -- The Open Music Instrument Classification Challenge

[![Build Status](https://travis-ci.org/cosmir/open-mic.svg?branch=master)](https://travis-ci.org/cosmir/open-mic)

## What's going on here?

This is the source repository for the Open-MIC initiative, a community-driven approach to benchmarking content-based MIR algorithms in a transparent and sustainable way.

**Relevant Links**

- B. McFee, E. J. Humphrey, and J. Urbano. [A Plan for Sustainable MIR Evaluation](https://wp.nyu.edu/ismir2016/wp-content/uploads/sites/2294/2016/07/257_Paper.pdf) ISMIR 2016. [[slides](http://bmcfee.github.io/slides/ismir2016_eval.pdf)]
- [Developer mailing list](https://groups.google.com/forum/#!forum/open-mic-dev)
- [Users mailing list](https://groups.google.com/forum/#!forum/open-mic-users)

## Annotation System Overview

This CAS architecture can be described in the following (approximately) sequential manner, where the corresponding functions are numerated in turn:

![Content Annotation System Architecture](https://github.com/cosmir/open-mic/raw/master/docs/img/cas_architecture.png "Content Annotation System Architecture")

- Uploader: A collection of audio files, with potentially varying signal parameters, are uploaded into the CAS. In doing so, a number of processes are performed per item:
 - A unique universal resource identifier (URI) is generated.
 - The signal is normalized to a common set of parameters / encoding scheme.
 - Normalized audio data is saved to a binary storage platform with that URI.
 - A record of the audio entity is created and stored under that URI in a database.
- Task Builder: Having creating a normalized, uniquely identified collection, a number of annotation “tasks” are created, whereby the following occurs for each:
 - An audio URI is selected.
 - A N-second “clip” is trimmed from the corresponding audio and imported as a new audio item with appropriate metadata.
 - A new task record is initialized with the clip’s URI and empty state, and stored in a database.
- Annotation: Tasks are served to a web-based annotation tool guided by some backend logic, where users select and submit the music instrument tags recognized.
 - A user registers with the CAS, creating a new user record initialized with a unique URI and empty state, and stored in a database.
 - A user logs into the CAS by providing the appropriate credentials.
 - The annotation front-end requests a task from the server, providing the current user’s information.
 - Audio is rendered in the browser; the user can play the audio any number of times, selecting the music instrument tags deemed relevant.
 - The user attempts to submit their observations; the annotation front-end will accept or reject the response based on the task data received.
 - On occasion, the user is presented with individual and global statistics related to the initiative’s progress.
- Dataset Compiler: Based on the the state of the task collection, a labeled “training” set (audio and instrument tags) and unlabeled “test” (audio only) set are exported from the CAS.
 - The task collection is reviewed, whereby a number of records are deemed “complete.”
 - A randomized subset of complete items are exported as audio clips and labels, under the clip URIs, as the training set.
 - A randomized subset of items from the remaining collection are exported, without labels, as the test set.
 - The URIs for both sets are logged for posterity.

### Roadmap

Here is a rough projection of the timeline for progress on the Open-MIC project, as detailed above:

![Open-MIC Roadmap - v1.2](https://github.com/cosmir/open-mic/raw/master/docs/img/roadmap.png "Open-MIC Roadmap - v1.2")


## Running the annotation machinery locally

The easiest way to get started is to run the demo at the commandline:

```
   $ ./run_demo.sh
```

This will start the backend server (CMS), upload a few audio files, and begin serving the audio annotation tool locally. By default this will appear at [http://localhost:8000/docs/annotator.html](http://localhost:8000/docs/annotator.html).

**Notes**:
- It is **strongly** recommended that a private / incognito session is used for demo purposes. Caching behavior in normal browser sessions can cause significant headaches.
- For some reason, loading the audio seems to get "stuck" on occasion. To unblock it, manually proceed to an audio file's URL once the server is running, e.g. [http://localhost:8080/api/v0.1/audio/740c835f-a23d-41ef-b84c-0cd1de4edfa5](http://localhost:8080/api/v0.1/audio/740c835f-a23d-41ef-b84c-0cd1de4edfa5).

Alternatively, instructions for running the different parts of the system are listed below.

### Content Management System

See the [ReadMe](https://github.com/cosmir/open-mic/blob/master/backend_server/README.md) for details on running the backend web server.

### Audio annotator

If this is your first time checking out this repository, you'll need to pull in external
dependencies by saying

    git submodule update --init

after cloning the repository.
