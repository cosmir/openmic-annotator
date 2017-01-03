import pytest

import pybackend.urilib as U


def test_validate():
    U.validate("x:y")
    with pytest.raises(ValueError):
        U.validate(":x")

    with pytest.raises(ValueError):
        U.validate("y:")

    with pytest.raises(ValueError):
        U.validate(":")

    with pytest.raises(ValueError):
        U.validate("x:x:y")


def test_split():
    assert U.split("x:y") == ("x", "y")
    with pytest.raises(ValueError):
        U.split(":x")


def test_join():
    assert U.join("x", "y") == "x:y"

    with pytest.raises(ValueError):
        U.join("x")

    with pytest.raises(ValueError):
        U.join("x", "y", "z")

    with pytest.raises(ValueError):
        U.join(":x", "y")
