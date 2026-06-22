"""Unit tests for ``BaseProxyInterface`` helpers and ``BaseProxyObject`` validation."""

import xml.etree.ElementTree as ET

import pytest

from dbus_fast import introspection as intr
from dbus_fast.constants import ErrorType, MessageType
from dbus_fast.errors import (
    DBusError,
    InterfaceNotFoundError,
    InvalidBusNameError,
    InvalidObjectPathError,
)
from dbus_fast.message import Message
from dbus_fast.message_bus import BaseMessageBus
from dbus_fast.proxy_object import BaseProxyInterface, BaseProxyObject

_NODE_XML = "<node></node>"
_IFACE_NAME = "org.example.Iface"
_IFACE_XML = (
    '<node><interface name="org.example.Iface">'
    '<method name="Foo"><arg type="s" direction="in"/></method>'
    '<property name="P" type="s" access="read"/>'
    '<signal name="Tick"><arg type="s"/></signal>'
    "</interface></node>"
)


class _StubInterface(BaseProxyInterface):
    """Concrete proxy interface that no-ops the backend-specific member adders."""

    def _add_method(self, intr_method: intr.Method) -> None:
        pass

    def _add_property(self, intr_property: intr.Property) -> None:
        pass


def _offline_bus() -> BaseMessageBus:
    return BaseMessageBus(bus_address="unix:path=/dev/null")


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
def test_to_snake_case(member: str, expected: str) -> None:
    assert BaseProxyInterface._to_snake_case(member) == expected


def test_to_snake_case_is_idempotent() -> None:
    first = BaseProxyInterface._to_snake_case("GetManagedObjects")
    second = BaseProxyInterface._to_snake_case("GetManagedObjects")
    assert first == second == "get_managed_objects"


def _method_return(signature: str = "", body: list | None = None) -> Message:
    return Message(
        message_type=MessageType.METHOD_RETURN,
        reply_serial=1,
        signature=signature,
        body=body if body is not None else [],
    )


def test_check_method_return_accepts_matching_return() -> None:
    assert BaseProxyInterface._check_method_return(_method_return()) is None


def test_check_method_return_accepts_matching_signature() -> None:
    msg = _method_return(signature="s", body=["ok"])
    assert BaseProxyInterface._check_method_return(msg, "s") is None


def test_check_method_return_raises_on_error_message() -> None:
    msg = Message(
        message_type=MessageType.ERROR,
        error_name="com.example.Boom",
        reply_serial=1,
        signature="s",
        body=["boom"],
    )
    with pytest.raises(DBusError, match=r"boom") as exc:
        BaseProxyInterface._check_method_return(msg)
    assert exc.value.type == "com.example.Boom"


def test_check_method_return_raises_on_non_return_type() -> None:
    msg = Message(
        message_type=MessageType.SIGNAL,
        path="/org/example",
        interface="org.example.Iface",
        member="Tick",
    )
    with pytest.raises(DBusError, match=r"didnt return a method return") as exc:
        BaseProxyInterface._check_method_return(msg)
    assert exc.value.type == ErrorType.CLIENT_ERROR.value


def test_check_method_return_raises_on_signature_mismatch() -> None:
    msg = _method_return(signature="i", body=[1])
    with pytest.raises(DBusError, match=r"unexpected signature") as exc:
        BaseProxyInterface._check_method_return(msg, "s")
    assert exc.value.type == ErrorType.CLIENT_ERROR.value
    assert 'unexpected signature: "i"' in exc.value.text


def test_proxy_object_rejects_invalid_object_path() -> None:
    with pytest.raises(InvalidObjectPathError, match="not a path"):
        BaseProxyObject(
            "org.example.Name", "not a path", _NODE_XML, object(), BaseProxyInterface
        )


def test_proxy_object_rejects_invalid_bus_name() -> None:
    with pytest.raises(InvalidBusNameError, match="not a bus name"):
        BaseProxyObject(
            "not a bus name", "/org/example", _NODE_XML, object(), BaseProxyInterface
        )


def test_proxy_object_rejects_non_bus() -> None:
    with pytest.raises(TypeError, match="bus must be an instance"):
        BaseProxyObject(
            "org.example.Name", "/org/example", _NODE_XML, object(), BaseProxyInterface
        )


def test_proxy_object_rejects_non_proxy_interface() -> None:
    with pytest.raises(TypeError, match="ProxyInterface must be an instance"):
        BaseProxyObject(
            "org.example.Name", "/org/example", _NODE_XML, _offline_bus(), object
        )


def test_proxy_object_accepts_node_instance() -> None:
    node = intr.Node.parse(_NODE_XML)
    obj = BaseProxyObject(
        "org.example.Name", "/org/example", node, _offline_bus(), _StubInterface
    )
    assert obj.introspection is node


