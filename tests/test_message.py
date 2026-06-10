"""Behavioural tests for the :class:`Message` construction contract."""

from __future__ import annotations

from typing import Any

import pytest

from dbus_fast.constants import ErrorType, MessageFlag, MessageType
from dbus_fast.errors import (
    InvalidBusNameError,
    InvalidInterfaceNameError,
    InvalidMemberNameError,
    InvalidMessageError,
    InvalidObjectPathError,
)
from dbus_fast.message import Message


@pytest.mark.parametrize(
    ("kwargs", "missing"),
    [
        ({"message_type": MessageType.METHOD_CALL}, "path"),
        ({"message_type": MessageType.METHOD_CALL, "path": "/x"}, "member"),
        (
            {"message_type": MessageType.SIGNAL, "path": "/x", "member": "M"},
            "interface",
        ),
        ({"message_type": MessageType.ERROR, "error_name": "a.b"}, "reply_serial"),
        ({"message_type": MessageType.METHOD_RETURN}, "reply_serial"),
    ],
)
def test_missing_required_field_rejected(kwargs: dict[str, Any], missing: str) -> None:
    with pytest.raises(InvalidMessageError, match=f"missing required field: {missing}"):
        Message(**kwargs)


def test_zero_reply_serial_counts_as_missing() -> None:
    with pytest.raises(
        InvalidMessageError, match="missing required field: reply_serial"
    ):
        Message(message_type=MessageType.METHOD_RETURN, reply_serial=0)


def test_valid_messages_per_type() -> None:
    Message(message_type=MessageType.METHOD_CALL, path="/x", member="M")
    Message(message_type=MessageType.METHOD_RETURN, reply_serial=5)
    Message(message_type=MessageType.ERROR, error_name="a.b", reply_serial=5)
    Message(message_type=MessageType.SIGNAL, path="/x", member="M", interface="a.b.C")


def test_validate_false_skips_all_checks() -> None:
    msg = Message(message_type=MessageType.METHOD_CALL, validate=False)
    assert msg.path is None
    assert msg.member is None


def test_validate_false_skips_field_validators() -> None:
    msg = Message(path="not a path", member="bad.member", validate=False)
    assert msg.path == "not a path"


def test_error_name_enum_coerced_to_str() -> None:
    msg = Message(
        message_type=MessageType.ERROR,
        error_name=ErrorType.FAILED,
        reply_serial=1,
    )
    assert msg.error_name == ErrorType.FAILED.value
    assert type(msg.error_name) is str


def test_flags_int_coerced_to_enum() -> None:
    msg = Message(message_type=MessageType.METHOD_CALL, path="/x", member="M", flags=1)
    assert msg.flags is MessageFlag.NO_REPLY_EXPECTED


def test_defaults_for_optional_fields() -> None:
    msg = Message(message_type=MessageType.METHOD_CALL, path="/x", member="M")
    assert msg.serial == 0
    assert msg.reply_serial == 0
    assert msg.flags is MessageFlag.NONE
    assert msg.signature == ""
    assert msg.body == []
    assert msg.unix_fds == []


@pytest.mark.parametrize(
    ("kwargs", "error"),
    [
        ({"path": "bad path", "member": "M"}, InvalidObjectPathError),
        ({"path": "/x", "member": "bad.member"}, InvalidMemberNameError),
        (
            {
                "message_type": MessageType.SIGNAL,
                "path": "/x",
                "member": "M",
                "interface": "badiface",
            },
            InvalidInterfaceNameError,
        ),
        ({"destination": "bad name", "path": "/x", "member": "M"}, InvalidBusNameError),
        (
            {
                "message_type": MessageType.ERROR,
                "error_name": "badname",
                "reply_serial": 1,
            },
            InvalidInterfaceNameError,
        ),
    ],
)
def test_invalid_field_values_rejected(
    kwargs: dict[str, Any], error: type[Exception]
) -> None:
    with pytest.raises(error):
        Message(**kwargs)


def _call(serial: int = 42) -> Message:
    msg = Message(
        message_type=MessageType.METHOD_CALL,
        path="/x",
        member="M",
        sender=":1.5",
    )
    msg.serial = serial
    return msg


def test_new_error_builds_reply() -> None:
    err = Message.new_error(_call(), "org.example.Err", "boom")
    assert err.message_type is MessageType.ERROR
    assert err.reply_serial == 42
    assert err.destination == ":1.5"
    assert err.error_name == "org.example.Err"
    assert err.signature == "s"
    assert err.body == ["boom"]


def test_new_error_accepts_error_type_enum() -> None:
    err = Message.new_error(_call(), ErrorType.FAILED, "boom")
    assert err.error_name == ErrorType.FAILED.value


def test_new_method_return_builds_reply() -> None:
    ret = Message.new_method_return(_call(), "s", ["hi"])
    assert ret.message_type is MessageType.METHOD_RETURN
    assert ret.reply_serial == 42
    assert ret.destination == ":1.5"
    assert ret.signature == "s"
    assert ret.body == ["hi"]


def test_new_signal_builds_signal() -> None:
    sig = Message.new_signal("/x", "a.b.C", "Sig")
    assert sig.message_type is MessageType.SIGNAL
    assert sig.path == "/x"
    assert sig.interface == "a.b.C"
    assert sig.member == "Sig"


def test_repr_includes_key_fields() -> None:
    msg = Message(message_type=MessageType.METHOD_CALL, path="/x", member="M")
    text = repr(msg)
    assert "METHOD_CALL" in text
    assert "path=/x" in text
    assert "member=M" in text
