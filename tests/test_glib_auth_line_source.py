"""Pre-auth DoS guards for the GLib auth-line source."""

from __future__ import annotations

import io

import pytest

from dbus_fast.auth import AuthExternal
from dbus_fast.errors import AuthError
from dbus_fast.glib import message_bus as glib_message_bus
from dbus_fast.glib.message_bus import MessageBus, _AuthLineSource
from tests.util import check_gi_repository, skip_reason_no_gi

has_gi = check_gi_repository()

if has_gi:
    from gi.repository import GLib


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
def test_auth_line_source_rejects_invalid_utf8() -> None:
    stream = io.BytesIO(b"OK \xff\xfe\r\n")
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


@pytest.mark.skipif(not has_gi, reason=skip_reason_no_gi)
def test_auth_line_source_continues_when_read_returns_none() -> None:
    # Non-blocking reads can return None when no data is ready; dispatch
    # must keep the source attached rather than treat that as EOF.
    class NoneStream:
        def read(self) -> None:
            return None

    source = _AuthLineSource(NoneStream())

    captured: list[object] = []

    def callback(arg: object) -> bool:
        captured.append(arg)
        return True

    result = source.dispatch(callback, None)

    assert captured == []
    assert result == GLib.SOURCE_CONTINUE


@pytest.mark.skipif(not has_gi, reason=skip_reason_no_gi)
def test_line_notify_forwards_auth_error_to_notify() -> None:
    # When _AuthLineSource hands line_notify an Exception instead of a line
    # (EOF / oversize), line_notify must surface it via authenticate_notify
    # rather than crash.
    bus = MessageBus.__new__(MessageBus)
    bus._auth = AuthExternal()
    bus._fd = -1
    bus._main_context = None

    class FakeStream:
        def __init__(self) -> None:
            self.written = bytearray()

        def write(self, data: bytes) -> int:
            self.written.extend(data)
            return len(data)

        def flush(self) -> None:
            pass

    bus._stream = FakeStream()

    captured_callbacks: list[object] = []

    class CapturingSource:
        def __init__(self, stream: object) -> None:
            self.stream = stream

        def set_callback(self, cb: object) -> None:
            captured_callbacks.append(cb)

        def add_unix_fd(self, fd: int, mask: object) -> None:
            pass

        def attach(self, ctx: object) -> None:
            pass

    notifications: list[object] = []

    def notify(exc: object) -> None:
        notifications.append(exc)

    original = glib_message_bus._AuthLineSource
    glib_message_bus._AuthLineSource = CapturingSource
    try:
        bus._authenticate(notify)
    finally:
        glib_message_bus._AuthLineSource = original

    assert len(captured_callbacks) == 1
    line_notify = captured_callbacks[0]

    err = AuthError("connection closed during authentication")
    result = line_notify(err)

    assert notifications == [err]
    assert result is True
