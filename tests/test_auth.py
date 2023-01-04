"""This tests setting a hardcoded UID in AuthExternal"""
import os

import pytest

from dbus_fast.auth import AuthExternal, UID_NOT_SPECIFIED


def test_uid_is_set():
    auth = AuthExternal(uid=999)
    assert auth._authentication_start() == "AUTH EXTERNAL 393939"


def test_no_uid():
    auth = AuthExternal(uid=UID_NOT_SPECIFIED)
    assert auth._authentication_start() == "AUTH EXTERNAL"
    assert auth._receive_line("DATA") == "DATA"
