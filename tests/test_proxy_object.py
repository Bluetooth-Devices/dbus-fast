"""Unit tests for ``BaseProxyInterface`` helpers and ``BaseProxyObject`` validation."""

import pytest

from dbus_fast.constants import ErrorType, MessageType
from dbus_fast.errors import (
    DBusError,
    InvalidBusNameError,
    InvalidObjectPathError,
)
from dbus_fast.message import Message
from dbus_fast.proxy_object import BaseProxyInterface, BaseProxyObject

_NODE_XML = "<node></node>"


@pytest.mark.parametrize(
    ("member", "expected"),
    [
        ("Introspect", "introspect"),
        ("Get", "get"),
        ("GetAll", "get_all"),
        ("SetValue", "set_value"),
        ("RequestName", "request_name"),
        ("GetManagedObjects", "get_managed_objects"),
        ("PropertiesChanged", "properties_changed"),
        ("AddMatch", "add_match"),
        ("already_snake", "already_snake"),
    ],
)
def test_to_snake_case(member, expected):
    assert BaseProxyInterface._to_snake_case(member) == expected


def test_to_snake_case_is_cached():
    first = BaseProxyInterface._to_snake_case("GetManagedObjects")
    second = BaseProxyInterface._to_snake_case("GetManagedObjects")
    assert first == second == "get_managed_objects"


def _method_return(signature: str = "", body=None) -> Message:
    return Message(
        message_type=MessageType.METHOD_RETURN,
        reply_serial=1,
        signature=signature,
        body=body if body is not None else [],
    )


def test_check_method_return_accepts_matching_return():
    assert BaseProxyInterface._check_method_return(_method_return()) is None


def test_check_method_return_accepts_matching_signature():
    msg = _method_return(signature="s", body=["ok"])
    assert BaseProxyInterface._check_method_return(msg, "s") is None


def test_check_method_return_raises_on_error_message():
    msg = Message(
        message_type=MessageType.ERROR,
        error_name="com.example.Boom",
        reply_serial=1,
        signature="s",
        body=["boom"],
    )
    with pytest.raises(DBusError) as exc:
        BaseProxyInterface._check_method_return(msg)
    assert exc.value.type == "com.example.Boom"


def test_check_method_return_raises_on_non_return_type():
    msg = Message(
        message_type=MessageType.SIGNAL,
        path="/org/example",
        interface="org.example.Iface",
        member="Tick",
    )
    with pytest.raises(DBusError) as exc:
        BaseProxyInterface._check_method_return(msg)
    assert exc.value.type == ErrorType.CLIENT_ERROR.value


def test_check_method_return_raises_on_signature_mismatch():
    msg = _method_return(signature="i", body=[1])
    with pytest.raises(DBusError) as exc:
        BaseProxyInterface._check_method_return(msg, "s")
    assert exc.value.type == ErrorType.CLIENT_ERROR.value
    assert 'unexpected signature: "i"' in exc.value.text


def test_proxy_object_rejects_invalid_object_path():
    with pytest.raises(InvalidObjectPathError):
        BaseProxyObject(
            "org.example.Name", "not a path", _NODE_XML, object(), BaseProxyInterface
        )


def test_proxy_object_rejects_invalid_bus_name():
    with pytest.raises(InvalidBusNameError):
        BaseProxyObject(
            "not a bus name", "/org/example", _NODE_XML, object(), BaseProxyInterface
        )


def test_proxy_object_rejects_non_bus():
    with pytest.raises(TypeError, match="bus must be an instance"):
        BaseProxyObject(
            "org.example.Name", "/org/example", _NODE_XML, object(), BaseProxyInterface
        )
