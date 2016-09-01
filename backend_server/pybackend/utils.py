import hashlib
from uuid import UUID


def uuid(data):
    """Create a unique identifier for this entry.

    Parameters
    ----------
    data : str
        Some data to drive a deterministic hash.

    Returns
    -------
    uuid : uuid
        Generated unique identifier.
    """
    if hasattr(data, 'encode'):
        data = data.encode('utf-8')

    hex_data = hashlib.md5(data).hexdigest()
    return UUID(hex=hex_data, version=1)
