import os
from collections.abc import Generator

import pytest

from dbus_fast.constants import ErrorType, MessageType
from dbus_fast.errors import DBusError
from dbus_fast.message import Message
from dbus_fast.message_bus import BaseMessageBus
from dbus_fast.send_reply import SendReply


@pytest.fixture(autouse=True)
def mock_address() -> Generator[None, None, None]:
    original_address = os.environ.get("DBUS_SESSION_BUS_ADDRESS")
    os.environ["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=/dev/null"
    yield
    if original_address is None:
        del os.environ["DBUS_SESSION_BUS_ADDRESS"]
    else:
        os.environ["DBUS_SESSION_BUS_ADDRESS"] = original_address


@pytest.fixture
def send_reply_setup() -> Generator[
    tuple[BaseMessageBus, Message, list[Message]], None, None
]:
    messages: list[Message] = []

    class MockClosable:
        def close(self) -> None:
            pass

    class MockBus(BaseMessageBus):
        def __init__(self) -> None:
            super().__init__()
            self._sock = MockClosable()  # type: ignore
            self._stream = MockClosable()  # type: ignore

        def send(self, msg: Message) -> None:
            messages.append(msg)

        def send_message(self, msg: Message) -> None:
            messages.append(msg)

    bus = MockBus()
    msg = Message(
        path="/test/path", interface="test.interface", member="test_member", serial=1
    )
    try:
        yield bus, msg, messages
    finally:
        bus.disconnect()
        bus._finalize(None)


def test_send_reply_exception(
    send_reply_setup: tuple[BaseMessageBus, Message, list[Message]],
) -> None:
    """Test that SendReply sends an error message when DBusError is raised."""
    bus, msg, messages = send_reply_setup
    send_reply = SendReply(bus, msg)

    with send_reply:
        raise DBusError(ErrorType.DISCONNECTED, "Disconnected", None)

    assert len(messages) == 1
    assert messages[0].message_type == MessageType.ERROR
    assert messages[0].error_name == "org.freedesktop.DBus.Error.Disconnected"
    assert messages[0].reply_serial == 1


def test_send_reply_generic_exception(
    send_reply_setup: tuple[BaseMessageBus, Message, list[Message]],
) -> None:
    """Non-DBusError exceptions become SERVICE_ERROR replies."""
    bus, msg, messages = send_reply_setup
    send_reply = SendReply(bus, msg)

    with send_reply:
        raise RuntimeError("boom")

    assert len(messages) == 1
    assert messages[0].message_type == MessageType.ERROR
    assert messages[0].error_name == ErrorType.SERVICE_ERROR.value
    assert messages[0].reply_serial == 1
    # The wire body must disclose only the exception class name — never the
    # str() of the exception (might contain caller data) and never a Python
    # traceback (paths, line numbers, locals).
    body = messages[0].body[0]
    assert "boom" not in body, body
    assert "Traceback" not in body, body
    assert 'File "' not in body, body
    assert "RuntimeError" in body, body


def test_send_reply_send_error(
    send_reply_setup: tuple[BaseMessageBus, Message, list[Message]],
) -> None:
    """send_error() routes an exception through the same error reply path."""
    bus, msg, messages = send_reply_setup
    send_reply = SendReply(bus, msg)

    send_reply.send_error(DBusError(ErrorType.FAILED, "explicit failure", None))

    assert len(messages) == 1
    assert messages[0].message_type == MessageType.ERROR
    assert messages[0].error_name == "org.freedesktop.DBus.Error.Failed"
    assert messages[0].reply_serial == 1


def test_send_reply_no_exception_returns_false(
    send_reply_setup: tuple[BaseMessageBus, Message, list[Message]],
) -> None:
    """Exiting with no exception must not suppress and must not send a reply."""
    bus, msg, messages = send_reply_setup
    send_reply = SendReply(bus, msg)

    assert send_reply._exit(None, None, None) is False
    assert messages == []


def test_send_reply_happy_path(
    send_reply_setup: tuple[BaseMessageBus, Message, list[Message]],
) -> None:
    """Test that SendReply sends a message."""
    bus, msg, messages = send_reply_setup
    send_reply = SendReply(bus, msg)

    with send_reply as reply:
        reply(msg)

    assert len(messages) == 1
    assert messages[0].message_type == MessageType.METHOD_CALL
    assert messages[0].error_name is None