def test_proxy_object_accepts_xml_string() -> None:
    obj = BaseProxyObject(
        "org.example.Name", "/org/example", _IFACE_XML, _offline_bus(), _StubInterface
    )
    assert [i.name for i in obj.introspection.interfaces] == [_IFACE_NAME]


def test_proxy_object_accepts_et_element() -> None:
    # BaseProxyObject calls Node.from_xml(), which treats the element as a
    # non-root node, so the root <node> must carry a name attribute.
    element = ET.fromstring(_IFACE_XML.replace("<node>", '<node name="root">', 1))
    obj = BaseProxyObject(
        "org.example.Name", "/org/example", element, _offline_bus(), _StubInterface
    )
    assert [i.name for i in obj.introspection.interfaces] == [_IFACE_NAME]


def test_proxy_object_rejects_invalid_introspection_type() -> None:
    with pytest.raises(TypeError, match="introspection must be"):
        BaseProxyObject(
            "org.example.Name", "/org/example", 123, _offline_bus(), _StubInterface
        )


def test_proxy_object_child_paths() -> None:
    xml = '<node><node name="child"/></node>'
    obj = BaseProxyObject(
        "org.example.Name", "/org/example", xml, _offline_bus(), _StubInterface
    )
    assert obj.child_paths == ["/org/example/child"]


def _unique_name_object() -> BaseProxyObject:
    # A unique connection name (leading ":") skips the GetNameOwner _call path.
    return BaseProxyObject(
        ":1.42", "/org/example", _IFACE_XML, _offline_bus(), _StubInterface
    )


def test_get_interface_returns_and_caches() -> None:
    obj = _unique_name_object()
    iface = obj.get_interface(_IFACE_NAME)
    assert isinstance(iface, _StubInterface)
    assert iface.introspection.name == _IFACE_NAME
    assert obj.get_interface(_IFACE_NAME) is iface


def test_get_interface_unknown_raises() -> None:
    obj = _unique_name_object()
    with pytest.raises(InterfaceNotFoundError, match="interface not found"):
        obj.get_interface("org.example.Missing")


def test_get_interface_requests_name_owner_for_well_known_name(monkeypatch) -> None:
    captured: list = []

    def record(self, message, callback=None):
        captured.append((message, callback))

    monkeypatch.setattr(BaseMessageBus, "_call", record)
    obj = BaseProxyObject(
        "org.example.Name", "/org/example", _IFACE_XML, _offline_bus(), _StubInterface
    )
    obj.get_interface(_IFACE_NAME)

    assert len(captured) == 1
    message, _notify = captured[0]
    assert message.member == "GetNameOwner"
    assert message.body == ["org.example.Name"]


def _owner_notify(monkeypatch):
    captured: list = []

    def record(self, message, callback=None):
        captured.append((message, callback))

    monkeypatch.setattr(BaseMessageBus, "_call", record)
    bus = _offline_bus()
    obj = BaseProxyObject(
        "org.example.Name", "/org/example", _IFACE_XML, bus, _StubInterface
    )
    obj.get_interface(_IFACE_NAME)
    return bus, captured[0][1]


def test_owner_notify_records_owner_on_success(monkeypatch) -> None:
    bus, notify = _owner_notify(monkeypatch)
    notify(_method_return(signature="s", body=[":1.5"]), None)
    assert bus._name_owners["org.example.Name"] == ":1.5"


def test_owner_notify_ignores_transport_error(monkeypatch) -> None:
    bus, notify = _owner_notify(monkeypatch)
    notify(None, RuntimeError("boom"))
    assert "org.example.Name" not in bus._name_owners


def test_owner_notify_ignores_name_has_no_owner(monkeypatch) -> None:
    bus, notify = _owner_notify(monkeypatch)
    msg = Message(
        message_type=MessageType.ERROR,
        error_name=ErrorType.NAME_HAS_NO_OWNER.value,
        reply_serial=1,
        signature="s",
        body=["no owner"],
    )
    notify(msg, None)
    assert "org.example.Name" not in bus._name_owners


def test_owner_notify_logs_other_error(monkeypatch) -> None:
    bus, notify = _owner_notify(monkeypatch)
    msg = Message(
        message_type=MessageType.ERROR,
        error_name="com.example.Boom",
        reply_serial=1,
        signature="s",
        body=["kaboom"],
    )
    notify(msg, None)
    assert "org.example.Name" not in bus._name_owners


def _signal(signature: str = "s", body: list | None = None) -> Message:
    return Message(
        message_type=MessageType.SIGNAL,
        sender=":1.42",
        path="/org/example",
        interface=_IFACE_NAME,
        member="Tick",
        signature=signature,
        body=body if body is not None else ["payload"],
    )


