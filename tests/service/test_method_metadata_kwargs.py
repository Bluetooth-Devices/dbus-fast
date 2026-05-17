"""Keyword-only metadata kwargs on ``@dbus_method`` handlers (#486)."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from dbus_fast import Message, MessageFlag, MessageType
from dbus_fast.aio import MessageBus
from dbus_fast.annotations import DBusStr
from dbus_fast.service import (
    METHOD_METADATA_KWARGS,
    ServiceInterface,
    dbus_method,
)


class MetadataInterface(ServiceInterface):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.last_seen: dict[str, Any] = {}

    @dbus_method()
    def echo_sender(self, what: DBusStr, *, sender: str) -> DBusStr:
        self.last_seen["sender"] = sender
        return sender or ""

    @dbus_method()
    def collect_all(
        self,
        what: DBusStr,
        *,
        sender: str,
        destination: str,
        path: str,
        interface: str,
        flags: int,
        unix_fds: list,
        message: Message,
    ) -> DBusStr:
        self.last_seen["sender"] = sender
        self.last_seen["destination"] = destination
        self.last_seen["path"] = path
        self.last_seen["interface"] = interface
        self.last_seen["flags"] = flags
        self.last_seen["unix_fds"] = unix_fds
        self.last_seen["message"] = message
        return what

    @dbus_method()
    def no_metadata(self, what: DBusStr) -> DBusStr:
        return what


def test_unknown_keyword_only_param_rejected() -> None:
    class Bad(ServiceInterface):
        def __init__(self) -> None:
            super().__init__("test.bad")

    with pytest.raises(ValueError, match="unknown keyword-only parameter 'mystery'"):

        @dbus_method()
        def boom(self, what: DBusStr, *, mystery: str) -> DBusStr:
            return what


def test_metadata_kwargs_excluded_from_dbus_signature() -> None:
    iface = MetadataInterface("test.metadata")
    method = next(
        m.__dict__["__DBUS_METHOD"]
        for name, m in vars(type(iface)).items()
        if name == "echo_sender"
    )
    assert method.in_signature == "s"
    assert [a.name for a in method.introspection.in_args] == ["what"]
    assert method.kw_metadata == ("sender",)


def test_method_with_no_metadata_unchanged() -> None:
    iface = MetadataInterface("test.metadata")
    method = next(
        m.__dict__["__DBUS_METHOD"]
        for name, m in vars(type(iface)).items()
        if name == "no_metadata"
    )
    assert method.kw_metadata == ()


def test_all_known_metadata_names_recognized() -> None:
    expected = frozenset(
        {
            "sender",
            "destination",
            "path",
            "interface",
            "flags",
            "unix_fds",
            "message",
        }
    )
    assert expected == METHOD_METADATA_KWARGS


@pytest.mark.asyncio
async def test_sender_kwarg_receives_caller_unique_name() -> None:
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()
    try:
        iface = MetadataInterface("test.metadata")
        bus1.export("/test/path", iface)

        reply = await bus2.call(
            Message(
                destination=bus1.unique_name,
                path="/test/path",
                interface="test.metadata",
                member="echo_sender",
                signature="s",
                body=["hi"],
            )
        )
        assert reply.message_type == MessageType.METHOD_RETURN, reply.body[0]
        assert reply.body == [bus2.unique_name]
        assert iface.last_seen["sender"] == bus2.unique_name
    finally:
        bus1.disconnect()
        bus2.disconnect()
        await asyncio.wait_for(bus1.wait_for_disconnect(), timeout=1)
        await asyncio.wait_for(bus2.wait_for_disconnect(), timeout=1)


@pytest.mark.asyncio
async def test_full_metadata_set_injected() -> None:
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()
    try:
        iface = MetadataInterface("test.metadata")
        bus1.export("/test/path", iface)

        reply = await bus2.call(
            Message(
                destination=bus1.unique_name,
                path="/test/path",
                interface="test.metadata",
                member="collect_all",
                signature="s",
                body=["payload"],
                flags=MessageFlag.NONE,
            )
        )
        assert reply.message_type == MessageType.METHOD_RETURN, reply.body[0]
        seen = iface.last_seen
        assert seen["sender"] == bus2.unique_name
        assert seen["destination"] == bus1.unique_name
        assert seen["path"] == "/test/path"
        assert seen["interface"] == "test.metadata"
        assert isinstance(seen["flags"], MessageFlag)
        assert seen["unix_fds"] == []
        assert isinstance(seen["message"], Message)
        assert seen["message"].member == "collect_all"
    finally:
        bus1.disconnect()
        bus2.disconnect()
        await asyncio.wait_for(bus1.wait_for_disconnect(), timeout=1)
        await asyncio.wait_for(bus2.wait_for_disconnect(), timeout=1)


@pytest.mark.asyncio
async def test_method_without_metadata_still_works() -> None:
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()
    try:
        iface = MetadataInterface("test.metadata")
        bus1.export("/test/path", iface)

        reply = await bus2.call(
            Message(
                destination=bus1.unique_name,
                path="/test/path",
                interface="test.metadata",
                member="no_metadata",
                signature="s",
                body=["plain"],
            )
        )
        assert reply.message_type == MessageType.METHOD_RETURN, reply.body[0]
        assert reply.body == ["plain"]
    finally:
        bus1.disconnect()
        bus2.disconnect()
        await asyncio.wait_for(bus1.wait_for_disconnect(), timeout=1)
        await asyncio.wait_for(bus2.wait_for_disconnect(), timeout=1)
