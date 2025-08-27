import socket
from unittest.mock import MagicMock

import pytest

from dbus_fast.aio import MessageBus


@pytest.mark.asyncio
async def test_tcp_socket_cleanup_on_connect_fail(monkeypatch):
    """Test that socket resources are cleaned up on a failed TCP connection."""
    mock_sock = MagicMock()
    mock_stream = MagicMock()
    mock_sock.makefile.return_value = mock_stream
    mock_sock.connect.side_effect = ConnectionRefusedError
    monkeypatch.setattr(socket, "socket", lambda *_: mock_sock)

    bus_address = "tcp:host=127.0.0.1,port=1"

    with pytest.raises(ConnectionRefusedError):
        _ = MessageBus(bus_address=bus_address)

    mock_sock.connect.assert_called_once()
    mock_stream.close.assert_called_once()
    mock_sock.close.assert_called_once()


@pytest.mark.asyncio
async def test_unix_socket_cleanup_on_connect_fail(monkeypatch):
    """Test that socket resources are cleaned up on a failed Unix socket connection."""
    mock_sock = MagicMock()
    mock_stream = MagicMock()
    mock_sock.makefile.return_value = mock_stream
    mock_sock.connect.side_effect = FileNotFoundError
    monkeypatch.setattr(socket, "socket", lambda *_: mock_sock)

    path = "/tmp/non-existent-socket-for-dbus-fast"
    bus_address = f"unix:path={path}"

    with pytest.raises(FileNotFoundError):
        _ = MessageBus(bus_address=bus_address)

    mock_sock.connect.assert_called_once()
    mock_stream.close.assert_called_once()
    mock_sock.close.assert_called_once()
