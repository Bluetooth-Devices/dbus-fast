import asyncio

import pytest

from dbus_fast import Message, MessageFlag, MessageType
from dbus_fast.aio import MessageBus
from dbus_fast.service import ServiceInterface, method


@pytest.mark.xfail
@pytest.mark.asyncio
async def test_multiple_flags_in_message():
    class ExampleInterface(ServiceInterface):
        def __init__(self, name):
            super().__init__(name)

        @method()
        def Echo(self, what: "s") -> "s":  # noqa: F821
            return what

    bus = await MessageBus().connect()
    interface = ExampleInterface("test.interface")
    bus.export("/test/path", interface)
    await bus.request_name("test.name")
    await bus.wait_for_disconnect()