def test_message_handler_dispatches_to_all_handlers(monkeypatch) -> None:
    monkeypatch.setattr(BaseMessageBus, "_call", lambda *a, **k: None)
    obj = _unique_name_object()
    iface = obj.get_interface(_IFACE_NAME)

    raw: list = []
    unpacked: list = []
    unpacked2: list = []
    iface.on_tick(lambda v: raw.append(v))
    iface.on_tick(lambda v: unpacked.append(v), unpack_variants=True)
    # Second unpack handler exercises the cached-unpack branch.
    iface.on_tick(lambda v: unpacked2.append(v), unpack_variants=True)

    iface._message_handler(_signal(body=["hello"]))
    assert raw == ["hello"]
    assert unpacked == ["hello"]
    assert unpacked2 == ["hello"]


def test_message_handler_ignores_signature_mismatch(monkeypatch) -> None:
    monkeypatch.setattr(BaseMessageBus, "_call", lambda *a, **k: None)
    obj = _unique_name_object()
    iface = obj.get_interface(_IFACE_NAME)

    seen: list = []
    iface.on_tick(lambda v: seen.append(v))

    iface._message_handler(_signal(signature="i", body=[1]))
    assert seen == []


def test_off_signal_removes_handler_and_match_rule(monkeypatch) -> None:
    monkeypatch.setattr(BaseMessageBus, "_call", lambda *a, **k: None)
    obj = _unique_name_object()
    iface = obj.get_interface(_IFACE_NAME)

    def handler(v):
        pass

    iface.on_tick(handler)
    assert "Tick" in iface._signal_handlers

    iface.off_tick(handler)
    assert "Tick" not in iface._signal_handlers


def test_off_signal_unregistered_handler_is_noop(monkeypatch) -> None:
    monkeypatch.setattr(BaseMessageBus, "_call", lambda *a, **k: None)
    obj = _unique_name_object()
    iface = obj.get_interface(_IFACE_NAME)
    # Never registered — off must swallow the KeyError/ValueError.
    iface.off_tick(lambda v: None)
    assert iface._signal_handlers == {}


def test_off_signal_keeps_other_handlers(monkeypatch) -> None:
    monkeypatch.setattr(BaseMessageBus, "_call", lambda *a, **k: None)
    obj = _unique_name_object()
    iface = obj.get_interface(_IFACE_NAME)

    def first(v):
        pass

    def second(v):
        pass

    iface.on_tick(first)
    iface.on_tick(second)
    iface.off_tick(first)
    assert len(iface._signal_handlers["Tick"]) == 1


def test_message_handler_ignores_unmatched_message(monkeypatch) -> None:
    monkeypatch.setattr(BaseMessageBus, "_call", lambda *a, **k: None)
    obj = _unique_name_object()
    iface = obj.get_interface(_IFACE_NAME)

    seen: list = []
    iface.on_tick(lambda v: seen.append(v))

    wrong_path = _signal()
    wrong_path.path = "/other"
    iface._message_handler(wrong_path)
    assert seen == []


def test_message_handler_ignores_foreign_sender(monkeypatch) -> None:
    monkeypatch.setattr(BaseMessageBus, "_call", lambda *a, **k: None)
    obj = _unique_name_object()
    iface = obj.get_interface(_IFACE_NAME)

    seen: list = []
    iface.on_tick(lambda v: seen.append(v))

    foreign = _signal()
    foreign.sender = ":9.9"
    iface._message_handler(foreign)
    assert seen == []


def test_message_handler_ignores_unknown_signal_name(monkeypatch) -> None:
    monkeypatch.setattr(BaseMessageBus, "_call", lambda *a, **k: None)
    obj = _unique_name_object()
    iface = obj.get_interface(_IFACE_NAME)

    called: list = []
    # A member registered as a handler but absent from the introspected signals.
    iface._signal_handlers["Ghost"] = [object()]
    ghost = _signal()
    ghost.member = "Ghost"
    iface._message_handler(ghost)
    assert called == []


def test_on_signal_rejects_required_keyword_only_param(monkeypatch) -> None:
    monkeypatch.setattr(BaseMessageBus, "_call", lambda *a, **k: None)
    obj = _unique_name_object()
    iface = obj.get_interface(_IFACE_NAME)

    def handler(v, *, required):
        pass

    with pytest.raises(TypeError, match="required keyword only parameters"):
        iface.on_tick(handler)


def test_on_signal_rejects_wrong_positional_count(monkeypatch) -> None:
    monkeypatch.setattr(BaseMessageBus, "_call", lambda *a, **k: None)
    obj = _unique_name_object()
    iface = obj.get_interface(_IFACE_NAME)

    with pytest.raises(TypeError, match="positional parameters"):
        iface.on_tick(lambda a, b: None)
