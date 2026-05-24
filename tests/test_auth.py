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
def test_receive_line_unknown_response_raises_auth_error(line):
    """An unrecognized server keyword surfaces as AuthError, not ValueError."""
    auth = AuthExternal(uid=UID_NOT_SPECIFIED)
    with pytest.raises(AuthError):
        auth._receive_line(line)
