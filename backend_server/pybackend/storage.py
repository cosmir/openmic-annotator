"""Client interfaces for local and backend (binary) data storage.

Example
-------
>>> import pybackend.storage as S
>>> store = S.Storage(name='blah-blah-5678', project_id='my-project-3',
                      backend=S.LOCAL, local_dir="tmp")
>>> key = "my_song"
>>> store.upload(b"never gonna give you up...", key)
>>> print(store.download(key))
b"hello darkness my old friend"
"""

import io
import logging
import os
import warnings

from . import APPENGINE, GCLOUD, LOCAL

# GCloud Backend
try:
    from gcloud import storage
except ImportError:
    warnings.warn("backend:{} unavailable".format(GCLOUD))
    # TODO: This is a punt on fixing the symbol table below. Perhaps a more
    #   "correct" solution is to properly abstract the gcloud datastore client,
    #   but, meh.
    class storage(object):
        Client = None

# AppEngine Backend
try:
    import cloudstorage as gcs
    from google.appengine.api import app_identity
except ImportError:
    gcs = None
    warnings.warn("backend:{} unavailable".format(APPENGINE))


logger = logging.getLogger(__name__)


def _makedirs(dpath):
    if not os.path.exists(dpath):
        os.makedirs(dpath)
    return dpath


class LocalData(object):

    def __init__(self, name, root):
        self.name = name
        self.root = root

    @property
    def path(self):
        return os.path.join(self.root, self.name)


class LocalBlob(LocalData):

    def upload_from_string(self, bstream, content_type):
        """Upload data as a bytestring.

        Parameters
        ----------
        bstream : bytes
            Bytestring to upload.

        content_type : str
            Not used; preserved for consistency with gcloud.storage.
        """
        # obj = dict(bstream=bstream, content_type=content_type)
        with open(self.path, 'wb') as fp:
            fp.write(bstream)

    def download_as_string(self):
        """Upload data as a bytestring.

        Returns
        -------
        bstream : bytes
            Bytestring format of the data.
        """
        with open(self.path, 'rb') as fp:
            fdata = fp.read()
        return fdata


class LocalBucket(LocalData):

    def __init__(self, name, root):
        super(LocalBucket, self).__init__(name, root)

    def blob(self, name):
        return LocalBlob(name, root=_makedirs(self.path))

    def get_blob(self, name):
        return LocalBlob(name, root=self.path)


class LocalClient(object):

    def __init__(self, project_id, root_dir):
        """Create a local storage client.

        Paratmeters
        -----------
        project_id : str
            Unique identifier for the owner of the client.

        root_dir : str, default=None
            A directory on disk for writing binary data.
        """
        self.project_id = project_id
        self.root_dir = _makedirs(root_dir)

    def get_bucket(self, name):
        """Returns a bucket for the given name."""
        return LocalBucket(name=name, root=self.root_dir)


class AppEngineBlob(object):

    def __init__(self, name):
        self.name = name

    def upload_from_string(self, bstream, content_type,
                           options=None, retry_params=None):
        """Upload data as a bytestring.

        Parameters
        ----------
        bstream : bytes
            Bytestring to upload.

        options : dict, default=None
            Options for the file to write, e.g.
              `options={'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'}`

        retry_params : cloudstorage.RetryParams, default=None
            Write retry parameters; defaults to some same values.
        """
        retry_params = retry_params or gcs.RetryParams(initial_delay=0.2,
                                                       max_delay=5.0,
                                                       backoff_factor=1.1,
                                                       max_retry_period=15)
        options = dict() or options
        with gcs.open(self.name, 'w', content_type=content_type,
                      options=options, retry_params=retry_params) as fp:
            fp.write(bstream)

    def download_as_string(self, retry_params=None):
        """Upload data as a bytestring.

        Returns
        -------
        bstream : bytes
            Bytestring format of the data.
        """
        retry_params = retry_params or gcs.RetryParams(initial_delay=0.2,
                                                       max_delay=5.0,
                                                       backoff_factor=1.1,
                                                       max_retry_period=15)

        with gcs.open(self.name, 'r', retry_params=retry_params) as fp:
            fdata = fp.read()
        return fdata


class AppEngineBucket(object):
    def __init__(self, name):
        self.name = '/' + name.strip("/")

    def blob(self, key):
        return AppEngineBlob(os.path.join(self.name, key))

    def get_blob(self, key):
        return self.blob(key)


class AppEngineClient(object):

    def __init__(self, **kwargs):
        pass

    def get_bucket(self, name=None):
        if name is None:
            name = os.environ.get('BUCKET_NAME',
                                  app_identity.get_default_gcs_bucket_name())
        # TODO: Should probably test / make the bucket here?
        return AppEngineBucket(name)


BACKENDS = {
    APPENGINE: AppEngineClient,
    GCLOUD: storage.Client,
    LOCAL: LocalClient
}


class Storage(object):

    def __init__(self, name, project_id, backend=GCLOUD,
                 local_dir=None):
        """Create a storage object.

        Parameters
        ----------
        name : str
            Unique name for the bucket to use, persistent across instances.

        project_id : str
            Unique identifier for the owner of this storage object.

        backend : str, default='gcloud'
            Backend storage platform to use, one of ['local', 'gcloud'].

        local_dir : str, default=None
            A local directory on disk to use for local clients; only used if
            backend='local'.
        """
        if backend == LOCAL and local_dir is None:
            raise ValueError(
                "`local_dir` must be given if backend is '{}'".format(LOCAL))
        self.name = name
        self.project_id = project_id
        self._backend = backend
        self._backend_kwargs = dict(project_id=project_id)
        if self._backend == LOCAL:
            self._backend_kwargs.update(
                root_dir=os.path.abspath(os.path.expanduser(local_dir)))

    @property
    def client(self):
        return BACKENDS[self._backend](**self._backend_kwargs)

    def upload(self, fdata, key):
        """Upload a local file to GCS.

        Parameters
        ----------
        fdata : str
            File's bytestream.

        key : str
            Key for writing the file data.
        """
        logger.debug("Uploading {} bytes to {}.".format(len(fdata), key))
        bucket = self.client.get_bucket(self.name)
        blob = bucket.blob(key)
        blob.upload_from_string(fdata, content_type="application/octet-stream")

    def download(self, key):
        """Retrieve binary data for the given key.

        Parameters
        ----------
        key : str
            Name of the object to retrieve.

        Returns
        -------
        data : bytes
            Binary data.
        """
        bucket = self.client.get_bucket(self.name)
        blob = bucket.get_blob(key)
        return blob.download_as_string()
