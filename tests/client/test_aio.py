import asyncio
import pytest

from dbus_fast import aio
from dbus_fast.service import ServiceInterface


class ExampleInterface(ServiceInterface):
    def __init__(self):
        super().__init__("test.interface")


@pytest.mark.asyncio
async def test_fast_disconnect():
    bus_name = "aio.client.test.methods"

    bus = await aio.MessageBus().connect()
    bus2 = await aio.MessageBus().connect()
    await bus.request_name(bus_name)
    service_interface = ExampleInterface()
    bus.export("/test/path", service_interface)
    introspection = await bus2.introspect(bus_name, "/test/path")
    bus2.get_proxy_object(bus_name, "/test/path", introspection)
    bus2.disconnect()
    bus.disconnect()
    await asyncio.wait_for(bus.wait_for_disconnect(), timeout=1)
    await asyncio.wait_for(bus2.wait_for_disconnect(), timeout=1)
