import asyncio
import logging
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
from dbus_fast.errors import (
    AuthError,
    DBusError,
    InternalError,
    InvalidAddressError,
    InvalidObjectPathError,
)
from dbus_fast.message import Message
from dbus_fast.message_bus import BaseMessageBus, _expects_reply
from dbus_fast.send_reply import SendReply
from dbus_fast.service import PropertyAccess, ServiceInterface, dbus_property


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


class _RecordingMatchBus(BaseMessageBus):
    """Captures messages passed to the cpdef _call. Subclassing overrides it on
    both the pure-Python and compiled extension types, where the class is
    immutable and cannot be monkeypatched."""

    def __init__(self) -> None:
        super().__init__(bus_address="unix:path=/dev/null")
        self.calls: list[Message] = []

    def _call(self, msg: Message, callback=None) -> None:
        self.calls.append(msg)


def test_add_match_rule_skips_name_owner_rule() -> None:
    bus = _RecordingMatchBus()
    bus._add_match_rule(bus._name_owner_match_rule)
    assert bus.calls == []
    assert bus._name_owner_match_rule not in bus._match_rules


def test_add_match_rule_sends_add_match_once_then_refcounts() -> None:
    bus = _RecordingMatchBus()
    rule = "type='signal',interface='com.example'"

    bus._add_match_rule(rule)
    bus._add_match_rule(rule)

    assert bus._match_rules[rule] == 2
    assert [m.member for m in bus.calls] == ["AddMatch"]
    assert bus.calls[0].body == [rule]


def test_remove_match_rule_decrements_before_removing() -> None:
    bus = _RecordingMatchBus()
    rule = "type='signal',interface='com.example'"
    bus._add_match_rule(rule)
    bus._add_match_rule(rule)
    bus.calls.clear()

    bus._remove_match_rule(rule)
    assert bus._match_rules[rule] == 1
    assert bus.calls == []

    bus._remove_match_rule(rule)
    assert rule not in bus._match_rules
    assert [m.member for m in bus.calls] == ["RemoveMatch"]
    assert bus.calls[0].body == [rule]


def test_remove_match_rule_skips_name_owner_rule() -> None:
    bus = _RecordingMatchBus()
    bus._remove_match_rule(bus._name_owner_match_rule)
    assert bus.calls == []


class _SendCapturingBus(BaseMessageBus):
    """Records replies sent through SendReply and callbacks queued via _call."""

    def __init__(self) -> None:
        super().__init__(bus_address="unix:path=/dev/null")
        self.sent: list[Message] = []
        self.call_callbacks: list = []

    def send(self, msg: Message) -> None:
        self.sent.append(msg)

    def _call(self, msg: Message, callback=None) -> None:
        self.call_callbacks.append(callback)


def _props_message(member: str, signature: str, body: list) -> Message:
    return Message(
        path="/com/example/Test",
        interface="org.freedesktop.DBus.Properties",
        member=member,
        signature=signature,
        body=body,
        serial=1,
    )


def _get_machine_id_message() -> Message:
    return Message(
        path="/com/example/Test",
        interface="org.freedesktop.DBus.Peer",
        member="GetMachineId",
        serial=1,
    )


def test_default_properties_handler_rejects_unknown_method() -> None:
    bus = _SendCapturingBus()
    msg = _props_message("Frobnicate", "", [])
    with pytest.raises(DBusError, match="doesn't have method") as exc:
        bus._default_properties_handler(msg, SendReply(bus, msg))
    assert exc.value.type == ErrorType.UNKNOWN_METHOD.value


def test_default_properties_handler_rejects_signature_mismatch() -> None:
    bus = _SendCapturingBus()
    msg = _props_message("Get", "s", ["com.example.Foo"])
    with pytest.raises(DBusError, match="doesn't have method") as exc:
        bus._default_properties_handler(msg, SendReply(bus, msg))
    assert exc.value.type == ErrorType.UNKNOWN_METHOD.value


