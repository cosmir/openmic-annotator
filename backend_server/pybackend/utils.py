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
    hex_data = hashlib.md5(data.encode('utf-8')).hexdigest()
    return UUID(hex=hex_data, version=1)
