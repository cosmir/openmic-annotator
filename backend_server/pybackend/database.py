"""Client interfaces for local and backend (NoSQL) databases.

Example
-------
>>> import pybackend.database as D
>>> dbase = D.Database(project_id='my-fun-project',
                       backend=S.LOCAL, filepath='my-db.json',
                       mode=D.APPEND, atomic=True)
>>> key = "my_song"
>>> record = dict(a=15, b=['heya', 'hihi'])
>>> dbase.put(key, record)
>>> print(dbase.get(key))
{'a': 15, 'b': ['heya', 'hihi']}
"""

import json
from gcloud import datastore
import os

from . import GCLOUD, LOCAL

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

    def __init__(self, project_id, filepath='', mode=APPEND, atomic=True):
        """Create a local database client.

        Parameters
        ----------
        project_id : str
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

    def get(self, key):
        """Get the record for the given key."""
        return self._collection.get(key)

    def put(self, key, record):
        """Store a record under the given key.

        TODO(ejhumphrey): Call signature is backwards with the storage client;
        should harmonize.

        Parameters
        ----------
        key : str
            Key under which to write the record.

        record : dict
            Dictionary object to write.
        """
        # What happens if `key` is in self._collection?
        self._collection[key] = record
        if self.atomic:
            self.flush()

    def delete(self, key):
        """Delete the record for a given key.

        Parameters
        ----------
        key : str
            Key to delete. Passes quietly if key does not exist.
        """
        if key in self._collection:
            self._collection.pop(key)


class GClient(object):
    """Thin wrapper for gcloud's DataStore client.

    TODO(ejhumphrey):
     * Currently unclear how to plumb entity "kinds" through this abstraction.
     * The put/get interface for Google's native Datastore client requires
       some wrangling in terms of how Key objects are constructed. This
       interface serves to abstract that behavior away.
    """

    def __init__(self, project_id):
        """Create a GCP Datastore client.

        Parameters
        ----------
        project_id : str
            Unique identifier for the owner of this storage object.
        """
        self.project_id = project_id

    @property
    def _client(self):
        return datastore.Client(self.project_id)

    def get(self, key):
        """TODO(ejhumphrey): writeme"""
        raise NotImplementedError("Placeholder, needs revisiting.")
        key = self._client.key("key", key)
        return self._client.get(key)

    def put(self, key, record):
        """TODO(ejhumphrey): writeme"""
        raise NotImplementedError("Placeholder, needs revisiting.")
        # Create Entity from record + key
        key = self._client.key("key", key)
        entity = datastore.Entity(key, exclude_from_indexes=[])
        entity.update(record)
        self._client.put(entity)


BACKENDS = {
    GCLOUD: GClient,
    LOCAL: LocalClient
}


def Database(project_id, backend, **kwargs):
    """Factory constructor for different database backends.

    Parameters
    ----------
    project_id : str
        Unique identifier for the owner of this storage object.

    backend : str, default='gcloud'
        Backend storage platform to use, one of ['local', 'gcloud'].

    **kwargs : Additional arguments to pass through to the different backends.
    """
    return BACKENDS[backend](project_id, **kwargs)
