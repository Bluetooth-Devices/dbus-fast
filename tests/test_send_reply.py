import os
import traceback
from types import TracebackType
from typing import Any, Callable, Dict, List, Optional, Type, Union
from unittest.mock import Mock

import pytest

from dbus_fast.constants import ErrorType, MessageType
from dbus_fast.errors import DBusError
from dbus_fast.message import Message
from dbus_fast.message_bus import BaseMessageBus, SendReply


def test_send_reply_exception() -> None:
    """Test that SendReply sends an error message when DBusError is raised."""

    messages = []
    os.environ["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=/dev/null"

    class MockBus(BaseMessageBus):
        def send(self, msg: Message) -> None:
            messages.append(msg)

        def send_message(self, msg: Message) -> None:
            messages.append(msg)

        def _setup_socket(self) -> None:
            pass

    mock_message_bus = MockBus()
    mock_message = Message(
        path="/test/path", interface="test.interface", member="test_member", serial=1
    )
    send_reply = SendReply(mock_message_bus, mock_message)

    with send_reply as reply:
        raise DBusError(ErrorType.DISCONNECTED, "Disconnected", None)

    assert len(messages) == 1
    assert messages[0].message_type == MessageType.ERROR
    assert messages[0].error_name == "org.freedesktop.DBus.Error.Disconnected"
    assert messages[0].reply_serial == 1
