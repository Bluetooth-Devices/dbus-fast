"""This tests setting a hardcoded UID in AuthExternal"""

import pytest

from dbus_fast.auth import (
    UID_NOT_SPECIFIED,
    AuthAnnonymous,
    AuthAnonymous,
    AuthExternal,
)
from dbus_fast.errors import AuthError


def test_annonymous_backcompat():
    auth = AuthAnnonymous()
    assert isinstance(auth, AuthAnonymous)


def test_auth_anonymous_start():
    auth = AuthAnonymous()
    assert auth._authentication_start() == "AUTH ANONYMOUS"


def test_auth_anonymous_rejects_unix_fd_negotiation():
    auth = AuthAnonymous()
    with pytest.raises(AuthError):
        auth._authentication_start(negotiate_unix_fd=True)


def test_auth_anonymous_ok_begins():
    auth = AuthAnonymous()
    assert auth._receive_line("OK 1234deadbeef") == "BEGIN"


def test_auth_anonymous_rejected_raises():
    auth = AuthAnonymous()
    with pytest.raises(AuthError):
        auth._receive_line("REJECTED EXTERNAL")


def test_uid_is_set():
    auth = AuthExternal(uid=999)
    assert auth._authentication_start() == "AUTH EXTERNAL 393939"


def test_auth_external_no_uid():
    """Test AuthExternal with UID_NOT_SPECIFIED"""
    auth = AuthExternal(uid=UID_NOT_SPECIFIED)
    assert auth._authentication_start() == "AUTH EXTERNAL"
    assert auth._receive_line("DATA") == "DATA"
    with pytest.raises(AuthError):
        auth._receive_line("REJECTED")


@pytest.mark.parametrize("line", ["GARBAGE", "", "REJECTED\tfoo"])
@pytest.mark.parametrize("expected", [AuthError, ValueError])
def test_receive_line_unknown_response_raises_auth_error(line, expected):
    """An unrecognized server keyword raises AuthError, which is also a ValueError."""
    auth = AuthExternal(uid=UID_NOT_SPECIFIED)
    with pytest.raises(expected):
        auth._receive_line(line)
