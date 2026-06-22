import asyncio
import socket

import pytest

from dbus_fast import introspection as intr
from dbus_fast.aio import MessageBus
from dbus_fast.constants import (
    ErrorType,
    MessageFlag,
    MessageType,
    NameFlag,
    ReleaseNameReply,
    RequestNameReply,
)
from dbus_fast.errors import AuthError, DBusError, InternalError, InvalidAddressError
from dbus_fast.message import Message
from dbus_fast.message_bus import BaseMessageBus, _expects_reply


@pytest.mark.asyncio
async def test_tcp_socket_cleanup_on_connect_fail() -> None:
    """Test that socket resources are cleaned up on a failed TCP connection."""
    bus = MessageBus("tcp:host=127.0.0.1,port=1")

    with pytest.raises(ConnectionRefusedError, match=r".*"):
        await bus.connect()

    assert bus._stream is None
    assert bus._sock is None


@pytest.mark.asyncio
async def test_unix_socket_cleanup_on_connect_fail() -> None:
    """Test that socket resources are cleaned up on a failed Unix socket connection."""
    bus = MessageBus("unix:path=/there-is-no-way-that-this-file-should-exist")

    with pytest.raises(FileNotFoundError, match=r".*"):
        await bus.connect()

    assert bus._stream is None
    assert bus._sock is None


@pytest.mark.asyncio
async def test_tcp_socket_cleanup_with_host_only() -> None:
    """Test TCP connection with host option only (no port)."""
    bus = MessageBus("tcp:host=127.0.0.1")

    with pytest.raises(OSError, match=r".*"):
        # Port defaults to 0, which will fail
        await bus.connect()

    assert bus._stream is None
    assert bus._sock is None


@pytest.mark.asyncio
async def test_tcp_socket_cleanup_with_port_only() -> None:
    """Test TCP connection with port option only (no host)."""
    bus = MessageBus("tcp:port=1")

    with pytest.raises(OSError, match=r".*"):
        # Host defaults to empty string, which will fail
        await bus.connect()

    assert bus._stream is None
    assert bus._sock is None


@pytest.mark.asyncio
async def test_unix_socket_abstract_cleanup_on_connect_fail() -> None:
    """Test that socket resources are cleaned up on a failed abstract Unix socket connection."""
    bus = MessageBus("unix:abstract=/tmp/nonexistent-abstract-socket")

    # On Linux: ConnectionRefusedError, on macOS: FileNotFoundError
    with pytest.raises((FileNotFoundError, ConnectionRefusedError)):
        await bus.connect()

    assert bus._stream is None
    assert bus._sock is None


@pytest.mark.asyncio
async def test_unix_socket_invalid_path_specifier() -> None:
    """Test that Unix socket with invalid path specifier raises error."""
    bus = MessageBus("unix:invalid=foo")

    with pytest.raises(
        InvalidAddressError, match="got unix transport with unknown path specifier"
    ):
        await bus.connect()


@pytest.mark.asyncio
async def test_unknown_socket_type() -> None:
    """Test that unknown socket types raise InvalidAddressError."""
    bus = MessageBus("unknown:works=nope")

    with pytest.raises(InvalidAddressError, match="got unknown address transport"):
        await bus.connect()


@pytest.mark.asyncio
async def test_tcp_socket_non_integer_port() -> None:
    """A non-integer tcp port option is reported as InvalidAddressError."""
    bus = MessageBus("tcp:host=127.0.0.1,port=not-a-number")

    with pytest.raises(
        InvalidAddressError, match="got tcp transport with invalid port"
    ):
        await bus.connect()


@pytest.mark.asyncio
async def test_aio_connect_falls_back_between_transports() -> None:
    """If the first transport fails, aio connect() tries the next one and
    raises the last error if all fail.
    """
    bus = MessageBus(
        "unix:path=/there-is-no-way-that-this-file-should-exist;"
        "tcp:host=127.0.0.1,port=1"
    )

    with pytest.raises(ConnectionRefusedError, match=r".*"):
        await bus.connect()

    assert bus._stream is None
    assert bus._sock is None


