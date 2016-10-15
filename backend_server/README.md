# Content Management Backend Server

This is the source for content management system designed to be deployed on Google App Engine or run locally for testing.


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


## Running Locally

You can now run this project locally from the command line:

```
$ dev_appserver.py .
```

The endpoints should now be live via `localhost` (default deployment is to port 8080):

```
  $ curl -X GET localhost:8080/annotation/taxonomy
  $ curl -F "audio=@some_file.mp3" localhost:8080/audio/upload
```


## Deploying to App Engine

`TODO(ejhumphrey):` Is it possible to have pre-deployment testing hooks? If so, that should be documented here.

For the time being, you will need to create your own App Engine project. To do so, follow the directions here:

```
  https://console.cloud.google.com/freetrial?redirectPath=/start/appengine
```

Once this is configured, make note of your `PROJECT_ID`, because you're going to need it.

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


## Shutting Down App Engine

After deploying the application, you may wish to shut it down so as to not ring up unnecessary charges / usage. Proceed to the following URL and click all the things that say "Shutdown" for maximum certainty:

```
  https://console.cloud.google.com/appengine/instances?project=<PROJECT_ID>
```

Be sure to replace `<PROJECT_ID>` with the appropriate one matching the account you've configured.


