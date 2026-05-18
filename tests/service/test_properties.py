import asyncio
from typing import Annotated

import pytest

from dbus_fast import (
    DBusError,
    ErrorType,
    Message,
    MessageType,
    PropertyAccess,
    Variant,
)
from dbus_fast.aio import MessageBus
from dbus_fast.annotations import DBusSignature, DBusStr, DBusUInt64
from dbus_fast.service import ServiceInterface, dbus_method, dbus_property

# Type alias since this is used multiple times in this file.
TestDBusArrayOfStringTuple = Annotated[list[tuple[str, str]], DBusSignature("a(ss)")]


class ExampleInterface(ServiceInterface):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._string_prop = "hi"
        self._readonly_prop = 100
        self._disabled_prop = "1234"
        self._container_prop = [("hello", "world")]
        self._renamed_prop = "65"

    @dbus_property()
    def string_prop(self) -> DBusStr:
        return self._string_prop

    @string_prop.setter
    def string_prop_setter(self, val: DBusStr) -> None:
        self._string_prop = val

    @dbus_property(PropertyAccess.READ)
    def readonly_prop(self) -> DBusUInt64:
        return self._readonly_prop

    @dbus_property()
    def container_prop(self) -> TestDBusArrayOfStringTuple:
        return self._container_prop

    @container_prop.setter
    def container_prop(self, val: TestDBusArrayOfStringTuple):
        self._container_prop = val

    @dbus_property(name="renamed_prop")
    def original_name(self) -> DBusStr:
        return self._renamed_prop

    @original_name.setter
    def original_name_setter(self, val: DBusStr) -> None:
        self._renamed_prop = val

    @dbus_property(disabled=True)
    def disabled_prop(self) -> DBusStr:
        return self._disabled_prop

    @disabled_prop.setter
    def disabled_prop(self, val: DBusStr) -> None:
        self._disabled_prop = val

    @dbus_property(disabled=True)
    def throws_error(self) -> DBusStr:
        raise DBusError("test.error", "told you so")

    @throws_error.setter
    def throws_error(self, val: DBusStr) -> None:
        raise DBusError("test.error", "told you so")

    @dbus_property(PropertyAccess.READ, disabled=True)
    def returns_wrong_type(self) -> DBusStr:
        return 5  # type: ignore[return-value]

    @dbus_method()
    def do_emit_properties_changed(self):
        changed = {"string_prop": "asdf"}
        invalidated = ["container_prop"]
        self.emit_properties_changed(changed, invalidated)


class AsyncInterface(ServiceInterface):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._string_prop = "hi"
        self._readonly_prop = 100
        self._disabled_prop = "1234"
        self._container_prop = [("hello", "world")]
        self._renamed_prop = "65"

    @dbus_property()
    async def string_prop(self) -> DBusStr:
        return self._string_prop

    @string_prop.setter
    async def string_prop_setter(self, val: DBusStr) -> None:
        self._string_prop = val

    @dbus_property(PropertyAccess.READ)
    async def readonly_prop(self) -> DBusUInt64:
        return self._readonly_prop

    @dbus_property()
    async def container_prop(self) -> TestDBusArrayOfStringTuple:
        return self._container_prop

    @container_prop.setter
    async def container_prop(self, val: TestDBusArrayOfStringTuple):
        self._container_prop = val

    @dbus_property(name="renamed_prop")
    async def original_name(self) -> DBusStr:
        return self._renamed_prop

    @original_name.setter
    async def original_name_setter(self, val: DBusStr) -> None:
        self._renamed_prop = val

    @dbus_property(disabled=True)
    async def disabled_prop(self) -> DBusStr:
        return self._disabled_prop

    @disabled_prop.setter
    async def disabled_prop(self, val: DBusStr) -> None:
        self._disabled_prop = val

    @dbus_property(disabled=True)
    async def throws_error(self) -> DBusStr:
        raise DBusError("test.error", "told you so")

    @throws_error.setter
    async def throws_error(self, val: DBusStr) -> None:
        raise DBusError("test.error", "told you so")

    @dbus_property(PropertyAccess.READ, disabled=True)
    async def returns_wrong_type(self) -> DBusStr:
        return 5  # type: ignore[return-value]

    @dbus_method()
    def do_emit_properties_changed(self):
        changed = {"string_prop": "asdf"}
        invalidated = ["container_prop"]
        self.emit_properties_changed(changed, invalidated)