def test_default_properties_handler_rejects_empty_interface() -> None:
    bus = _SendCapturingBus()
    msg = _props_message("GetAll", "s", [""])
    with pytest.raises(DBusError, match="empty interface") as exc:
        bus._default_properties_handler(msg, SendReply(bus, msg))
    assert exc.value.type == ErrorType.NOT_SUPPORTED.value


def test_default_properties_handler_rejects_unknown_object() -> None:
    bus = _SendCapturingBus()
    msg = _props_message("GetAll", "s", ["com.example.Foo"])
    with pytest.raises(DBusError, match="no interfaces at path") as exc:
        bus._default_properties_handler(msg, SendReply(bus, msg))
    assert exc.value.type == ErrorType.UNKNOWN_OBJECT.value


def test_default_properties_handler_standard_interface_get_unknown_property() -> None:
    bus = _SendCapturingBus()
    bus._path_exports["/com/example/Test"] = {}
    msg = _props_message("Get", "ss", ["org.freedesktop.DBus.Peer", "SomeProp"])
    with pytest.raises(DBusError, match="does not have property") as exc:
        bus._default_properties_handler(msg, SendReply(bus, msg))
    assert exc.value.type == ErrorType.UNKNOWN_PROPERTY.value


def test_default_properties_handler_standard_interface_getall_returns_empty() -> None:
    bus = _SendCapturingBus()
    bus._path_exports["/com/example/Test"] = {}
    msg = _props_message("GetAll", "s", ["org.freedesktop.DBus.Peer"])
    bus._default_properties_handler(msg, SendReply(bus, msg))
    assert len(bus.sent) == 1
    assert bus.sent[0].message_type == MessageType.METHOD_RETURN
    assert bus.sent[0].body == [{}]


def test_default_properties_handler_rejects_unknown_interface() -> None:
    bus = _SendCapturingBus()
    bus._path_exports["/com/example/Test"] = {}
    msg = _props_message("GetAll", "s", ["com.example.NotExported"])
    with pytest.raises(DBusError, match="could not find an interface") as exc:
        bus._default_properties_handler(msg, SendReply(bus, msg))
    assert exc.value.type == ErrorType.UNKNOWN_INTERFACE.value


def test_default_get_machine_id_replies_from_cache_without_call() -> None:
    bus = _SendCapturingBus()
    bus._machine_id = "cached-machine-id"
    msg = _get_machine_id_message()
    bus._default_get_machine_id_handler(msg, SendReply(bus, msg))
    assert bus.call_callbacks == []
    assert bus.sent[0].body == ["cached-machine-id"]


def test_default_get_machine_id_caches_and_replies_on_method_return() -> None:
    bus = _SendCapturingBus()
    msg = _get_machine_id_message()
    bus._default_get_machine_id_handler(msg, SendReply(bus, msg))
    reply_handler = bus.call_callbacks[0]
    reply = Message(
        message_type=MessageType.METHOD_RETURN,
        reply_serial=1,
        signature="s",
        body=["fresh-machine-id"],
    )
    reply_handler(reply, None)
    assert bus._machine_id == "fresh-machine-id"
    assert bus.sent[0].body == ["fresh-machine-id"]


def test_default_get_machine_id_forwards_error_reply() -> None:
    bus = _SendCapturingBus()
    msg = _get_machine_id_message()
    bus._default_get_machine_id_handler(msg, SendReply(bus, msg))
    reply_handler = bus.call_callbacks[0]
    err_reply = Message(
        message_type=MessageType.ERROR,
        reply_serial=1,
        error_name="com.example.Failed",
        signature="s",
        body=["nope"],
    )
    reply_handler(err_reply, None)
    assert bus.sent[0].message_type == MessageType.ERROR
    assert bus.sent[0].error_name == "com.example.Failed"


