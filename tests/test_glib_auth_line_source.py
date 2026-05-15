"""Pre-auth DoS guards for the GLib auth-line source."""

from __future__ import annotations

import io

import pytest

from dbus_fast.errors import AuthError
from dbus_fast.glib.message_bus import _AuthLineSource
from tests.util import check_gi_repository, skip_reason_no_gi

has_gi = check_gi_repository()


@pytest.mark.skipif(not has_gi, reason=skip_reason_no_gi)
def test_auth_line_source_rejects_oversize() -> None:
    stream = io.BytesIO(b"A" * 64 * 1024)
    source = _AuthLineSource(stream)

    captured: list[object] = []

    def callback(arg: object) -> bool:
        captured.append(arg)
        return True

    source.dispatch(callback, None)

    assert len(captured) == 1
    assert isinstance(captured[0], AuthError)


@pytest.mark.skipif(not has_gi, reason=skip_reason_no_gi)
def test_auth_line_source_rejects_eof() -> None:
    stream = io.BytesIO(b"")
    source = _AuthLineSource(stream)

    captured: list[object] = []

    def callback(arg: object) -> bool:
        captured.append(arg)
        return True

    source.dispatch(callback, None)

    assert len(captured) == 1
    assert isinstance(captured[0], AuthError)


@pytest.mark.skipif(not has_gi, reason=skip_reason_no_gi)
def test_auth_line_source_passes_complete_line() -> None:
    stream = io.BytesIO(b"OK 1234\r\n")
    source = _AuthLineSource(stream)

    captured: list[object] = []

    def callback(arg: object) -> bool:
        captured.append(arg)
        return True

    source.dispatch(callback, None)

    assert captured == ["OK 1234"]
