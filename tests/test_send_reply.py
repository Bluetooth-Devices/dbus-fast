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


class InlineSendReply:
    """A context manager to send a reply to a message."""

    __slots__ = ("_bus", "_msg")

    def __init__(self, bus: "BaseMessageBus", msg: Message) -> None:
        """Create a new reply context manager."""
        self._bus = bus
        self._msg = msg

    def __enter__(self):
        return self

    def __call__(self, reply: Message) -> None:
        self._bus.send(reply)

    def _exit(
        self,
        exc_type: Optional[Type[Exception]],
        exc_value: Optional[Exception],
        tb: Optional[TracebackType],
    ) -> bool:
        if exc_value:
            if isinstance(exc_value, DBusError):
                self(exc_value._as_message(self._msg))
            else:
                self(
                    Message.new_error(
                        self._msg,
                        ErrorType.SERVICE_ERROR,
                        f"The service interface raised an error: {exc_value}.\n{traceback.format_tb(tb)}",
                    )
                )
            return True

        return False

    def __exit__(
        self,
        exc_type: Optional[Type[Exception]],
        exc_value: Optional[Exception],
        tb: Optional[TracebackType],
    ) -> bool:
        return self._exit(exc_type, exc_value, tb)

    def send_error(self, exc: Exception) -> None:
        self._exit(exc.__class__, exc, exc.__traceback__)


@pytest.mark.parametrize("send_reply_class", (SendReply, InlineSendReply))
def test_send_reply_exception(send_reply_class: Union[SendReply, InlineSendReply]):
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
    send_reply = send_reply_class(mock_message_bus, mock_message)

    with send_reply as reply:
        raise DBusError(ErrorType.DISCONNECTED, "Disconnected", None)

    assert len(messages) == 1
    assert messages[0].message_type == MessageType.ERROR
    assert messages[0].error_name == "org.freedesktop.DBus.Error.Disconnected"
    assert messages[0].reply_serial == 1
