import os
from unittest.mock import mock_open, patch

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
    with (
        patch.dict(os.environ, DBUS_SESSION_BUS_ADDRESS="", DISPLAY=""),
        pytest.raises(InvalidAddressError),
    ):
        assert get_session_bus_address()


def test_invalid_bus_address():
    with pytest.raises(Exception):
        assert get_bus_address(-1)


def test_session_bus_address_missing_display_raises():
    """Without DBUS_SESSION_BUS_ADDRESS and without DISPLAY, raise."""
    env = {k: v for k, v in os.environ.items() if k not in ("DBUS_SESSION_BUS_ADDRESS", "DISPLAY")}
    with patch.dict(os.environ, env, clear=True), pytest.raises(InvalidAddressError) as exc:
        get_session_bus_address()
    assert "DISPLAY" in str(exc.value)


def test_session_bus_address_unparseable_display_raises():
    """A DISPLAY value that doesn't match the regex must raise InvalidAddressError."""
    with (
        patch.dict(os.environ, DBUS_SESSION_BUS_ADDRESS="", DISPLAY="not-a-display"),
        pytest.raises(InvalidAddressError) as exc,
    ):
        get_session_bus_address()
    assert "DISPLAY" in str(exc.value)


def _fake_open_factory(file_contents: dict[str, str]):
    """Build a fake ``open`` that returns content based on path lookup."""
    real_open = open

    def fake_open(path, *args, **kwargs):
        if path in file_contents:
            return mock_open(read_data=file_contents[path]).return_value
        return real_open(path, *args, **kwargs)

    return fake_open


def test_session_bus_address_from_dbus_info_file(tmp_path):
    """Happy path: DISPLAY set, machine-id + dbus info file readable."""
    machine_id = "abc123"
    display = ":0"
    home = str(tmp_path)
    expected_addr = "unix:abstract=/tmp/dbus-XYZ"
    info_path = f"{home}/.dbus/session-bus/{machine_id}-0"
    files = {
        "/var/lib/dbus/machine-id": machine_id + "\n",
        info_path: f"# comment\nDBUS_SESSION_BUS_ADDRESS={expected_addr}\nOTHER=foo\n",
    }
    with (
        patch.dict(
            os.environ,
            DBUS_SESSION_BUS_ADDRESS="",
            DISPLAY=display,
            HOME=home,
        ),
        patch("builtins.open", _fake_open_factory(files)),
    ):
        assert get_session_bus_address() == expected_addr


def test_session_bus_address_strips_quotes_around_address(tmp_path):
    """Quoted DBUS_SESSION_BUS_ADDRESS values are unquoted."""
    machine_id = "abc123"
    home = str(tmp_path)
    info_path = f"{home}/.dbus/session-bus/{machine_id}-0"
    files = {
        "/var/lib/dbus/machine-id": machine_id,
        info_path: 'DBUS_SESSION_BUS_ADDRESS="unix:path=/tmp/socket"\n',
    }
    with (
        patch.dict(
            os.environ,
            DBUS_SESSION_BUS_ADDRESS="",
            DISPLAY="hostname:0.0",
            HOME=home,
        ),
        patch("builtins.open", _fake_open_factory(files)),
    ):
        assert get_session_bus_address() == "unix:path=/tmp/socket"


def test_session_bus_address_info_file_missing_raises(tmp_path):
    """If the dbus info file does not exist, raise InvalidAddressError."""
    machine_id = "abc123"
    home = str(tmp_path)
    files = {"/var/lib/dbus/machine-id": machine_id}
    with (
        patch.dict(
            os.environ,
            DBUS_SESSION_BUS_ADDRESS="",
            DISPLAY=":0",
            HOME=home,
        ),
        patch("builtins.open", _fake_open_factory(files)),
        pytest.raises(InvalidAddressError) as exc,
    ):
        get_session_bus_address()
    assert "dbus info file" in str(exc.value)


def test_session_bus_address_info_file_empty_value_raises(tmp_path):
    """An empty DBUS_SESSION_BUS_ADDRESS= line in the info file must raise."""
    machine_id = "abc123"
    home = str(tmp_path)
    info_path = f"{home}/.dbus/session-bus/{machine_id}-0"
    files = {
        "/var/lib/dbus/machine-id": machine_id,
        info_path: "DBUS_SESSION_BUS_ADDRESS=\n",
    }
    with (
        patch.dict(
            os.environ,
            DBUS_SESSION_BUS_ADDRESS="",
            DISPLAY=":0",
            HOME=home,
        ),
        patch("builtins.open", _fake_open_factory(files)),
        pytest.raises(InvalidAddressError) as exc,
    ):
        get_session_bus_address()
    assert "not set correctly" in str(exc.value)


def test_session_bus_address_info_file_missing_address_line_raises(tmp_path):
    """An info file without a DBUS_SESSION_BUS_ADDRESS line must raise."""
    machine_id = "abc123"
    home = str(tmp_path)
    info_path = f"{home}/.dbus/session-bus/{machine_id}-0"
    files = {
        "/var/lib/dbus/machine-id": machine_id,
        info_path: "OTHER=value\n# nothing useful\n",
    }
    with (
        patch.dict(
            os.environ,
            DBUS_SESSION_BUS_ADDRESS="",
            DISPLAY=":0",
            HOME=home,
        ),
        patch("builtins.open", _fake_open_factory(files)),
        pytest.raises(InvalidAddressError) as exc,
    ):
        get_session_bus_address()
    assert "could not find" in str(exc.value)