def test_default_get_machine_id_swallows_disconnect() -> None:
    bus = _SendCapturingBus()
    msg = _get_machine_id_message()
    bus._default_get_machine_id_handler(msg, SendReply(bus, msg))
    reply_handler = bus.call_callbacks[0]
    reply_handler(None, ConnectionError("disconnected"))
    assert bus.sent == []


def _method_call_msg(serial: int = 1) -> Message:
    return Message(
        message_type=MessageType.METHOD_CALL,
        path="/com/example",
        interface="com.example.Iface",
        member="DoThing",
        serial=serial,
    )


def _name_owner_changed(name: str, old: str, new: str) -> Message:
    return Message(
        message_type=MessageType.SIGNAL,
        sender="org.freedesktop.DBus",
        path="/org/freedesktop/DBus",
        interface="org.freedesktop.DBus",
        member="NameOwnerChanged",
        signature="sss",
        body=[name, old, new],
    )


def _error_reply(error_name: str = "com.example.Boom", text: str = "boom") -> Message:
    return Message(
        message_type=MessageType.ERROR,
        error_name=error_name,
        reply_serial=1,
        signature="s",
        body=[text],
    )


def test_process_message_sends_handler_returned_message() -> None:
    bus = _SendCapturingBus()
    reply = Message(
        message_type=MessageType.METHOD_RETURN,
        reply_serial=1,
        signature="s",
        body=["ok"],
    )
    seen_by_second: list = []
    bus.add_message_handler(lambda m: reply)
    bus.add_message_handler(lambda m: seen_by_second.append(m))
    bus._process_message(_method_call_msg())
    assert bus.sent == [reply]
    assert seen_by_second == []


def test_process_message_truthy_non_message_marks_handled_without_send() -> None:
    bus = _SendCapturingBus()
    seen_by_second: list = []
    bus.add_message_handler(lambda m: True)
    bus.add_message_handler(lambda m: seen_by_second.append(m))
    bus._process_message(_method_call_msg())
    assert bus.sent == []
    assert seen_by_second == []


def test_process_message_handler_dbus_error_on_call_sends_error_reply() -> None:
    bus = _SendCapturingBus()

    def boom(_msg: Message) -> None:
        raise DBusError(ErrorType.FAILED, "handler said no", None)

    bus.add_message_handler(boom)
    bus._process_message(_method_call_msg())
    assert len(bus.sent) == 1
    assert bus.sent[0].message_type == MessageType.ERROR
    assert bus.sent[0].error_name == ErrorType.FAILED.value


def test_process_message_handler_dbus_error_on_signal_is_swallowed() -> None:
    bus = _SendCapturingBus()

    def boom(_msg: Message) -> None:
        raise DBusError(ErrorType.FAILED, "handler said no", None)

    bus.add_message_handler(boom)
    bus._process_message(_name_owner_changed("com.example", "", ":1.5"))
    assert bus.sent == []


def test_process_message_name_owner_changed_records_owner() -> None:
    bus = _SendCapturingBus()
    bus._process_message(_name_owner_changed("com.example", "", ":1.42"))
    assert bus._name_owners["com.example"] == ":1.42"


def test_process_message_name_owner_changed_drops_owner_on_empty() -> None:
    bus = _SendCapturingBus()
    bus._name_owners["com.example"] = ":1.42"
    bus._process_message(_name_owner_changed("com.example", ":1.42", ""))
    assert "com.example" not in bus._name_owners


def test_process_message_name_owner_changed_empty_owner_unknown_name_noop() -> None:
    bus = _SendCapturingBus()
    bus._process_message(_name_owner_changed("com.example", "", ""))
    assert bus._name_owners == {}


def test_init_high_level_client_logs_add_match_error(caplog) -> None:
    bus = _SendCapturingBus()
    bus._init_high_level_client()
    notify = bus.call_callbacks[0]
    with caplog.at_level(logging.ERROR, logger="dbus_fast.message_bus"):
        notify(None, DBusError(ErrorType.FAILED, "nope", None))
    assert "add match request failed" in caplog.text