@pytest.mark.parametrize("interface_class", [ExampleInterface, AsyncInterface])
@pytest.mark.asyncio
async def test_property_methods(interface_class):
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    interface = interface_class("test.interface")
    export_path = "/test/path"
    bus1.export(export_path, interface)

    async def call_properties(member, signature, body):
        return await bus2.call(
            Message(
                destination=bus1.unique_name,
                path=export_path,
                interface="org.freedesktop.DBus.Properties",
                member=member,
                signature=signature,
                body=body,
            )
        )

    result = await call_properties("GetAll", "s", [interface.name])

    assert result.message_type == MessageType.METHOD_RETURN, result.body[0]
    assert result.signature == "a{sv}"
    assert result.body == [
        {
            "string_prop": Variant("s", interface._string_prop),
            "readonly_prop": Variant("t", interface._readonly_prop),
            "container_prop": Variant("a(ss)", interface._container_prop),
            "renamed_prop": Variant("s", interface._renamed_prop),
        }
    ]

    result = await call_properties("Get", "ss", [interface.name, "string_prop"])
    assert result.message_type == MessageType.METHOD_RETURN, result.body[0]
    assert result.signature == "v"
    assert result.body == [Variant("s", "hi")]

    result = await call_properties(
        "Set", "ssv", [interface.name, "string_prop", Variant("s", "ho")]
    )
    assert result.message_type == MessageType.METHOD_RETURN, result.body[0]
    assert interface._string_prop == "ho"
    if interface_class is AsyncInterface:
        assert "ho", await interface.string_prop()
    else:
        assert "ho", interface.string_prop

    result = await call_properties(
        "Set", "ssv", [interface.name, "readonly_prop", Variant("t", 100)]
    )
    assert result.message_type == MessageType.ERROR, result.body[0]
    assert result.error_name == ErrorType.PROPERTY_READ_ONLY.value, result.body[0]

    result = await call_properties(
        "Set", "ssv", [interface.name, "disabled_prop", Variant("s", "asdf")]
    )
    assert result.message_type == MessageType.ERROR, result.body[0]
    assert result.error_name == ErrorType.UNKNOWN_PROPERTY.value

    result = await call_properties(
        "Set", "ssv", [interface.name, "not_a_prop", Variant("s", "asdf")]
    )
    assert result.message_type == MessageType.ERROR, result.body[0]
    assert result.error_name == ErrorType.UNKNOWN_PROPERTY.value

    # wrong type
    result = await call_properties(
        "Set", "ssv", [interface.name, "string_prop", Variant("t", 100)]
    )
    assert result.message_type == MessageType.ERROR
    assert result.error_name == ErrorType.INVALID_SIGNATURE.value

    # enable the erroring properties so we can test them
    for prop in ServiceInterface._get_properties(interface):
        if prop.name in ["throws_error", "returns_wrong_type"]:
            prop.disabled = False

    result = await call_properties("Get", "ss", [interface.name, "returns_wrong_type"])
    assert result.message_type == MessageType.ERROR, result.body[0]
    assert result.error_name == ErrorType.SERVICE_ERROR.value

    result = await call_properties(
        "Set", "ssv", [interface.name, "throws_error", Variant("s", "ho")]
    )
    assert result.message_type == MessageType.ERROR, result.body[0]
    assert result.error_name == "test.error"
    assert result.body == ["told you so"]

    result = await call_properties("Get", "ss", [interface.name, "throws_error"])
    assert result.message_type == MessageType.ERROR, result.body[0]
    assert result.error_name == "test.error"
    assert result.body == ["told you so"]

    result = await call_properties("GetAll", "s", [interface.name])
    assert result.message_type == MessageType.ERROR, result.body[0]
    assert result.error_name == "test.error"
    assert result.body == ["told you so"]

    bus1.disconnect()
    bus2.disconnect()
    await asyncio.wait_for(bus1.wait_for_disconnect(), timeout=1)
    await asyncio.wait_for(bus2.wait_for_disconnect(), timeout=1)


@pytest.mark.parametrize("interface_class", [ExampleInterface, AsyncInterface])
@pytest.mark.asyncio
async def test_property_changed_signal(interface_class):
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    await bus2.call(
        Message(
            destination="org.freedesktop.DBus",
            path="/org/freedesktop/DBus",
            interface="org.freedesktop.DBus",
            member="AddMatch",
            signature="s",
            body=[f"sender={bus1.unique_name}"],
        )
    )

    interface = interface_class("test.interface")
    export_path = "/test/path"
    bus1.export(export_path, interface)

    async def wait_for_message():
        # TODO timeout
        future = asyncio.get_running_loop().create_future()

        def message_handler(signal):
            if signal.interface == "org.freedesktop.DBus.Properties":
                bus2.remove_message_handler(message_handler)
                future.set_result(signal)

        bus2.add_message_handler(message_handler)
        return await future

    bus2.send(
        Message(
            destination=bus1.unique_name,
            interface=interface.name,
            path=export_path,
            member="do_emit_properties_changed",
        )
    )

    signal = await wait_for_message()
    assert signal.interface == "org.freedesktop.DBus.Properties"
    assert signal.member == "PropertiesChanged"
    assert signal.signature == "sa{sv}as"
    assert signal.body == [
        interface.name,
        {"string_prop": Variant("s", "asdf")},
        ["container_prop"],
    ]

    bus1.disconnect()
    bus2.disconnect()
    await asyncio.wait_for(bus1.wait_for_disconnect(), timeout=1)
    await asyncio.wait_for(bus2.wait_for_disconnect(), timeout=1)


