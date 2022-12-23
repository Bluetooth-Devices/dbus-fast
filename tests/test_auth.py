"""This tests setting a hardcoded UID in AuthExternal"""
import os

import pytest

from dbus_fast.auth import AuthExternal


def test_uid_is_set():
    auth = AuthExternal(uid=999)
    assert auth._authentication_start() == "AUTH EXTERNAL 393939"
