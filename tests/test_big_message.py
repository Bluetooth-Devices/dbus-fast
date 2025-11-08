import sys

import pytest

from dbus_fast import Message, MessageType, aio, glib
from dbus_fast.service import ServiceInterface, dbus_method
from tests.util import check_gi_repository, skip_reason_no_gi

has_gi = check_gi_repository()


class ExampleInterface(ServiceInterface):
    def __init__(self):
        super().__init__("example.interface")

    @dbus_method()
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


@pytest.mark.skipif(not has_gi, reason=skip_reason_no_gi)
@pytest.mark.skipif(
    sys.version_info[:3][1] in (10, 11, 12, 13),
    reason="segfaults on py3.10,py3.11,py3.12,py3.13",
)
def test_glib_big_message():
    "this tests that nonblocking reads and writes actually work for glib"
    bus1 = glib.MessageBus().connect_sync()
    bus2 = glib.MessageBus().connect_sync()
    interface = ExampleInterface()
    bus1.export("/test/path", interface)

    # two megabytes
    big_body = [bytes(1000000) * 2]
    result = bus2.call_sync(
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