class _Bag(ServiceInterface):
    def __init__(self) -> None:
        super().__init__("test.bag")


@pytest.mark.asyncio
async def test_add_property_dynamic_read_write() -> None:
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    state = {"v": "alpha"}
    bag = _Bag()
    bag.add_property(
        "dyn_str",
        "s",
        lambda iface: state["v"],
        lambda iface, value: state.update(v=value),
    )
    bus1.export("/dyn", bag)

    result = await bus2.call(
        Message(
            destination=bus1.unique_name,
            path="/dyn",
            interface="org.freedesktop.DBus.Properties",
            member="Get",
            signature="ss",
            body=["test.bag", "dyn_str"],
        )
    )
    assert result.message_type == MessageType.METHOD_RETURN
    assert result.body == [Variant("s", "alpha")]

    result = await bus2.call(
        Message(
            destination=bus1.unique_name,
            path="/dyn",
            interface="org.freedesktop.DBus.Properties",
            member="Set",
            signature="ssv",
            body=["test.bag", "dyn_str", Variant("s", "beta")],
        )
    )
    assert result.message_type == MessageType.METHOD_RETURN
    assert state["v"] == "beta"

    result = await bus2.call(
        Message(
            destination=bus1.unique_name,
            path="/dyn",
            interface="org.freedesktop.DBus.Properties",
            member="GetAll",
            signature="s",
            body=["test.bag"],
        )
    )
    assert result.body == [{"dyn_str": Variant("s", "beta")}]

    bus1.disconnect()
    bus2.disconnect()
    await asyncio.wait_for(bus1.wait_for_disconnect(), timeout=1)
    await asyncio.wait_for(bus2.wait_for_disconnect(), timeout=1)


@pytest.mark.asyncio
async def test_add_property_dynamic_read_only_set_rejected() -> None:
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    bag = _Bag()
    bag.add_property("ro_prop", "u", lambda iface: 42, access=PropertyAccess.READ)
    bus1.export("/dyn", bag)

    result = await bus2.call(
        Message(
            destination=bus1.unique_name,
            path="/dyn",
            interface="org.freedesktop.DBus.Properties",
            member="Set",
            signature="ssv",
            body=["test.bag", "ro_prop", Variant("u", 99)],
        )
    )
    assert result.message_type == MessageType.ERROR
    assert result.error_name == ErrorType.PROPERTY_READ_ONLY.value

    bus1.disconnect()
    bus2.disconnect()
    await asyncio.wait_for(bus1.wait_for_disconnect(), timeout=1)
    await asyncio.wait_for(bus2.wait_for_disconnect(), timeout=1)


@pytest.mark.asyncio
async def test_add_property_dynamic_async_getter_and_setter() -> None:
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    state = {"v": 7}

    async def getter(_iface):
        return state["v"]

    async def setter(_iface, value):
        state["v"] = value

    bag = _Bag()
    bag.add_property("dyn_uint", "u", getter, setter)
    bus1.export("/dyn", bag)

    result = await bus2.call(
        Message(
            destination=bus1.unique_name,
            path="/dyn",
            interface="org.freedesktop.DBus.Properties",
            member="Get",
            signature="ss",
            body=["test.bag", "dyn_uint"],
        )
    )
    assert result.body == [Variant("u", 7)]

    result = await bus2.call(
        Message(
            destination=bus1.unique_name,
            path="/dyn",
            interface="org.freedesktop.DBus.Properties",
            member="Set",
            signature="ssv",
            body=["test.bag", "dyn_uint", Variant("u", 19)],
        )
    )
    assert result.message_type == MessageType.METHOD_RETURN
    assert state["v"] == 19

    bus1.disconnect()
    bus2.disconnect()
    await asyncio.wait_for(bus1.wait_for_disconnect(), timeout=1)
    await asyncio.wait_for(bus2.wait_for_disconnect(), timeout=1)


