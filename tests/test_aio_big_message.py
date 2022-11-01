import pytest

from dbus_fast import Message, MessageType, aio
from dbus_fast.service import ServiceInterface, method


class ExampleInterface(ServiceInterface):
    def __init__(self):
        super().__init__("example.interface")

    @method()
    def echo_bytes(self, what: "ay") -> "ay":
        return what


@pytest.mark.asyncio
async def test_aio_big_message():
    "this tests that nonblocking reads and writes actually work for aio"
    bus1 = await aio.MessageBus().connect()
    bus2 = await aio.MessageBus().connect()
    interface = ExampleInterface()
    bus1.export("/test/path", interface)

    # two megabytes
    big_body = [bytes(1000000) * 2]
    result = await bus2.call(
        Message(
            destination=bus1.unique_name,
            path="/test/path",
            interface=interface.name,
            member="echo_bytes",
            signature="ay",
            body=big_body,
        )
    )
    assert result.message_type == MessageType.METHOD_RETURN, result.body[0]
    assert result.body[0] == big_body[0]

    bus1.disconnect()
    bus2.disconnect()