def test_init_high_level_client_logs_add_match_error_reply(caplog) -> None:
    bus = _SendCapturingBus()
    bus._init_high_level_client()
    notify = bus.call_callbacks[0]
    with caplog.at_level(logging.ERROR, logger="dbus_fast.message_bus"):
        notify(_error_reply(), None)
    assert "add match request failed" in caplog.text


def test_init_high_level_client_runs_once() -> None:
    bus = _SendCapturingBus()
    bus._init_high_level_client()
    bus._init_high_level_client()
    assert len(bus.call_callbacks) == 1


def test_add_match_rule_notify_logs_error(caplog) -> None:
    bus = _SendCapturingBus()
    bus._add_match_rule("type='signal',interface='com.example'")
    notify = bus.call_callbacks[0]
    with caplog.at_level(logging.ERROR, logger="dbus_fast.message_bus"):
        notify(None, DBusError(ErrorType.FAILED, "nope", None))
    assert "add match request failed" in caplog.text


def test_add_match_rule_notify_logs_error_reply(caplog) -> None:
    bus = _SendCapturingBus()
    bus._add_match_rule("type='signal',interface='com.example'")
    notify = bus.call_callbacks[0]
    with caplog.at_level(logging.ERROR, logger="dbus_fast.message_bus"):
        notify(_error_reply(), None)
    assert "add match request failed" in caplog.text


def test_remove_match_rule_notify_logs_error(caplog) -> None:
    bus = _SendCapturingBus()
    rule = "type='signal',interface='com.example'"
    bus._add_match_rule(rule)
    bus._remove_match_rule(rule)
    notify = bus.call_callbacks[-1]
    with caplog.at_level(logging.ERROR, logger="dbus_fast.message_bus"):
        notify(None, DBusError(ErrorType.FAILED, "nope", None))
    assert "remove match request failed" in caplog.text


def test_remove_match_rule_notify_logs_error_reply(caplog) -> None:
    bus = _SendCapturingBus()
    rule = "type='signal',interface='com.example'"
    bus._add_match_rule(rule)
    bus._remove_match_rule(rule)
    notify = bus.call_callbacks[-1]
    with caplog.at_level(logging.ERROR, logger="dbus_fast.message_bus"):
        notify(_error_reply(), None)
    assert "remove match request failed" in caplog.text


def test_remove_match_rule_notify_skips_when_disconnected(caplog) -> None:
    bus = _SendCapturingBus()
    rule = "type='signal',interface='com.example'"
    bus._add_match_rule(rule)
    bus._remove_match_rule(rule)
    notify = bus.call_callbacks[-1]
    bus._disconnected = True
    with caplog.at_level(logging.ERROR, logger="dbus_fast.message_bus"):
        notify(None, DBusError(ErrorType.FAILED, "nope", None))
    assert "remove match request failed" not in caplog.text


class _SendOnlyBus(BaseMessageBus):
    """Captures sent messages while exercising the real _call/_finalize paths."""

    def __init__(self) -> None:
        super().__init__(bus_address="unix:path=/dev/null")
        self.sent: list[Message] = []

    def send(self, msg: Message) -> None:
        self.sent.append(msg)


class _Closable:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_call_no_reply_expected_invokes_callback_immediately() -> None:
    bus = _SendOnlyBus()
    msg = _method_call(MessageFlag.NO_REPLY_EXPECTED)
    calls: list[tuple] = []
    bus._call(msg, lambda reply, err: calls.append((reply, err)))
    assert len(bus.sent) == 1
    assert calls == [(None, None)]
    assert bus._method_return_handlers == {}


def test_call_reply_expected_installs_handler_and_defers_callback() -> None:
    bus = _SendOnlyBus()
    msg = _method_call(MessageFlag.NONE)
    calls: list[tuple] = []
    bus._call(msg, lambda reply, err: calls.append((reply, err)))
    assert len(bus.sent) == 1
    assert calls == []
    assert msg.serial in bus._method_return_handlers


