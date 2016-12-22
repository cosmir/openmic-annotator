import copy
import json


class Record(dict):
    """
    """
    def __init__(self, serialized_keys=None):
        self.serialized_keys = serialized_keys or []

    def flatten(self):
        obj = copy.deepcopy(self)
        obj.update(**{k: json.dumps(v) for k, v in obj.items()
                      if k in self.serialized_keys})
        return obj

    def expand(self, **kwargs):
        kwargs.update(**{k: json.loads(v) for k, v in kwargs.items()
                      if k in self.serialized_keys})
        self.update(**kwargs)
