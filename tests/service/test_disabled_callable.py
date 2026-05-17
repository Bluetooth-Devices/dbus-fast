from typing import Annotated

import pytest

from dbus_fast import (
    ErrorType,
    Message,
    MessageType,
    PropertyAccess,
    Variant,
)
from dbus_fast.aio import MessageBus
from dbus_fast.annotations import DBusSignature, DBusStr, DBusUInt32
from dbus_fast.errors import SignalDisabledError
from dbus_fast.service import (
    ServiceInterface,
    dbus_method,
    dbus_property,
    dbus_signal,
)


class CallableDisabledInterface(ServiceInterface):
    def __init__(self, name: str, hide: bool) -> None:
        super().__init__(name)
        self._hide = hide
        self._value = 42

    @dbus_method(disabled=lambda self: self._hide)
    def hidden_method(self, arg: DBusStr) -> DBusStr:
        return arg

    @dbus_method()
    def visible_method(self) -> DBusStr:
        return "ok"

    @dbus_signal(disabled=lambda self: self._hide)
    def hidden_signal(self) -> Annotated[str, DBusSignature("s")]:
        return "ping"

    @dbus_property(disabled=lambda self: self._hide)
    def hidden_prop(self) -> DBusUInt32:
        return self._value

    @hidden_prop.setter
    def hidden_prop(self, val: DBusUInt32) -> None:
        self._value = val

    @dbus_property(PropertyAccess.READ)
    def visible_prop(self) -> DBusUInt32:
        return self._value


def test_disabled_callable_stored_as_callable():
    interface = CallableDisabledInterface("test.cb", True)
    methods = ServiceInterface._get_methods(interface)
    signals = ServiceInterface._get_signals(interface)
    properties = ServiceInterface._get_properties(interface)

    hidden_method = next(m for m in methods if m.name == "hidden_method")
    assert callable(hidden_method.disabled)

    hidden_signal = next(s for s in signals if s.name == "hidden_signal")
    assert callable(hidden_signal.disabled)

    hidden_prop = next(p for p in properties if p.name == "hidden_prop")
    assert callable(hidden_prop.disabled)


def test_introspection_reflects_per_instance_state():
    hidden = CallableDisabledInterface("test.cb1", True)
    intr_hidden = hidden.introspect()
    method_names = {m.name for m in intr_hidden.methods}
    prop_names = {p.name for p in intr_hidden.properties}
    signal_names = {s.name for s in intr_hidden.signals}
    assert "hidden_method" not in method_names
    assert "hidden_prop" not in prop_names
    assert "hidden_signal" not in signal_names
    assert "visible_method" in method_names
    assert "visible_prop" in prop_names

    visible = CallableDisabledInterface("test.cb2", False)
    intr_visible = visible.introspect()
    method_names = {m.name for m in intr_visible.methods}
    prop_names = {p.name for p in intr_visible.properties}
    signal_names = {s.name for s in intr_visible.signals}
    assert "hidden_method" in method_names
    assert "hidden_prop" in prop_names
    assert "hidden_signal" in signal_names


def test_disabled_evaluated_dynamically():
    interface = CallableDisabledInterface("test.cb3", True)
    assert "hidden_method" not in {m.name for m in interface.introspect().methods}
    interface._hide = False
    assert "hidden_method" in {m.name for m in interface.introspect().methods}


def test_disabled_signal_raises_when_callable_returns_true():
    interface = CallableDisabledInterface("test.cb4", True)
    with pytest.raises(SignalDisabledError):
        interface.hidden_signal()

    interface._hide = False
    interface.hidden_signal()


@pytest.mark.asyncio
async def test_method_dispatch_honours_callable_disabled():
    name = "dbus.test.disabled.callable.method"
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    iface_hidden = CallableDisabledInterface(name, True)
    bus1.export("/test/path", iface_hidden)

    reply = await bus1.request_name(name)
    assert reply

    # call hidden_method — must be reported as UNKNOWN_METHOD while hidden
    msg = Message(
        destination=name,
        path="/test/path",
        interface=name,
        member="hidden_method",
        signature="s",
        body=["hello"],
    )
    result = await bus2.call(msg)
    assert result.message_type == MessageType.ERROR
    assert result.error_name == ErrorType.UNKNOWN_METHOD.value

    # flip the flag and call again — now must succeed
    iface_hidden._hide = False
    msg = Message(
        destination=name,
        path="/test/path",
        interface=name,
        member="hidden_method",
        signature="s",
        body=["hello"],
    )
    result = await bus2.call(msg)
    assert result.message_type == MessageType.METHOD_RETURN
    assert result.body == ["hello"]

    bus1.disconnect()
    bus2.disconnect()


@pytest.mark.asyncio
async def test_property_get_set_honours_callable_disabled():
    name = "dbus.test.disabled.callable.prop"
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    iface = CallableDisabledInterface(name, True)
    bus1.export("/test/path", iface)

    reply = await bus1.request_name(name)
    assert reply

    async def call_props(member: str, signature: str, body: list) -> Message:
        return await bus2.call(
            Message(
                destination=name,
                path="/test/path",
                interface="org.freedesktop.DBus.Properties",
                member=member,
                signature=signature,
                body=body,
            )
        )

    # Get hidden_prop while disabled: UNKNOWN_PROPERTY
    result = await call_props("Get", "ss", [name, "hidden_prop"])
    assert result.message_type == MessageType.ERROR
    assert result.error_name == ErrorType.UNKNOWN_PROPERTY.value

    # Set hidden_prop while disabled: UNKNOWN_PROPERTY
    result = await call_props("Set", "ssv", [name, "hidden_prop", Variant("u", 99)])
    assert result.message_type == MessageType.ERROR
    assert result.error_name == ErrorType.UNKNOWN_PROPERTY.value

    # GetAll while hidden -> hidden_prop excluded
    result = await call_props("GetAll", "s", [name])
    assert result.message_type == MessageType.METHOD_RETURN
    assert "hidden_prop" not in result.body[0]
    assert "visible_prop" in result.body[0]

    # Enable the property dynamically
    iface._hide = False

    result = await call_props("Get", "ss", [name, "hidden_prop"])
    assert result.message_type == MessageType.METHOD_RETURN
    assert result.body[0].value == 42

    result = await call_props("Set", "ssv", [name, "hidden_prop", Variant("u", 99)])
    assert result.message_type == MessageType.METHOD_RETURN
    assert iface._value == 99

    result = await call_props("GetAll", "s", [name])
    assert result.message_type == MessageType.METHOD_RETURN
    assert "hidden_prop" in result.body[0]

    bus1.disconnect()
    bus2.disconnect()


def test_decorators_reject_non_bool_non_callable():
    with pytest.raises(TypeError, match="disabled"):
        dbus_method(disabled="yes")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="disabled"):
        dbus_signal(disabled=1)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="disabled"):
        dbus_property(disabled=0)  # type: ignore[arg-type]
