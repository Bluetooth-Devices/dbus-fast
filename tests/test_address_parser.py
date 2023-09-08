import pytest

from dbus_fast._private.address import parse_address
from dbus_fast.errors import InvalidAddressError


def test_valid_addresses():
    valid_addresses = {
        "unix:path=/run/user/1000/bus": [("unix", {"path": "/run/user/1000/bus"})],
        "unix:abstract=/tmp/dbus-ft9sODWpZk,guid=a7b1d5912379c2d471165e9b5cb74a03": [
            (
                "unix",
                {
                    "abstract": "/tmp/dbus-ft9sODWpZk",
                    "guid": "a7b1d5912379c2d471165e9b5cb74a03",
                },
            )
        ],
        "unix1:key1=val1;unix2:key2=val2": [
            ("unix1", {"key1": "val1"}),
            ("unix2", {"key2": "val2"}),
        ],
        "unix:escaped=hello%20world": [("unix", {"escaped": "hello world"})],
        "tcp:host=127.0.0.1,port=55556": [
            ("tcp", {"host": "127.0.0.1", "port": "55556"})
        ],
        "unix:tmpdir=/tmp,;": [("unix", {"tmpdir": "/tmp"})],
    }

    for address, parsed in valid_addresses.items():
        assert parse_address(address) == parsed


def test_invalid_addresses():
    with pytest.raises(InvalidAddressError):
        assert parse_address("")
    with pytest.raises(InvalidAddressError):
        assert parse_address("unix")
    with pytest.raises(InvalidAddressError):
        assert parse_address("unix:tmpdir")
    with pytest.raises(InvalidAddressError):
        assert parse_address("unix:tmpdir=😁")
