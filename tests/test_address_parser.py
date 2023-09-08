import os
from unittest.mock import patch

import pytest

from dbus_fast._private.address import (
    get_bus_address,
    get_session_bus_address,
    get_system_bus_address,
    parse_address,
)
from dbus_fast.constants import BusType
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


def test_get_system_bus_address():
    with patch.dict(os.environ, DBUS_SYSTEM_BUS_ADDRESS="unix:path=/dog"):
        assert get_system_bus_address() == "unix:path=/dog"
        assert get_bus_address(BusType.SYSTEM) == "unix:path=/dog"
    with patch.dict(os.environ, DBUS_SYSTEM_BUS_ADDRESS=""):
        assert get_system_bus_address() == "unix:path=/var/run/dbus/system_bus_socket"


def test_get_session_bus_address():
    with patch.dict(os.environ, DBUS_SESSION_BUS_ADDRESS="unix:path=/dog"):
        assert get_session_bus_address() == "unix:path=/dog"
        assert get_bus_address(BusType.SESSION) == "unix:path=/dog"
    with patch.dict(os.environ, DBUS_SESSION_BUS_ADDRESS="", DISPLAY=""), pytest.raises(
        InvalidAddressError
    ):
        assert get_session_bus_address()