@pytest.mark.asyncio
async def test_add_property_dynamic_disabled_hidden() -> None:
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    bag = _Bag()
    bag.add_property(
        "hidden",
        "s",
        lambda iface: "secret",
        access=PropertyAccess.READ,
        disabled=True,
    )
    bus1.export("/dyn", bag)

    result = await bus2.call(
        Message(
            destination=bus1.unique_name,
            path="/dyn",
            interface="org.freedesktop.DBus.Properties",
            member="GetAll",
            signature="s",
            body=["test.bag"],
        )
    )
    assert result.body == [{}]

    result = await bus2.call(
        Message(
            destination=bus1.unique_name,
            path="/dyn",
            interface="org.freedesktop.DBus.Properties",
            member="Get",
            signature="ss",
            body=["test.bag", "hidden"],
        )
    )
    assert result.message_type == MessageType.ERROR
    assert result.error_name == ErrorType.UNKNOWN_PROPERTY.value

    intr_xml = bag.introspect()
    assert all(p.name != "hidden" for p in intr_xml.properties)

    bus1.disconnect()
    bus2.disconnect()
    await asyncio.wait_for(bus1.wait_for_disconnect(), timeout=1)
    await asyncio.wait_for(bus2.wait_for_disconnect(), timeout=1)


@pytest.mark.asyncio
async def test_add_property_dynamic_emit_properties_changed() -> None:
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    await bus2.call(
        Message(
            destination="org.freedesktop.DBus",
            path="/org/freedesktop/DBus",
            interface="org.freedesktop.DBus",
            member="AddMatch",
            signature="s",
            body=[f"sender={bus1.unique_name}"],
        )
    )

    state = {"v": "one"}
    bag = _Bag()
    bag.add_property(
        "dyn_str",
        "s",
        lambda iface: state["v"],
        lambda iface, value: state.update(v=value),
    )
    bus1.export("/dyn", bag)

    future = asyncio.get_running_loop().create_future()

    def handler(signal):
        if signal.interface == "org.freedesktop.DBus.Properties":
            bus2.remove_message_handler(handler)
            future.set_result(signal)

    bus2.add_message_handler(handler)

    state["v"] = "two"
    bag.emit_properties_changed({"dyn_str": "two"})

    signal = await asyncio.wait_for(future, timeout=2)
    assert signal.body == [
        "test.bag",
        {"dyn_str": Variant("s", "two")},
        [],
    ]

    bus1.disconnect()
    bus2.disconnect()
    await asyncio.wait_for(bus1.wait_for_disconnect(), timeout=1)
    await asyncio.wait_for(bus2.wait_for_disconnect(), timeout=1)


def test_add_property_validation_errors() -> None:
    bag = _Bag()

    with pytest.raises(TypeError, match="name must be a string"):
        bag.add_property(123, "s", lambda iface: "x")  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="signature must be a string"):
        bag.add_property("p", 123, lambda iface: "x")  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="getter must be callable"):
        bag.add_property("p", "s", "not callable")  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="setter must be callable"):
        bag.add_property("p", "s", lambda iface: "x", setter=123)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="access must be a PropertyAccess"):
        bag.add_property(
            "p",
            "s",
            lambda iface: "x",
            access="read",  # type: ignore[arg-type]
        )

    with pytest.raises(TypeError, match="disabled must be a bool"):
        bag.add_property(
            "p",
            "s",
            lambda iface: "x",
            disabled="yes",  # type: ignore[arg-type]
        )

    with pytest.raises(ValueError, match="does not have a setter"):
        bag.add_property("rw_no_setter", "s", lambda iface: "x")

    with pytest.raises(ValueError, match="must be a single complete type"):
        bag.add_property(
            "two_types",
            "ss",
            lambda iface: ("a", "b"),
            lambda iface, v: None,
        )

    bag.add_property(
        "dup",
        "s",
        lambda iface: "x",
        lambda iface, v: None,
    )
    with pytest.raises(ValueError, match="already registered"):
        bag.add_property(
            "dup",
            "s",
            lambda iface: "y",
            lambda iface, v: None,
        )


def test_dbus_property_decorator_extra_params_rejected() -> None:
    with pytest.raises(ValueError, match='must only have the "self" input parameter'):

        class Bad(ServiceInterface):
            def __init__(self) -> None:
                super().__init__("test.bad")

            @dbus_property()
            def two_params(self, extra) -> "s":  # type: ignore[no-untyped-def]
                return "x"


def test_dbus_property_decorator_missing_return_annotation_rejected() -> None:
    with pytest.raises(ValueError, match="must specify the dbus type string"):

        class Bad(ServiceInterface):
            def __init__(self) -> None:
                super().__init__("test.bad")

            @dbus_property()
            def no_annotation(self):  # type: ignore[no-untyped-def]
                return "x"
