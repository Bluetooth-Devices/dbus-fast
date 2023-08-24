from unittest.mock import Mock

import pytest

from dbus_fast.constants import ErrorType, MessageType
from dbus_fast.errors import DBusError
from dbus_fast.message import Message
from dbus_fast.message_bus import SendReply


def test_send_reply_exception():
    """Test that SendReply sends an error message when DBusError is raised."""

    mock_message_bus = Mock()
    mock_message = Mock()
    send_reply = SendReply(mock_message_bus, mock_message)

    with send_reply as reply:
        raise DBusError(ErrorType.DISCONNECTED, "Disconnected", None)

    assert mock_message_bus.send_message.call_count == 1
    assert (
        mock_message_bus.send_message.call_args[0][0].message_type == MessageType.ERROR
    )
