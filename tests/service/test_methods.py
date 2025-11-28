import asyncio

import pytest

from dbus_fast import (
    DBusError,
    ErrorType,
    Message,
    MessageFlag,
    MessageType,
    SignatureTree,
    Variant,
)
from dbus_fast.aio import MessageBus
from dbus_fast.service import ServiceInterface, dbus_method


class ExampleInterface(ServiceInterface):
    def __init__(self, name):
        super().__init__(name)

    @dbus_method()
    def echo(self, what: "s") -> "s":
        assert type(self) is ExampleInterface
        return what

    @dbus_method()
    def echo_multiple(self, what1: "s", what2: "s") -> "ss":
        assert type(self) is ExampleInterface
        return [what1, what2]

    @dbus_method()
    def echo_containers(
        self,
        array: "as",  # noqa: F722
        variant: "v",
        dict_entries: "a{sv}",  # noqa: F722
        struct: "(s(s(v)))",
    ) -> "asva{sv}(s(s(v)))":  # noqa: F722
        assert type(self) is ExampleInterface
        return [array, variant, dict_entries, struct]

    @dbus_method()
    def ping(self):
        assert type(self) is ExampleInterface

    @dbus_method(name="renamed")
    def original_name(self):
        assert type(self) is ExampleInterface

    @dbus_method(disabled=True)
    def not_here(self):
        assert type(self) is ExampleInterface

    @dbus_method()
    def throws_unexpected_error(self):
        assert type(self) is ExampleInterface
        raise Exception("oops")

    @dbus_method()
    def throws_dbus_error(self):
        assert type(self) is ExampleInterface
        raise DBusError("test.error", "an error occurred")


class AsyncInterface(ServiceInterface):
    def __init__(self, name):
        super().__init__(name)

    @dbus_method()
    async def echo(self, what: "s") -> "s":
        assert type(self) is AsyncInterface
        return what

    @dbus_method()
    async def echo_multiple(self, what1: "s", what2: "s") -> "ss":
        assert type(self) is AsyncInterface
        return [what1, what2]

    @dbus_method()
    async def echo_containers(
        self,
        array: "as",  # noqa: F722
        variant: "v",
        dict_entries: "a{sv}",  # noqa: F722
        struct: "(s(s(v)))",
    ) -> "asva{sv}(s(s(v)))":  # noqa: F722
        assert type(self) is AsyncInterface
        return [array, variant, dict_entries, struct]

    @dbus_method()
    async def ping(self):
        assert type(self) is AsyncInterface

    @dbus_method(name="renamed")
    async def original_name(self):
        assert type(self) is AsyncInterface

    @dbus_method(disabled=True)
    async def not_here(self):
        assert type(self) is AsyncInterface

    @dbus_method()
    async def throws_unexpected_error(self):
        assert type(self) is AsyncInterface
        raise Exception("oops")

    @dbus_method()
    def throws_dbus_error(self):
        assert type(self) is AsyncInterface
        raise DBusError("test.error", "an error occurred")


@pytest.mark.parametrize("interface_class", [ExampleInterface, AsyncInterface])
@pytest.mark.asyncio
async def test_methods(interface_class):
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    interface = interface_class("test.interface")
    export_path = "/test/path"

    async def call(
        member, signature="", body=[], flags=MessageFlag.NONE, interface=interface.name
    ):
        msg = Message(
            destination=bus1.unique_name,
            path=export_path,
            interface=interface,
            member=member,
            signature=signature,
            body=body,
            flags=flags,
        )

        if flags & MessageFlag.NO_REPLY_EXPECTED:
            await bus2.send(msg)
            return None

        return await bus2.call(msg)

    bus1.export(export_path, interface)

    body = ["hello world"]
    reply = await call("echo", "s", body)

    assert reply.message_type == MessageType.METHOD_RETURN, reply.body[0]
    assert reply.signature == "s"
    assert reply.body == body

    body = ["hello", "world"]
    reply = await call("echo_multiple", "ss", body)
    assert reply.message_type == MessageType.METHOD_RETURN, reply.body[0]
    assert reply.signature == "ss"
    assert reply.body == body

    body = [
        ["hello", "world"],
        Variant("v", Variant("(ss)", ("hello", "world"))),
        {"foo": Variant("t", 100)},
        ("one", ("two", (Variant("s", "three"),))),
    ]
    signature = "asva{sv}(s(s(v)))"
    SignatureTree(signature).verify(body)
    reply = await call("echo_containers", signature, body)
    assert reply.message_type == MessageType.METHOD_RETURN, reply.body[0]
    assert reply.signature == signature
    assert reply.body == body

    # Wrong interface should be a failure
    reply = await call(
        "echo_containers", signature, body, interface="org.abc.xyz.Props"
    )
    assert reply.message_type == MessageType.ERROR, reply.body[0]
    assert reply.error_name == "org.freedesktop.DBus.Error.UnknownMethod", reply.body[0]
    assert reply.body == [
        'org.abc.xyz.Props.echo_containers with signature "asva{sv}(s(s(v)))" could not be found'
    ]

    # No interface should result in finding anything that matches the member name
    # and the signature
    reply = await call("echo_containers", signature, body, interface=None)
    assert reply.message_type == MessageType.METHOD_RETURN, reply.body[0]
    assert reply.signature == signature
    assert reply.body == body

    # No interface should result in finding anything that matches the member name
    # and the signature, but in this case it will be nothing because
    # the signature is wrong
    reply = await call("echo_containers", "as", body, interface=None)
    assert reply.message_type == MessageType.ERROR, reply.body[0]
    assert reply.error_name == "org.freedesktop.DBus.Error.UnknownMethod", reply.body[0]
    assert reply.body == ['None.echo_containers with signature "as" could not be found']

    reply = await call("ping")
    assert reply.message_type == MessageType.METHOD_RETURN, reply.body[0]
    assert reply.signature == ""
    assert reply.body == []

    reply = await call("throws_unexpected_error")
    assert reply.message_type == MessageType.ERROR, reply.body[0]
    assert reply.error_name == ErrorType.SERVICE_ERROR.value, reply.body[0]

    reply = await call("throws_dbus_error")
    assert reply.message_type == MessageType.ERROR, reply.body[0]
    assert reply.error_name == "test.error", reply.body[0]
    assert reply.body == ["an error occurred"]

    reply = await call("ping", flags=MessageFlag.NO_REPLY_EXPECTED)
    assert reply is None

    reply = await call("throws_unexpected_error", flags=MessageFlag.NO_REPLY_EXPECTED)
    assert reply is None

    reply = await call("throws_dbus_error", flags=MessageFlag.NO_REPLY_EXPECTED)
    assert reply is None

    reply = await call("does_not_exist")
    assert reply.message_type == MessageType.ERROR, reply.body[0]
    assert reply.error_name == "org.freedesktop.DBus.Error.UnknownMethod", reply.body[0]
    assert reply.body == [
        'test.interface.does_not_exist with signature "" could not be found'
    ]

    bus1.disconnect()
    bus2.disconnect()
    await asyncio.wait_for(bus1.wait_for_disconnect(), timeout=1)
    await asyncio.wait_for(bus2.wait_for_disconnect(), timeout=1)
