import os

import pytest

from dbus_fast.constants import ErrorType, MessageType
from dbus_fast.errors import DBusError
from dbus_fast.message import Message
from dbus_fast.message_bus import BaseMessageBus
from dbus_fast.send_reply import SendReply


@pytest.fixture(autouse=True)
def mock_address() -> None:
    original_address = os.environ.get("DBUS_SESSION_BUS_ADDRESS")
    os.environ["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=/dev/null"
    yield
    if original_address is None:
        del os.environ["DBUS_SESSION_BUS_ADDRESS"]
    else:
        os.environ["DBUS_SESSION_BUS_ADDRESS"] = original_address


def test_send_reply_exception() -> None:
    """Test that SendReply sends an error message when DBusError is raised."""

    messages = []

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

    with send_reply:
        raise DBusError(ErrorType.DISCONNECTED, "Disconnected", None)

    assert len(messages) == 1
    assert messages[0].message_type == MessageType.ERROR
    assert messages[0].error_name == "org.freedesktop.DBus.Error.Disconnected"
    assert messages[0].reply_serial == 1


def test_send_reply_happy_path() -> None:
    """Test that SendReply sends a message."""

    messages = []

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
        reply(mock_message)

    assert len(messages) == 1
    assert messages[0].message_type == MessageType.METHOD_CALL
    assert messages[0].error_name is None
