import asyncio
from unittest.mock import patch

import pytest

from dbus_fast import Message
from dbus_fast.aio import MessageBus
from dbus_fast.aio.message_bus import ConnectionClosed


@pytest.mark.asyncio
async def test_bus_disconnect_before_reply(event_loop):
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

        event_loop.call_soon(bus.disconnect)

        with pytest.raises((EOFError, BrokenPipeError)):
            await ping

    assert bus._disconnected
    assert not bus.connected
    assert (await bus.wait_for_disconnect()) is None
    # Let the exception propagate to the event loop
    # so the next test does not fail
    await asyncio.sleep(0)
    await asyncio.sleep(0)


@pytest.mark.asyncio
async def test_unexpected_disconnect(event_loop):
    bus = MessageBus()

    class FakeSocket:
        def send(self, *args, **kwargs):
            raise OSError

    assert not bus.connected
    await bus.connect()
    assert bus.connected

    with patch.object(bus._writer, "_write_without_remove_writer"), patch.object(
        bus._writer, "sock", FakeSocket()
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
        await bus.wait_for_disconnect()

    bus.disconnect()
    with pytest.raises(OSError):
        await bus.wait_for_disconnect()
