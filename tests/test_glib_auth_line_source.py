"""Pre-auth DoS guards for the GLib auth-line source."""

from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

import pytest

from dbus_fast.auth import UID_NOT_SPECIFIED, AuthExternal
from dbus_fast.errors import AuthError, AuthTimeoutError
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


@pytest.fixture
def glib_bus() -> MessageBus:
    bus = MessageBus.__new__(MessageBus)
    bus._auth = AuthExternal()
    bus._auth_timeout = None
    bus._fd = -1
    bus._main_context = None
    bus._stream = io.BytesIO()
    return bus


@pytest.mark.skipif(not has_gi, reason=skip_reason_no_gi)
def test_line_notify_forwards_auth_error_to_notify(glib_bus: MessageBus) -> None:
    # When _AuthLineSource hands line_notify an Exception instead of a line
    # (EOF / oversize), line_notify must surface it via authenticate_notify
    # rather than crash.
    bus = glib_bus

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


@pytest.mark.skipif(not has_gi, reason=skip_reason_no_gi)
def test_line_notify_cancels_auth_timeout_when_auth_completes(
    glib_bus: MessageBus,
) -> None:
    """line_notify cancels the GLib timer when auth finishes before the timeout fires."""
    bus = glib_bus
    bus._auth_timeout = 5.0

    captured_line_notify: list[object] = []

    class CapturingSource:
        def __init__(self, stream: object) -> None:
            self.stream = stream

        def set_callback(self, cb: object) -> None:
            captured_line_notify.append(cb)

        def add_unix_fd(self, fd: int, mask: object) -> None:
            pass

        def attach(self, ctx: object) -> None:
            pass

    FAKE_TIMER_ID = 42
    notifications: list[object] = []
    removed_ids: list[int] = []

    # Authentication state is managed with local functions and variables,
    # (as opposed to using instance variables or methods).
    # To confirm behavior, it's necessary to mock a number of methods
    # that are called while the `._authenticate()` method is executing.
    with (
        patch.object(glib_message_bus, "_AuthLineSource", CapturingSource),
        patch.object(glib_message_bus.GLib, "timeout_add", return_value=FAKE_TIMER_ID),
        patch.object(
            glib_message_bus.GLib, "source_remove", side_effect=removed_ids.append
        ),
    ):
        bus._authenticate(lambda exc: notifications.append(exc))
        assert len(captured_line_notify) == 1
        line_notify = captured_line_notify[0]

        err = AuthError("connection closed during authentication")
        line_notify(err)

    assert removed_ids == [FAKE_TIMER_ID], "Expected the timer ID to be removed"
    assert notifications == [err]


@pytest.mark.skipif(not has_gi, reason=skip_reason_no_gi)
def test_authenticate_notifies_on_auth_timeout_errors(glib_bus: MessageBus) -> None:
    """Verify auth timeouts call `authenticate_notify()` if the timeout fires."""
    bus = glib_bus
    bus._readline_source = None
    bus._auth_timeout = 0.05

    notifications = []
    timeout_callbacks = []

    def track_callback(ms, cb) -> int:
        timeout_callbacks.append(cb)
        return 1

    with (
        patch.object(glib_message_bus, "_AuthLineSource", MagicMock()),
        patch.object(glib_message_bus.GLib, "timeout_add", side_effect=track_callback),
    ):
        bus._authenticate(lambda exc: notifications.append(exc))

    error_message = "expected _authenticate to register a GLib timeout"
    assert len(timeout_callbacks) == 1, error_message

    timeout_callbacks[0]()

    assert len(notifications) == 1
    assert isinstance(notifications[0], AuthTimeoutError)


@pytest.mark.skipif(not has_gi, reason=skip_reason_no_gi)
def test_line_notify_keeps_auth_timeout_for_intermediate_lines(
    glib_bus: MessageBus,
) -> None:
    """A non-final auth line leaves the GLib timer armed."""
    bus = glib_bus
    bus._auth = AuthExternal(uid=UID_NOT_SPECIFIED)
    bus._auth_timeout = 5.0
    source = MagicMock()
    removed_ids: list[int] = []

    with (
        patch.object(glib_message_bus, "_AuthLineSource", return_value=source),
        patch.object(glib_message_bus.GLib, "timeout_add", return_value=42),
        patch.object(
            glib_message_bus.GLib, "source_remove", side_effect=removed_ids.append
        ),
    ):
        bus._authenticate(lambda exc: None)
        line_notify = source.set_callback.call_args.args[0]
        assert not line_notify("DATA")
        assert removed_ids == []
        assert line_notify("OK 1234")

    assert removed_ids == [42]


@pytest.mark.skipif(not has_gi, reason=skip_reason_no_gi)
def test_auth_timeout_destroys_readline_source(glib_bus: MessageBus) -> None:
    """The auth timeout detaches the readline source so late replies are ignored."""
    bus = glib_bus
    bus._auth_timeout = 0.05
    source = MagicMock()
    timeout_callbacks = []

    with (
        patch.object(glib_message_bus, "_AuthLineSource", return_value=source),
        patch.object(
            glib_message_bus.GLib,
            "timeout_add",
            side_effect=lambda ms, cb: timeout_callbacks.append(cb) or 1,
        ),
    ):
        bus._authenticate(lambda exc: None)

    assert timeout_callbacks[0]() == GLib.SOURCE_REMOVE
    source.destroy.assert_called_once_with()
    assert bus._readline_source is None
