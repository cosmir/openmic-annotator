"""Client interfaces for local and backend (NoSQL) databases.

Example
-------
>>> import pybackend.database as D
>>> dbase = D.Database(project='my-fun-project',
                       backend=S.LOCAL, filepath='my-db.json',
                       mode=D.APPEND, atomic=True)
>>> key = "my_song"
>>> record = dict(a=15, b=['heya', 'hihi'])
>>> dbase.put(key, record)
>>> print(dbase.get(key))
{'a': 15, 'b': ['heya', 'hihi']}
"""

import json
from google.cloud import datastore
import os

from . import GCLOUD, LOCAL
from . import urilib

# Start clean
WRITE = 'w'
# Load any existing data
APPEND = 'a'
# Immutable / write-safe
READ = 'r'


class LocalClient():
    """A "local" JSON backed database object.

    TODO: Can / could use a slightly smarter backend to easily mimic the
    functionality we'll need (multiple indexing), e.g. pandas, mongo, etc.
    """

    def __init__(self, project, filepath='', mode=APPEND, atomic=True):
        """Create a local database client.

        Parameters
        ----------
        project : str
            Unique identifier for the owner of this storage object.

        filepath : str
            Path on disk for writing the persistent database JSON.

        mode : str, default='a'
            File mode for accessing the "database", one of
             * 'r': read only
             * 'w': write; overwrites the existing file
             * 'a': append; will attempt to add to the current database.

        atomic : bool, default=True
            If True, will flush the database to disk on every `put` operation.
            Trades performance / speed for guarantees that all data is written.
        """
        self._collection = dict()
        self._filepath = filepath
        self.mode = mode
        self.atomic = atomic
        append_conds = [self.mode in [APPEND, READ],
                        os.path.exists(self._filepath)]
        if all(append_conds):
            with open(self._filepath) as fp:
                loaded_items = json.load(fp)
            self._collection.update(**loaded_items)

    def __del__(self):
        if self._collection is not None:
            self.flush()

    def flush(self):
        """Flush all changes to disk."""
        write_conds = [self.mode in [WRITE, APPEND],
                       bool(self._filepath)]
        if all(write_conds):
            with open(self._filepath, 'w') as fp:
                json.dump(self._collection, fp)

    def get(self, uri):
        """Get the record for the given URI."""
        return self._collection.get(uri)

    def put(self, uri, record, atomic=False):
        """Store a record under the given URI.

        Parameters
        ----------
        uri : str
            URI under which to write the record.

        record : dict
            Dictionary object to write.
        """
        # What happens if `uri` is in self._collection?
        self._collection[uri] = record
        if self.atomic or atomic:
            self.flush()

    def delete(self, uri):
        """Delete the record for a given URI.

        Parameters
        ----------
        uri : str
            URI to delete. Passes quietly if URI does not exist.
        """
        if uri in self._collection:
            self._collection.pop(uri)


class GClient(object):
    """Thin wrapper for gcloud's DataStore client.

    Notes:
    - We use a URI format (<kind>:<gid>) to pass DataStore "kinds" around.
      This doesn't allow us to hierarchically nest keys, which DS makes
      possible, but we *probably* won't need to leverage this functionality.
    - The put/get interface for Google's native Datastore client requires
      some wrangling in terms of how Key objects are constructed. This
      interface serves to abstract that behavior away.
    """

    def __init__(self, project):
        """Create a GCP Datastore client.

        Parameters
        ----------
        project : str
            Unique identifier for the owner of this storage object.
        """
        self.project = project

    @property
    def _client(self):
        return datastore.Client(self.project)

    def get(self, uri):
        """Return a record for the given URI."""
        kind, gid = urilib.split(uri)
        key = self._client.key(kind, gid)
        return dict(**self._client.get(key))

    def put(self, uri, record, exclude_from_indexes=None):
        """Put a record into the database."""
        exclude_from_indexes = exclude_from_indexes or []

        # Create Entity from record + key
        kind, gid = urilib.split(uri)
        key = self._client.key(kind, gid)

        entity = datastore.Entity(
            key, exclude_from_indexes=exclude_from_indexes)
        entity.update(record)
        self._client.put(entity)


BACKENDS = {
    GCLOUD: GClient,
    LOCAL: LocalClient
}


def Database(project, backend, **kwargs):
    """Factory constructor for different database backends.

    Parameters
    ----------
    project : str
        Unique identifier for the owner of this storage object.

    backend : str, default='gcloud'
        Backend storage platform to use, one of ['local', 'gcloud'].

    **kwargs : Additional arguments to pass through to the different backends.
    """
    return BACKENDS[backend](project, **kwargs)
