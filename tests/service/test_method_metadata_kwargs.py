"""The ``message`` keyword-only parameter on ``@dbus_method`` handlers (#486)."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio

from dbus_fast import Message, MessageFlag, MessageType
from dbus_fast.aio import MessageBus
from dbus_fast.annotations import DBusStr
from dbus_fast.service import ServiceInterface, dbus_method


class MetadataInterface(ServiceInterface):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.last_message: Message | None = None

    @dbus_method()
    def echo_sender(self, what: DBusStr, *, message: Message) -> DBusStr:
        self.last_message = message
        return message.sender or ""

    @dbus_method()
    def no_metadata(self, what: DBusStr) -> DBusStr:
        return what


@pytest_asyncio.fixture(name="two_buses")
async def two_buses_fixture() -> AsyncIterator[tuple[MessageBus, MessageBus]]:
    """A connected pair of buses, torn down after the test."""
    server = await MessageBus().connect()
    client = await MessageBus().connect()
    try:
        yield server, client
    finally:
        server.disconnect()
        client.disconnect()
        await asyncio.wait_for(server.wait_for_disconnect(), timeout=1)
        await asyncio.wait_for(client.wait_for_disconnect(), timeout=1)


def test_unknown_keyword_only_param_rejected() -> None:
    with pytest.raises(ValueError, match="unknown keyword-only parameter 'sender'"):

        @dbus_method()
        def boom(self, what: DBusStr, *, sender: str) -> DBusStr:
            return what


def test_message_kwarg_excluded_from_introspection() -> None:
    iface = MetadataInterface("test.metadata")
    method = next(m for m in iface.introspect().methods if m.name == "echo_sender")
    assert method.in_signature == "s"
    assert [arg.name for arg in method.in_args] == ["what"]


@pytest.mark.asyncio
async def test_message_kwarg_receives_caller_metadata(
    two_buses: tuple[MessageBus, MessageBus],
) -> None:
    server, client = two_buses
    iface = MetadataInterface("test.metadata")
    server.export("/test/path", iface)

    reply = await client.call(
        Message(
            destination=server.unique_name,
            path="/test/path",
            interface="test.metadata",
            member="echo_sender",
            signature="s",
            body=["hi"],
            flags=MessageFlag.NO_AUTOSTART,
        )
    )

    assert reply.message_type == MessageType.METHOD_RETURN, reply.body[0]
    assert reply.body == [client.unique_name]

    msg = iface.last_message
    assert isinstance(msg, Message)
    assert msg.sender == client.unique_name
    assert msg.destination == server.unique_name
    assert msg.path == "/test/path"
    assert msg.interface == "test.metadata"
    assert msg.member == "echo_sender"
    assert msg.flags is MessageFlag.NO_AUTOSTART
    assert msg.unix_fds == []


@pytest.mark.asyncio
async def test_method_without_metadata_still_works(
    two_buses: tuple[MessageBus, MessageBus],
) -> None:
    server, client = two_buses
    iface = MetadataInterface("test.metadata")
    server.export("/test/path", iface)

    reply = await client.call(
        Message(
            destination=server.unique_name,
            path="/test/path",
            interface="test.metadata",
            member="no_metadata",
            signature="s",
            body=["plain"],
        )
    )

    assert reply.message_type == MessageType.METHOD_RETURN, reply.body[0]
    assert reply.body == ["plain"]
