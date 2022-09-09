import functools
import os

import pytest

from dbus_fast import Message
from dbus_fast.aio import MessageBus


@pytest.mark.asyncio
async def test_bus_disconnect_before_reply(event_loop):
    """In this test, the bus disconnects before the reply comes in. Make sure
    the caller receives a reply with the error instead of hanging."""
    bus = MessageBus()
    assert not bus.connected
    await bus.connect()
    assert bus.connected

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


@pytest.mark.asyncio
async def test_unexpected_disconnect(event_loop):
    bus = MessageBus()
    assert not bus.connected
    await bus.connect()
    assert bus.connected

    ping = bus.call(
        Message(
            destination="org.freedesktop.DBus",
            path="/org/freedesktop/DBus",
            interface="org.freedesktop.DBus",
            member="Ping",
        )
    )

    event_loop.call_soon(functools.partial(os.close, bus._fd))

    with pytest.raises(OSError):
        await ping

    assert bus._disconnected
    assert not bus.connected

    with pytest.raises(OSError):
        await bus.wait_for_disconnect()