def test_finalize_drains_return_handlers_with_error(caplog) -> None:
    bus = _SendOnlyBus()
    bus._stream = _Closable()
    bus._sock = _Closable()
    err = DBusError(ErrorType.FAILED, "bus gone", None)
    received: list[tuple] = []
    bus._method_return_handlers[1] = lambda reply, e: received.append((reply, e))

    def _raising(reply, e):
        raise RuntimeError("handler boom")

    bus._method_return_handlers[2] = _raising

    with caplog.at_level(logging.WARNING, logger="dbus_fast.message_bus"):
        bus._finalize(err)

    assert received == [(None, err)]
    assert "threw an exception on shutdown" in caplog.text
    assert bus._method_return_handlers == {}
    assert bus._disconnected is True
    assert bus._stream.closed is True
    assert bus._sock.closed is True


def test_finalize_is_idempotent_when_already_disconnected() -> None:
    bus = _SendOnlyBus()
    bus._disconnected = True
    bus._method_return_handlers[1] = lambda reply, e: None
    bus._finalize(None)
    assert bus._method_return_handlers == {1: bus._method_return_handlers[1]}


@pytest.mark.asyncio
async def test_future_exception_no_reply_logs_and_discards(caplog) -> None:
    bus = MessageBus("unix:path=/dev/null")
    fut = bus._loop.create_future()
    fut.set_exception(ValueError("boom"))
    bus._pending_futures.add(fut)

    with caplog.at_level(logging.ERROR, logger="dbus_fast.aio.message_bus"):
        bus._future_exception_no_reply(fut)

    assert fut not in bus._pending_futures
    assert "unexpected exception in future" in caplog.text


@pytest.mark.asyncio
async def test_future_exception_no_reply_swallows_cancelled(caplog) -> None:
    bus = MessageBus("unix:path=/dev/null")
    fut = bus._loop.create_future()
    fut.cancel()
    bus._pending_futures.add(fut)

    with caplog.at_level(logging.ERROR, logger="dbus_fast.aio.message_bus"):
        bus._future_exception_no_reply(fut)

    assert fut not in bus._pending_futures
    assert "unexpected exception in future" not in caplog.text


@pytest.mark.asyncio
async def test_finalize_warns_when_reader_removal_fails(caplog, monkeypatch) -> None:
    bus = MessageBus("unix:path=/dev/null")
    bus._fd = 0
    bus._stream = _Closable()
    bus._sock = _Closable()

    def _raise(fd: int) -> None:
        raise RuntimeError("no reader")

    monkeypatch.setattr(bus._loop, "remove_reader", _raise)

    with caplog.at_level(logging.WARNING, logger="dbus_fast.aio.message_bus"):
        bus._finalize(None)

    assert "could not remove message reader" in caplog.text
    assert bus._disconnect_future.done()


@pytest.mark.asyncio
async def test_finalize_warns_when_writer_removal_fails(caplog, monkeypatch) -> None:
    bus = MessageBus("unix:path=/dev/null")
    bus._fd = 0
    bus._stream = _Closable()
    bus._sock = _Closable()

    def _raise(fd: int) -> None:
        raise RuntimeError("no writer")

    monkeypatch.setattr(bus._loop, "remove_writer", _raise)

    with caplog.at_level(logging.WARNING, logger="dbus_fast.aio.message_bus"):
        bus._finalize(None)

    assert "could not remove message writer" in caplog.text
    assert bus._disconnect_future.done()


class _ExampleInterface(ServiceInterface):
    @dbus_property(access=PropertyAccess.READ)
    def Foo(self) -> "s":
        return "bar"


def _interfaces_signal(sent: list[Message], member: str) -> Message:
    return next(m for m in sent if m.member == member)


