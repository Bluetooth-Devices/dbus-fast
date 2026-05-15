import os
from pathlib import Path
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
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("DBUS_SESSION_BUS_ADDRESS", "DISPLAY")
    }
    with (
        patch.dict(os.environ, env, clear=True),
        pytest.raises(InvalidAddressError, match=r"DISPLAY"),
    ):
        get_session_bus_address()


def test_session_bus_address_unparseable_display_raises():
    """A DISPLAY value that doesn't match the regex must raise InvalidAddressError."""
    with (
        patch.dict(os.environ, DBUS_SESSION_BUS_ADDRESS="", DISPLAY="not-a-display"),
        pytest.raises(InvalidAddressError, match=r"DISPLAY"),
    ):
        get_session_bus_address()


def _read_real_machine_id() -> str:
    """Return the host's real ``/var/lib/dbus/machine-id`` or skip the test."""
    try:
        with open("/var/lib/dbus/machine-id") as f:
            return f.read().rstrip()
    except OSError:
        pytest.skip("/var/lib/dbus/machine-id is not available on this host")


def _write_info_file(home: Path, machine_id: str, display_num: str, content: str) -> Path:
    info_path = home / ".dbus" / "session-bus" / f"{machine_id}-{display_num}"
    info_path.parent.mkdir(parents=True, exist_ok=True)
    info_path.write_text(content)
    return info_path


def test_session_bus_address_from_dbus_info_file(tmp_path):
    """Happy path: DISPLAY set, real machine-id, info file under HOME readable."""
    machine_id = _read_real_machine_id()
    expected_addr = "unix:abstract=/tmp/dbus-XYZ"
    _write_info_file(
        tmp_path,
        machine_id,
        "0",
        f"# comment\nDBUS_SESSION_BUS_ADDRESS={expected_addr}\nOTHER=foo\n",
    )
    with patch.dict(
        os.environ,
        DBUS_SESSION_BUS_ADDRESS="",
        DISPLAY=":0",
        HOME=str(tmp_path),
    ):
        assert get_session_bus_address() == expected_addr


def test_session_bus_address_strips_quotes_around_address(tmp_path):
    """Quoted DBUS_SESSION_BUS_ADDRESS values are unquoted."""
    machine_id = _read_real_machine_id()
    _write_info_file(
        tmp_path,
        machine_id,
        "0",
        'DBUS_SESSION_BUS_ADDRESS="unix:path=/tmp/socket"\n',
    )
    with patch.dict(
        os.environ,
        DBUS_SESSION_BUS_ADDRESS="",
        DISPLAY="hostname:0.0",
        HOME=str(tmp_path),
    ):
        assert get_session_bus_address() == "unix:path=/tmp/socket"


def test_session_bus_address_info_file_missing_raises(tmp_path):
    """If the dbus info file does not exist, raise InvalidAddressError."""
    _read_real_machine_id()
    with (
        patch.dict(
            os.environ,
            DBUS_SESSION_BUS_ADDRESS="",
            DISPLAY=":0",
            HOME=str(tmp_path),
        ),
        pytest.raises(InvalidAddressError, match=r"could not open dbus info file"),
    ):
        get_session_bus_address()


def test_session_bus_address_info_file_empty_value_raises(tmp_path):
    """An empty DBUS_SESSION_BUS_ADDRESS= line in the info file must raise."""
    machine_id = _read_real_machine_id()
    _write_info_file(tmp_path, machine_id, "0", "DBUS_SESSION_BUS_ADDRESS=\n")
    with (
        patch.dict(
            os.environ,
            DBUS_SESSION_BUS_ADDRESS="",
            DISPLAY=":0",
            HOME=str(tmp_path),
        ),
        pytest.raises(InvalidAddressError, match=r"not set correctly"),
    ):
        get_session_bus_address()


def test_session_bus_address_info_file_missing_address_line_raises(tmp_path):
    """An info file without a DBUS_SESSION_BUS_ADDRESS line must raise."""
    machine_id = _read_real_machine_id()
    _write_info_file(tmp_path, machine_id, "0", "OTHER=value\n# nothing useful\n")
    with (
        patch.dict(
            os.environ,
            DBUS_SESSION_BUS_ADDRESS="",
            DISPLAY=":0",
            HOME=str(tmp_path),
        ),
        pytest.raises(InvalidAddressError, match=r"could not find"),
    ):
        get_session_bus_address()