@pytest.mark.asyncio
async def test_aio_connect_cleanup_after_socket_connected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failure after the socket is connected clears _sock/_stream/_fd/_writer."""
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    host, port = listener.getsockname()
    try:

        async def _boom(self: MessageBus) -> None:
            raise AuthError("simulated auth failure")

        monkeypatch.setattr(MessageBus, "_authenticate", _boom)

        bus = MessageBus(f"tcp:host={host},port={port}")

        with pytest.raises(AuthError, match="simulated auth failure"):
            await bus.connect()

        assert bus._sock is None
        assert bus._stream is None
        assert bus._fd is None
        assert bus._writer is None
    finally:
        listener.close()


@pytest.mark.parametrize(
    ("transport", "options", "family"),
    [
        ("unix", {"path": "/nope"}, socket.AF_UNIX),
        ("tcp", {"host": "127.0.0.1", "port": "1"}, socket.AF_INET),
    ],
    ids=["unix", "tcp"],
)
def test_create_socket_for_transport_makefile_failure_closes_socket(
    monkeypatch: pytest.MonkeyPatch,
    transport: str,
    options: dict[str, str],
    family: int,
) -> None:
    """A makefile() failure closes the socket before re-raising."""
    closed: list[int] = []
    real_close = socket.socket.close

    def tracking_close(self: socket.socket) -> None:
        closed.append(self.family)
        real_close(self)

    def boom(self: socket.socket, *args: object, **kwargs: object) -> None:
        raise OSError("makefile failed")

    monkeypatch.setattr(socket.socket, "close", tracking_close)
    monkeypatch.setattr(socket.socket, "makefile", boom)

    with pytest.raises(OSError, match="makefile failed"):
        BaseMessageBus._create_socket_for_transport(transport, options)

    assert family in closed


def test_get_proxy_object_raises_when_proxy_object_class_missing() -> None:
    # ProxyObject defaults to None on BaseMessageBus, which is the condition
    # under test. Passing an explicit bus_address avoids depending on
    # DBUS_SESSION_BUS_ADDRESS in the environment.
    bus = BaseMessageBus(bus_address="unix:path=/dev/null")
    with pytest.raises(InternalError, match=r"did not provide a proxy object class"):
        bus.get_proxy_object("com.example.Test", "/com/example/Test", "<node/>")


@pytest.mark.asyncio
async def test_aio_connect_hello_error_propagates_and_clears_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """on_hello with an error reply tears down sock/stream/fd/writer."""
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    host, port = listener.getsockname()
    try:

        async def _auth_noop(self: MessageBus) -> None:
            return

        monkeypatch.setattr(MessageBus, "_authenticate", _auth_noop)

        bus = MessageBus(f"tcp:host={host},port={port}")
        # Force next_serial() to return 2 so the else-branch that calls
        # _generate_hello_serialized() is exercised instead of the cached
        # HELLO_1_SERIALIZED constant.
        bus._serial = 1

        task = asyncio.create_task(bus.connect())

        for _ in range(200):
            if bus._method_return_handlers:
                break
            await asyncio.sleep(0)
        else:
            task.cancel()
            raise AssertionError("on_hello handler never registered")

        serial, handler = next(iter(bus._method_return_handlers.items()))
        assert serial == 2

        handler(None, DBusError("org.freedesktop.DBus.Error.Failed", "boom", None))

        with pytest.raises(DBusError, match="boom"):
            await task

        assert bus._sock is None
        assert bus._stream is None
        assert bus._fd is None
        assert bus._writer is None
    finally:
        listener.close()


def _offline_bus() -> BaseMessageBus:
    # Constructs a bus without touching DBUS_SESSION_BUS_ADDRESS or a socket;
    # enough to exercise the pure registry/serial/reply-expectation contract.
    return BaseMessageBus(bus_address="unix:path=/dev/null")


def test_next_serial_increments_monotonically_from_one() -> None:
    bus = _offline_bus()
    assert [bus.next_serial() for _ in range(3)] == [1, 2, 3]


def test_add_message_handler_registers_callable() -> None:
    bus = _offline_bus()

    def handler(msg: Message) -> None:
        return None

    bus.add_message_handler(handler)
    assert bus._user_message_handlers == [handler]


def test_add_message_handler_rejects_non_callable() -> None:
    bus = _offline_bus()
    with pytest.raises(TypeError, match="must be callable with a single parameter"):
        bus.add_message_handler(object())  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "handler",
    [
        lambda: None,
        lambda a, b: None,
    ],
    ids=["zero_args", "two_args"],
)
def test_add_message_handler_rejects_wrong_arity(handler) -> None:
    bus = _offline_bus()
    with pytest.raises(TypeError, match="must be callable with a single parameter"):
        bus.add_message_handler(handler)


def test_remove_message_handler_removes_single_registration() -> None:
    bus = _offline_bus()

    def handler(msg: Message) -> None:
        return None

    bus.add_message_handler(handler)
    bus.add_message_handler(handler)
    bus.remove_message_handler(handler)
    # remove_message_handler deletes only the first match, not every copy.
    assert bus._user_message_handlers == [handler]


def test_remove_message_handler_absent_is_noop() -> None:
    bus = _offline_bus()

    def handler(msg: Message) -> None:
        return None

    bus.remove_message_handler(handler)
    assert bus._user_message_handlers == []


def _method_call(flags: MessageFlag) -> Message:
    return Message(
        path="/test/path",
        interface="test.interface",
        member="Method",
        message_type=MessageType.METHOD_CALL,
        flags=flags,
    )


@pytest.mark.parametrize(
    ("flags", "expected"),
    [
        (MessageFlag.NONE, True),
        (MessageFlag.NO_REPLY_EXPECTED, False),
        # Slow path: any flag that is not the NONE/NO_REPLY_EXPECTED singleton
        # falls through to the mask check — both a lone third flag (this case)
        # and a combined one (next case).
        (MessageFlag.ALLOW_INTERACTIVE_AUTHORIZATION, True),
        (
            MessageFlag.NO_REPLY_EXPECTED | MessageFlag.ALLOW_INTERACTIVE_AUTHORIZATION,
            False,
        ),
    ],
    ids=["none", "no_reply", "interactive", "combined"],
)
def test_expects_reply_honours_no_reply_flag(
    flags: MessageFlag, expected: bool
) -> None:
    assert _expects_reply(_method_call(flags)) is expected


class _RecordingCallBus(BaseMessageBus):
    """Records (message, reply_notify) so the closure can be driven directly,
    without a socket or session daemon. Subclassing overrides the cpdef _call
    on both the pure-Python and compiled extension types."""

    def __init__(self) -> None:
        super().__init__(bus_address="unix:path=/dev/null")
        self.captured: list[tuple] = []

    def _call(self, msg: Message, callback) -> None:
        self.captured.append((msg, callback))


def _return_msg(signature: str, body: list) -> Message:
    return Message(
        message_type=MessageType.METHOD_RETURN,
        reply_serial=1,
        signature=signature,
        body=body,
    )


def _valid_callback(a, b) -> None:
    return None


def test_check_callback_type_accepts_two_param_callable() -> None:
    assert BaseMessageBus._check_callback_type(_valid_callback) is None


def test_check_callback_type_rejects_non_callable() -> None:
    with pytest.raises(TypeError, match="callable with two parameters"):
        BaseMessageBus._check_callback_type(object())  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "callback",
    [lambda: None, lambda a: None, lambda a, b, c: None],
    ids=["zero", "one", "three"],
)
def test_check_callback_type_rejects_wrong_arity(callback) -> None:
    with pytest.raises(TypeError, match="callable with two parameters"):
        BaseMessageBus._check_callback_type(callback)


def _method_return(signature: str, body) -> Message:
    return Message(
        message_type=MessageType.METHOD_RETURN,
        reply_serial=1,
        signature=signature,
        body=body,
    )


def test_request_name_callback_receives_parsed_reply() -> None:
    bus = _RecordingCallBus()
    results: list = []

    bus.request_name("com.example.Name", callback=lambda r, e: results.append((r, e)))

    _msg, reply_notify = bus.captured[0]
    reply_notify(_return_msg("u", [RequestNameReply.PRIMARY_OWNER.value]), None)
    assert results == [(RequestNameReply.PRIMARY_OWNER, None)]


def test_request_name_callback_receives_error() -> None:
    bus = _RecordingCallBus()
    results: list = []

    bus.request_name("com.example.Name", callback=lambda r, e: results.append((r, e)))

    err = DBusError(ErrorType.FAILED, "nope", None)
    bus.captured[0][1](None, err)
    assert results == [(None, err)]


def test_request_name_coerces_integer_flags_to_nameflag() -> None:
    bus = _RecordingCallBus()

    bus.request_name("com.example.Name", flags=NameFlag.REPLACE_EXISTING.value)

    sent_flags = bus.captured[0][0].body[1]
    assert sent_flags == NameFlag.REPLACE_EXISTING
    assert type(sent_flags) is NameFlag


def test_request_name_without_callback_passes_none() -> None:
    bus = _RecordingCallBus()

    bus.request_name("com.example.Name")

    assert bus.captured[0][1] is None


def test_release_name_callback_receives_parsed_reply() -> None:
    bus = _RecordingCallBus()
    results: list = []

    bus.release_name("com.example.Name", callback=lambda r, e: results.append((r, e)))

    bus.captured[0][1](_return_msg("u", [ReleaseNameReply.RELEASED.value]), None)
    assert results == [(ReleaseNameReply.RELEASED, None)]


def test_release_name_callback_receives_error() -> None:
    bus = _RecordingCallBus()
    results: list = []

    bus.release_name("com.example.Name", callback=lambda r, e: results.append((r, e)))

    err = DBusError(ErrorType.FAILED, "nope", None)
    bus.captured[0][1](None, err)
    assert results == [(None, err)]


def test_release_name_without_callback_passes_none() -> None:
    bus = _RecordingCallBus()

    bus.release_name("com.example.Name")

    assert bus.captured[0][1] is None


def test_introspect_callback_receives_parsed_node() -> None:
    bus = _RecordingCallBus()
    results: list = []

    bus.introspect(
        "com.example.Name", "/com/example", lambda r, e: results.append((r, e))
    )

    bus.captured[0][1](_return_msg("s", ["<node></node>"]), None)
    node, err = results[0]
    assert err is None
    assert isinstance(node, intr.Node)


def test_introspect_callback_receives_error_from_error_reply() -> None:
    bus = _RecordingCallBus()
    results: list = []

    bus.introspect(
        "com.example.Name", "/com/example", lambda r, e: results.append((r, e))
    )

    error_reply = Message(
        message_type=MessageType.ERROR,
        error_name="com.example.Boom",
        reply_serial=1,
        signature="s",
        body=["boom"],
    )
    bus.captured[0][1](error_reply, None)
    node, err = results[0]
    assert node is None
    assert isinstance(err, DBusError)
    assert err.type == "com.example.Boom"


@pytest.mark.parametrize(
    "bad_callback",
    [object(), lambda only_one: None, lambda a, b, c: None],
    ids=["not_callable", "one_param", "three_params"],
)
def test_introspect_rejects_invalid_callback(bad_callback) -> None:
    bus = _offline_bus()
    with pytest.raises(TypeError, match="must be callable with two parameters"):
        bus.introspect("com.example.Name", "/com/example", bad_callback)


def test_check_method_return_passes_on_matching_signature() -> None:
    assert (
        BaseMessageBus._check_method_return(_method_return("s", ["ok"]), None, "s")
        is None
    )


def test_check_method_return_reraises_supplied_error() -> None:
    sentinel = RuntimeError("transport gone")
    with pytest.raises(RuntimeError, match="transport gone"):
        BaseMessageBus._check_method_return(None, sentinel, "s")


def test_check_method_return_raises_internal_error_on_none_message() -> None:
    with pytest.raises(DBusError, match="invalid message type") as exc:
        BaseMessageBus._check_method_return(None, None, "s")
    assert exc.value.type == ErrorType.INTERNAL_ERROR.value


def test_check_method_return_raises_internal_error_on_signature_mismatch() -> None:
    with pytest.raises(DBusError, match="invalid message type") as exc:
        BaseMessageBus._check_method_return(_method_return("i", [1]), None, "s")
    assert exc.value.type == ErrorType.INTERNAL_ERROR.value


def test_check_method_return_surfaces_error_message() -> None:
    err_msg = Message(
        message_type=MessageType.ERROR,
        reply_serial=1,
        error_name="com.example.Failed",
        signature="s",
        body=["boom"],
    )
    with pytest.raises(DBusError, match="boom") as exc:
        BaseMessageBus._check_method_return(err_msg, None, "s")
    assert exc.value.type == "com.example.Failed"
    assert exc.value.text == "boom"


def _record_calls(monkeypatch):
    calls = []
    monkeypatch.setattr(
        BaseMessageBus,
        "_call",
        lambda self, msg, notify=None: calls.append(msg),
    )
    return calls


def test_add_match_rule_skips_name_owner_rule(monkeypatch) -> None:
    bus = _offline_bus()
    calls = _record_calls(monkeypatch)
    bus._add_match_rule(bus._name_owner_match_rule)
    assert calls == []
    assert bus._name_owner_match_rule not in bus._match_rules


def test_add_match_rule_sends_add_match_once_then_refcounts(monkeypatch) -> None:
    bus = _offline_bus()
    calls = _record_calls(monkeypatch)
    rule = "type='signal',interface='com.example'"

    bus._add_match_rule(rule)
    bus._add_match_rule(rule)

    assert bus._match_rules[rule] == 2
    assert [m.member for m in calls] == ["AddMatch"]
    assert calls[0].body == [rule]


def test_remove_match_rule_decrements_before_removing(monkeypatch) -> None:
    bus = _offline_bus()
    calls = _record_calls(monkeypatch)
    rule = "type='signal',interface='com.example'"
    bus._add_match_rule(rule)
    bus._add_match_rule(rule)
    calls.clear()

    bus._remove_match_rule(rule)
    assert bus._match_rules[rule] == 1
    assert calls == []

    bus._remove_match_rule(rule)
    assert rule not in bus._match_rules
    assert [m.member for m in calls] == ["RemoveMatch"]
    assert calls[0].body == [rule]


def test_remove_match_rule_skips_name_owner_rule(monkeypatch) -> None:
    bus = _offline_bus()
    calls = _record_calls(monkeypatch)
    bus._remove_match_rule(bus._name_owner_match_rule)
    assert calls == []
