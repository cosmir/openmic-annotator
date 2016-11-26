# Open-MIC -- The Open Music Instrument Classification Challenge

[![Build Status](https://travis-ci.org/cosmir/open-mic.svg?branch=master)](https://travis-ci.org/cosmir/open-mic)

## What's going on here?

This is the source repository for the Open-MIC initiative, a community-driven approach to benchmarking content-based MIR algorithms in a transparent and sustainable way.

## Relevant Links

- B. McFee, E. J. Humphrey, and J. Urbano. [A Plan for Sustainable MIR Evaluation](https://wp.nyu.edu/ismir2016/wp-content/uploads/sites/2294/2016/07/257_Paper.pdf) ISMIR 2016. [[slides](http://bmcfee.github.io/slides/ismir2016_eval.pdf)]
- [Developer mailing list](https://groups.google.com/forum/#!forum/open-mic-dev)
- [Users mailing list](https://groups.google.com/forum/#!forum/open-mic-users)

## System Overview

![Content Annotation System Architecture](https://github.com/cosmir/open-mic/raw/master/docs/img/cas_architecture.png "Content Annotation System Architecture")

### Annotation State Diagram
![Annotation State Diagram](https://github.com/cosmir/open-mic/raw/master/docs/img/annotation_state_diagram.png "Annotation State Diagram")

### Roadmap
![Open-MIC Roadmap - v1.2](https://github.com/cosmir/open-mic/raw/master/docs/img/roadmap.png "Open-MIC Roadmap - v1.2")

## Running the components

### Backend Server

#### Running Locally

First, follow the directions to install the [App Engine SDK](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python)

Then, once that's all set, you should be able to do the following from
repository root:

```
$ cd backend_server
$ dev_appserver.py .
```

At this point, the endpoints should be live via localhost:

```
$ curl -X GET localhost:8080/annotation/taxonomy
$ curl -F "audio=@some_file.mp3" localhost:8080/audio/upload
```

#### Deploying to App Engine

For the time being, you will need to create your own App Engine project. To do
so, [follow the directions here](https://console.cloud.google.com/freetrial?redirectPath=/start/appengine).

Once this is configured, make note of your `PROJECT_ID`, because you're going
to need it.

```
$ cd backend_server
$ pip install -t lib -r requirements/setup/requirements_dev.txt
$ appcfg.py -A <PROJECT_ID> -V v1 update .
```

From here, the app should be deployed to the following URL:

```
http://<PROJECT_ID>.appspot.com
```

You can then poke the endpoints as one would expect:

```
$ curl -X GET http://<PROJECT_ID>.appspot.com/annotation/taxonomy
$ curl -F "audio=@some_file.mp3" http://<PROJECT_ID>/audio/upload
```

#### Shutting Down App Engine

After deploying the application, you may wish to shut it down so as to not
ring up unnecessary charges / usage. Proceed to the following URL and click
all the things that say "Shutdown" for maximum certainty:

```
https://console.cloud.google.com/appengine/instances?project=<PROJECT_ID>
```

Be sure to replace <PROJECT_ID> with the appropriate one matching the account
you've configured.

