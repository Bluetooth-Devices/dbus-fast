import asyncio

import pytest

from dbus_fast.aio import MessageBus
from dbus_fast.annotations import DBusStr
from dbus_fast.service import ServiceInterface, dbus_method


@pytest.mark.asyncio
async def test_multiple_flags_in_message():
    class ExampleInterface(ServiceInterface):
        def __init__(self, name: str) -> None:
            super().__init__(name)

        @dbus_method()
        def Echo(self, what: DBusStr) -> DBusStr:
            return what

    bus = await MessageBus().connect()
    interface = ExampleInterface("test.interface")
    bus.export("/test/path", interface)
    await bus.request_name("test.name")
    bus.disconnect()
    await asyncio.wait_for(bus.wait_for_disconnect(), timeout=1)
