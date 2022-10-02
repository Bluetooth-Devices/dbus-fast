import asyncio

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
from dbus_fast.service import ServiceInterface, dbus_property, method


class ExampleInterface(ServiceInterface):
    def __init__(self, name):
        super().__init__(name)
        self._string_prop = "hi"
        self._readonly_prop = 100
        self._disabled_prop = "1234"
        self._container_prop = [["hello", "world"]]
        self._renamed_prop = "65"

    @dbus_property()
    def string_prop(self) -> "s":
        return self._string_prop

    @string_prop.setter
    def string_prop_setter(self, val: "s"):
        self._string_prop = val

    @dbus_property(PropertyAccess.READ)
    def readonly_prop(self) -> "t":
        return self._readonly_prop

    @dbus_property()
    def container_prop(self) -> "a(ss)":
        return self._container_prop

    @container_prop.setter
    def container_prop(self, val: "a(ss)"):
        self._container_prop = val

    @dbus_property(name="renamed_prop")
    def original_name(self) -> "s":
        return self._renamed_prop

    @original_name.setter
    def original_name_setter(self, val: "s"):
        self._renamed_prop = val

    @dbus_property(disabled=True)
    def disabled_prop(self) -> "s":
        return self._disabled_prop

    @disabled_prop.setter
    def disabled_prop(self, val: "s"):
        self._disabled_prop = val

    @dbus_property(disabled=True)
    def throws_error(self) -> "s":
        raise DBusError("test.error", "told you so")

    @throws_error.setter
    def throws_error(self, val: "s"):
        raise DBusError("test.error", "told you so")

    @dbus_property(PropertyAccess.READ, disabled=True)
    def returns_wrong_type(self) -> "s":
        return 5

    @method()
    def do_emit_properties_changed(self):
        changed = {"string_prop": "asdf"}
        invalidated = ["container_prop"]
        self.emit_properties_changed(changed, invalidated)


class AsyncInterface(ServiceInterface):
    def __init__(self, name):
        super().__init__(name)
        self._string_prop = "hi"
        self._readonly_prop = 100
        self._disabled_prop = "1234"
        self._container_prop = [["hello", "world"]]
        self._renamed_prop = "65"

    @dbus_property()
    async def string_prop(self) -> "s":
        return self._string_prop

    @string_prop.setter
    async def string_prop_setter(self, val: "s"):
        self._string_prop = val

    @dbus_property(PropertyAccess.READ)
    async def readonly_prop(self) -> "t":
        return self._readonly_prop

    @dbus_property()
    async def container_prop(self) -> "a(ss)":
        return self._container_prop

    @container_prop.setter
    async def container_prop(self, val: "a(ss)"):
        self._container_prop = val

    @dbus_property(name="renamed_prop")
    async def original_name(self) -> "s":
        return self._renamed_prop

    @original_name.setter
    async def original_name_setter(self, val: "s"):
        self._renamed_prop = val

    @dbus_property(disabled=True)
    async def disabled_prop(self) -> "s":
        return self._disabled_prop

    @disabled_prop.setter
    async def disabled_prop(self, val: "s"):
        self._disabled_prop = val

    @dbus_property(disabled=True)
    async def throws_error(self) -> "s":
        raise DBusError("test.error", "told you so")

    @throws_error.setter
    async def throws_error(self, val: "s"):
        raise DBusError("test.error", "told you so")

    @dbus_property(PropertyAccess.READ, disabled=True)
    async def returns_wrong_type(self) -> "s":
        return 5

    @method()
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
    bus1._sock.close()
    bus2._sock.close()


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
    bus1._sock.close()
    bus2._sock.close()
