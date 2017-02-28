# Content Annotation System

This is the source for the backend Flask server, responsible for the following:

- Tracking and uniquely identifying users
- Ingesting source audio
- Building tasks over the ingested database
- Serving tasks on request
- Validating annotation submissions
- Returning user statistics on request


## Annotation State Diagram
![Annotation State Diagram](https://github.com/cosmir/open-mic/raw/master/docs/img/annotation_state_diagram.png "Annotation State Diagram")


## Dependencies

First, install the [App Engine Python SDK](https://developers.google.com/appengine/downloads).

Next, install dependencies in a directory local to this project, e.g. `lib`. App Engine will only be able to import libraries uploaded with the project.

```
$ pip install -r requirements/setup/requirements_dev.txt -t lib
```

## Testing

Having taken care of dependencies, you should be able to run the test suite:

```
$ py.test -v .
```

All tests should pass; halt everything if this is not the case. In all likelihood, failure is the result of a broken / missing dependency, but please create a new issue (with a console log and steps to reproduce) if you believe otherwise.

**Note**: The underlying `google-cloud` library doesn't have the best testing interfaces at the moment; this library is under active development, and hopefully we'll be able to stub out this testing soon. In the meantime, testing is achieved by pinging a live GCP project. To do this, pass a test project flag at the command line:

```
$ TEST_GCP_PROJECT=<YOUR_PROJECT_ID> py.test -v --cov=pybackend tests
```

All affected tests are skipped in the absence of this environment variable.

## Using the CAS machinery

### Running Locally

First, follow the directions to install the [App Engine SDK](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python)

Then, once that's all set, you should be able to do the following from
repository root:

```
$ dev_appserver.py .
```

At this point, the endpoints should be live via localhost (default deployment is to port 8080):

```
$ curl -X GET localhost:8080/annotation/taxonomy
$ curl -F "audio=@some_file.mp3" localhost:8080/audio
```

### Deploying to App Engine

For the time being, you will need to create your own App Engine project. To do
so, [follow the directions here](https://console.cloud.google.com/freetrial?redirectPath=/start/appengine).

Once this is configured, make note of your `PROJECT_ID`, because you're going
to need to pass it through to the deployment script.

```
$ ./deploy.sh <PROJECT_ID>
```

From here, the app should be deployed to the following URL:

```
  http://<PROJECT_ID>.appspot.com
```

You can then poke the endpoints as one would expect:

```
  $ curl -X GET http://<PROJECT_ID>.appspot.com/api/v0.1/annotation/taxonomy
  $ curl -F "audio=@some_file.mp3" http://<PROJECT_ID>/api/v0.1/audio
```


## Shutting Down App Engine

After deploying the application, you may wish to shut it down so as to not ring up unnecessary charges / usage. Proceed to the following URL and click all the things that say "Shutdown" for maximum certainty:

```
  https://console.cloud.google.com/appengine/instances?project=<PROJECT_ID>
```

Be sure to replace `<PROJECT_ID>` with the appropriate one matching the account you've configured.


## OAuth

### Spotify

To configure Spotify to verify OAuth credentials, follow the following steps (assuming you already have a Spotify user account):

- Go to the [developer portal](https://developer.spotify.com/web-api/) and proceed to "My Applications".

- Select "Create an App"; provide it with a human-readable name and description. Note that these will be displayed to a user when authenticating.

- Make note of the "Client ID" and "Client Secret", and store them in a YAML file in this repository. You can use either of the template files in `configs/` as a starter, and you'll want to copy it to the backend root with a leading `.`, e.g. `backend_server/.config.cloud.yaml`).

- For now, set the "Redirect URI" to the following:
  - [http://localhost:8080/login/authorized/spotify](http://localhost:8080/login/authorized/spotify)
  - [http://localhost:8080/login/authorized/spotify?show_dialog=True](http://localhost:8080/login/authorized/spotify?show_dialog=True)

- Make sure you save your changes!

### Google

To configure Google to verify OAuth credentials, follow the following steps (assuming you already have a Google Cloud Platform developer account):

- Go to the GCP console, at https://console.cloud.google.com/, and select "API" from the menu (the infamous "hamburger" button). From the vertical menu tray on the left-hand side, select "Credentials". You can shortcut this by replacing <YOUR_PROJECT> in the following URL:

```
https://console.cloud.google.com/apis/credentials?project=<YOUR_PROJECT>
```

- Select "Create Credentials", and pick "OAuth client ID" from the pop-up menu.

- Select "Web Application" and provide an appropriate name.

- Copy the Client ID and Client Secret to the `google` section of the the OAuth config file. Copy this to the backend root directory, and prefix with a leading `.`, e.g. `backend_server/.config.cloud.yaml`.

- For now, set the redirect URL to [http://localhost:8080/login/authorized/google](http://localhost:8080/login/authorized/google).
