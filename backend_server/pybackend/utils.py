import hashlib
from uuid import UUID


def uuid(data):
    """Create a unique (deterministic) identifier.

    Parameters
    ----------
    data : str
        Some data to drive a deterministic hash.

    Returns
    -------
    uuid : uuid
        Generated unique identifier.
    """
    if isinstance(data, str):
        data = bytes(data)

    hex_data = hashlib.md5(data).hexdigest()
    return UUID(hex=hex_data, version=4)