def test_export_rejects_non_service_interface() -> None:
    bus = _SendCapturingBus()
    with pytest.raises(TypeError, match="must be a ServiceInterface"):
        bus.export("/com/example/Test", object())


def test_export_rejects_invalid_object_path() -> None:
    bus = _SendCapturingBus()
    with pytest.raises(InvalidObjectPathError, match="invalid object path"):
        bus.export("not a path", _ExampleInterface("com.example.Test"))


def test_export_rejects_duplicate_interface_name() -> None:
    bus = _SendCapturingBus()
    bus.export("/com/example/Test", _ExampleInterface("com.example.Test"))
    with pytest.raises(ValueError, match="already exported"):
        bus.export("/com/example/Test", _ExampleInterface("com.example.Test"))


def test_export_registers_interface_and_emits_interfaces_added() -> None:
    bus = _SendCapturingBus()
    iface = _ExampleInterface("com.example.Test")
    bus.export("/com/example/Test", iface)
    assert bus._path_exports["/com/example/Test"]["com.example.Test"] is iface
    added = _interfaces_signal(bus.sent, "InterfacesAdded")
    assert added.interface == "org.freedesktop.DBus.ObjectManager"
    assert added.body[0] == "/com/example/Test"
    assert added.body[1]["com.example.Test"]["Foo"].value == "bar"


def test_export_skips_emit_when_disconnected() -> None:
    bus = _SendCapturingBus()
    bus._disconnected = True
    bus.export("/com/example/Test", _ExampleInterface("com.example.Test"))
    assert bus.sent == []


def test_unexport_rejects_invalid_object_path() -> None:
    bus = _SendCapturingBus()
    with pytest.raises(InvalidObjectPathError, match="invalid object path"):
        bus.unexport("not a path")


def test_unexport_rejects_bad_interface_type() -> None:
    bus = _SendCapturingBus()
    with pytest.raises(TypeError, match="must be a ServiceInterface or interface name"):
        bus.unexport("/com/example/Test", 123)


def test_unexport_unknown_path_is_noop() -> None:
    bus = _SendCapturingBus()
    bus.unexport("/com/example/Absent")
    assert bus.sent == []


def test_unexport_unknown_interface_name_is_noop() -> None:
    bus = _SendCapturingBus()
    bus.export("/com/example/Test", _ExampleInterface("com.example.Test"))
    bus.sent.clear()
    bus.unexport("/com/example/Test", "com.example.Other")
    assert "com.example.Test" in bus._path_exports["/com/example/Test"]
    assert bus.sent == []


def test_unexport_by_name_removes_and_emits_interfaces_removed() -> None:
    bus = _SendCapturingBus()
    bus.export("/com/example/Test", _ExampleInterface("com.example.Test"))
    bus.sent.clear()
    bus.unexport("/com/example/Test", "com.example.Test")
    assert "/com/example/Test" not in bus._path_exports
    removed = _interfaces_signal(bus.sent, "InterfacesRemoved")
    assert removed.body == ["/com/example/Test", ["com.example.Test"]]


def test_unexport_by_instance_removes_interface() -> None:
    bus = _SendCapturingBus()
    iface = _ExampleInterface("com.example.Test")
    bus.export("/com/example/Test", iface)
    bus.sent.clear()
    bus.unexport("/com/example/Test", iface)
    assert "/com/example/Test" not in bus._path_exports
    assert _interfaces_signal(bus.sent, "InterfacesRemoved")


def test_unexport_all_interfaces_on_path() -> None:
    bus = _SendCapturingBus()
    bus.export("/com/example/Test", _ExampleInterface("com.example.One"))
    bus.export("/com/example/Test", _ExampleInterface("com.example.Two"))
    bus.sent.clear()
    bus.unexport("/com/example/Test")
    assert "/com/example/Test" not in bus._path_exports
    removed = _interfaces_signal(bus.sent, "InterfacesRemoved")
    assert set(removed.body[1]) == {"com.example.One", "com.example.Two"}
