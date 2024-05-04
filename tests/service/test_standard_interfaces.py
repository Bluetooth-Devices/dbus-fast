import pytest

from dbus_fast import Message, MessageType
from dbus_fast import introspection as intr
from dbus_fast.aio import MessageBus
from dbus_fast.constants import ErrorType
from dbus_fast.service import PropertyAccess, ServiceInterface, dbus_property
from dbus_fast.signature import Variant

standard_interfaces_count = len(intr.Node.default().interfaces)


class ExampleInterface(ServiceInterface):
    def __init__(self, name):
        super().__init__(name)


class ExampleComplexInterface(ServiceInterface):
    def __init__(self, name):
        self._foo = 42
        self._bar = "str"
        self._async_prop = "async"
        super().__init__(name)

    @dbus_property(access=PropertyAccess.READ)
    def Foo(self) -> "y":
        return self._foo

    @dbus_property(access=PropertyAccess.READ)
    def Bar(self) -> "s":
        return self._bar

    @dbus_property(access=PropertyAccess.READ)
    async def AsyncProp(self) -> "s":
        return self._async_prop


@pytest.mark.asyncio
async def test_introspectable_interface():
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    interface = ExampleInterface("test.interface")
    interface2 = ExampleInterface("test.interface2")

    export_path = "/test/path"
    bus1.export(export_path, interface)
    bus1.export(export_path, interface2)

    reply = await bus2.call(
        Message(
            destination=bus1.unique_name,
            path=export_path,
            interface="org.freedesktop.DBus.Introspectable",
            member="Introspect",
        )
    )

    assert reply.message_type == MessageType.METHOD_RETURN, reply.body[0]
    assert reply.signature == "s"
    node = intr.Node.parse(reply.body[0])
    assert len(node.interfaces) == standard_interfaces_count + 2
    assert node.interfaces[-1].name == "test.interface2"
    assert node.interfaces[-2].name == "test.interface"
    assert not node.nodes

    # introspect works on every path
    reply = await bus2.call(
        Message(
            destination=bus1.unique_name,
            path="/path/doesnt/exist",
            interface="org.freedesktop.DBus.Introspectable",
            member="Introspect",
        )
    )
    assert reply.message_type == MessageType.METHOD_RETURN, reply.body[0]
    assert reply.signature == "s"
    node = intr.Node.parse(reply.body[0])
    assert not node.interfaces
    assert not node.nodes

    bus1.disconnect()
    bus2.disconnect()


@pytest.mark.asyncio
async def test_introspect_matching_sub_paths():
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    interface = ExampleInterface("test.interface1")

    bus1.export("/a/test/path1", interface)
    bus1.export("/a/test/path10", interface)
    bus1.export("/a/subpath/a/test/path2", interface)

    async def introspect_subpath(path, expected_subnodes):
        reply = await bus2.call(
            Message(
                destination=bus1.unique_name,
                path=path,
                interface="org.freedesktop.DBus.Introspectable",
                member="Introspect",
            )
        )
        assert reply.signature == "s"
        node = intr.Node.parse(reply.body[0])
        assert {n.name for n in node.nodes} == expected_subnodes

    await introspect_subpath("/", {"a"})
    await introspect_subpath("/a", {"test", "subpath"})
    await introspect_subpath("/a/test", {"path1", "path10"})
    await introspect_subpath("/a/test/path1", set())
    await introspect_subpath("/a/test/path10", set())
    await introspect_subpath("/a/subpath/a/test", {"path2"})
    await introspect_subpath("/a/subpath/a/test/path2", set())

    bus1.disconnect()
    bus2.disconnect()


