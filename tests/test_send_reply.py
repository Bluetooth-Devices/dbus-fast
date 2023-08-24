import os
from unittest.mock import Mock

import pytest

from dbus_fast.constants import ErrorType, MessageType
from dbus_fast.errors import DBusError
from dbus_fast.message import Message
from dbus_fast.message_bus import BaseMessageBus, SendReply


def test_send_reply_exception():
    """Test that SendReply sends an error message when DBusError is raised."""

    messages = []
    os.environ["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=/dev/null"

    class MockBus(BaseMessageBus):
        def send(self, msg: Message) -> None:
            messages.append(msg)

        def _setup_socket(self) -> None:
            pass

    mock_message_bus = MockBus()
    mock_message = Message(
        path="/test/path", interface="test.interface", member="test_member"
    )
    send_reply = SendReply(mock_message_bus, mock_message)

    with send_reply as reply:
        raise DBusError(ErrorType.DISCONNECTED, "Disconnected", None)

    assert mock_message_bus.send_message.call_count == 1
    assert (
        mock_message_bus.send_message.call_args[0][0].message_type == MessageType.ERROR
    )
