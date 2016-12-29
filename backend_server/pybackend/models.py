import copy
import json


class BaseRecord(dict):
    """Data model for records in the database.

    Database technologies in use cannot handle nested objects. Records exist
    to flatten / expand nested fields through JSON serialization.

    To subclass, specify the keys to flatten / expand via the `serialized_keys`
    class variable.
    """
    serialized_keys = []

    def flatten(self):
        """Return a flattened view of the object."""
        obj = copy.deepcopy(self)
        obj.update(**{k: json.dumps(v) for k, v in obj.items()
                      if k in self.serialized_keys})
        return obj

    @classmethod
    def from_flat(cls, **kwargs):
        """Create a record from a set of flattened key-value data."""
        kwargs.update(**{k: json.loads(v) for k, v in kwargs.items()
                         if k in cls.serialized_keys})
        return cls(**kwargs)


class AnnotationResponse(BaseRecord):
    serialized_keys = ['response']