@pytest.mark.asyncio
async def test_peer_interface():
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    reply = await bus2.call(
        Message(
            destination=bus1.unique_name,
            path="/path/doesnt/exist",
            interface="org.freedesktop.DBus.Peer",
            member="Ping",
        )
    )

    assert reply.message_type == MessageType.METHOD_RETURN, reply.body[0]
    assert reply.signature == ""

    reply = await bus2.call(
        Message(
            destination=bus1.unique_name,
            path="/path/doesnt/exist",
            interface="org.freedesktop.DBus.Peer",
            member="GetMachineId",
            signature="",
        )
    )

    assert reply.message_type == MessageType.METHOD_RETURN, reply.body[0]
    assert reply.signature == "s"

    bus1.disconnect()
    bus2.disconnect()


@pytest.mark.asyncio
async def test_object_manager():
    expected_reply = {
        "/test/path/deeper": {
            "test.interface2": {
                "Bar": Variant("s", "str"),
                "Foo": Variant("y", 42),
                "AsyncProp": Variant("s", "async"),
            }
        }
    }
    reply_ext = {
        "/test/path": {
            "test.interface1": {},
            "test.interface2": {
                "Bar": Variant("s", "str"),
                "Foo": Variant("y", 42),
                "AsyncProp": Variant("s", "async"),
            },
        }
    }

    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    interface = ExampleInterface("test.interface1")
    interface2 = ExampleComplexInterface("test.interface2")

    export_path = "/test/path"
    bus1.export(export_path, interface)
    bus1.export(export_path, interface2)
    bus1.export(export_path + "/deeper", interface2)

    reply_root = await bus2.call(
        Message(
            destination=bus1.unique_name,
            path="/",
            interface="org.freedesktop.DBus.ObjectManager",
            member="GetManagedObjects",
        )
    )

    reply_level1 = await bus2.call(
        Message(
            destination=bus1.unique_name,
            path=export_path,
            interface="org.freedesktop.DBus.ObjectManager",
            member="GetManagedObjects",
        )
    )

    reply_level2 = await bus2.call(
        Message(
            destination=bus1.unique_name,
            path=export_path + "/deeper",
            interface="org.freedesktop.DBus.ObjectManager",
            member="GetManagedObjects",
        )
    )

    assert reply_root.signature == "a{oa{sa{sv}}}"
    assert reply_level1.signature == "a{oa{sa{sv}}}"
    assert reply_level2.signature == "a{oa{sa{sv}}}"

    assert reply_level2.body == [{}]
    assert reply_level1.body == [expected_reply]
    expected_reply.update(reply_ext)
    assert reply_root.body == [expected_reply]

    bus1.disconnect()
    bus2.disconnect()


@pytest.mark.asyncio
async def test_standard_interface_properties():
    # standard interfaces have no properties, but should still behave correctly
    # when you try to call the methods anyway (#49)
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()
    interface = ExampleInterface("test.interface1")
    export_path = "/test/path"
    bus1.export(export_path, interface)

    for iface in [
        "org.freedesktop.DBus.Properties",
        "org.freedesktop.DBus.Introspectable",
        "org.freedesktop.DBus.Peer",
        "org.freedesktop.DBus.ObjectManager",
    ]:
        result = await bus2.call(
            Message(
                destination=bus1.unique_name,
                path=export_path,
                interface="org.freedesktop.DBus.Properties",
                member="Get",
                signature="ss",
                body=[iface, "anything"],
            )
        )
        assert result.message_type is MessageType.ERROR
        assert result.error_name == ErrorType.UNKNOWN_PROPERTY.value

        result = await bus2.call(
            Message(
                destination=bus1.unique_name,
                path=export_path,
                interface="org.freedesktop.DBus.Properties",
                member="Set",
                signature="ssv",
                body=[iface, "anything", Variant("s", "new thing")],
            )
        )
        assert result.message_type is MessageType.ERROR
        assert result.error_name == ErrorType.UNKNOWN_PROPERTY.value

        result = await bus2.call(
            Message(
                destination=bus1.unique_name,
                path=export_path,
                interface="org.freedesktop.DBus.Properties",
                member="GetAll",
                signature="s",
                body=[iface],
            )
        )
        assert result.message_type is MessageType.METHOD_RETURN
        assert result.body == [{}]

    bus1.disconnect()
    bus2.disconnect()
