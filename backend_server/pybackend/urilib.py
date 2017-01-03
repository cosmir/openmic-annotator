SEP = ":"


def validate(uri):
    if uri.count(SEP) != 1 or not all(uri.split(SEP)):
        raise ValueError(
            "URI ({}) is malformed; expected `<kind>:<gid>`".format(uri))


def split(uri):
    """Split a URI into an (kind, gid) tuple."""
    validate(uri)
    kind, gid = uri.split(SEP)
    return kind, gid


def join(*data):
    """Join an (kind, gid) tuple into a URI."""
    if len(data) != 2 or any([SEP in v for v in data]):
        raise ValueError(
            "`data` ({}) is malformed; expected `(kind, gid)`".format(data))
    return SEP.join(data)
