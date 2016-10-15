# Content Management Backend Server

This is the source for content management system designed to be deployed on Google App Engine or run locally for testing.


## Running Locally

1. Install the [App Engine Python SDK](https://developers.google.com/appengine/downloads).

2. Install dependencies in a directory local to this project, e.g. `lib`. App Engine will only be able to import libraries uploaded with the project.

```
$ pip install -r requirements/setup/requirements_dev.txt -t lib
```

3. Run this project locally from the command line:
```
$ dev_appserver.py .
```

## Testing

At this point, you should be able to run the test suite:

```
$ py.test -v .
```


