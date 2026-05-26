import asyncio
import logging
from unittest.mock import patch

import pytest

from dbus_fast import Message
from dbus_fast.aio import MessageBus


@pytest.mark.asyncio
async def test_bus_disconnect_before_reply():
    """In this test, the bus disconnects before the reply comes in. Make sure
    the caller receives a reply with the error instead of hanging."""
    bus = MessageBus()
    assert not bus.connected
    await bus.connect()
    assert bus.connected

    with patch.object(bus._writer, "_write_without_remove_writer"):
        ping = bus.call(
            Message(
                destination="org.freedesktop.DBus",
                path="/org/freedesktop/DBus",
                interface="org.freedesktop.DBus",
                member="Ping",
            )
        )

        asyncio.get_running_loop().call_soon(bus.disconnect)

        with pytest.raises((EOFError, BrokenPipeError)):
            await ping

    assert bus._disconnected
    assert not bus.connected

    await asyncio.wait_for(bus.wait_for_disconnect(), timeout=1)


@pytest.mark.asyncio
async def test_unexpected_disconnect():
    bus = MessageBus()

    class FakeSocket:
        def send(self, *args, **kwargs):
            raise OSError

    assert not bus.connected
    await bus.connect()
    assert bus.connected

    with (
        patch.object(bus._writer, "_write_without_remove_writer"),
        patch.object(bus._writer, "sock", FakeSocket()),
    ):
        ping = bus.call(
            Message(
                destination="org.freedesktop.DBus",
                path="/org/freedesktop/DBus",
                interface="org.freedesktop.DBus",
                member="Ping",
            )
        )

        with pytest.raises(OSError):
            await ping

        assert bus._disconnected
        assert not bus.connected

    with pytest.raises(OSError):
        await asyncio.wait_for(bus.wait_for_disconnect(), timeout=1)

    bus.disconnect()
    with pytest.raises(OSError):
        await asyncio.wait_for(bus.wait_for_disconnect(), timeout=1)


@pytest.mark.asyncio
async def test_disconnect_after_finalize_does_not_warn(caplog):
    """disconnect() on an already finalized bus does not warn about the socket."""
    bus = MessageBus()
    await bus.connect()
    assert bus.connected

    bus._finalize(EOFError())
    assert bus._disconnected

    with caplog.at_level(logging.WARNING, logger="dbus_fast.message_bus"):
        bus.disconnect()

    assert bus._user_disconnect
    assert not any(
        "could not shut down socket" in record.message for record in caplog.records
    )
