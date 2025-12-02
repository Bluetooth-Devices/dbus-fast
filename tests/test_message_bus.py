import pytest

from dbus_fast.aio import MessageBus
from dbus_fast.errors import InvalidAddressError


@pytest.mark.asyncio
async def test_tcp_socket_cleanup_on_connect_fail() -> None:
    """Test that socket resources are cleaned up on a failed TCP connection."""
    bus = MessageBus("tcp:host=127.0.0.1,port=1")

    with pytest.raises(ConnectionRefusedError):
        await bus.connect()

    assert bus._stream.closed
    assert bus._sock._closed


@pytest.mark.asyncio
async def test_unix_socket_cleanup_on_connect_fail() -> None:
    """Test that socket resources are cleaned up on a failed Unix socket connection."""
    bus = MessageBus("unix:path=/there-is-no-way-that-this-file-should-exist")

    with pytest.raises(FileNotFoundError):
        await bus.connect()

    assert bus._stream.closed
    assert bus._sock._closed


@pytest.mark.asyncio
async def test_tcp_socket_cleanup_with_host_only() -> None:
    """Test TCP connection with host option only (no port)."""
    bus = MessageBus("tcp:host=127.0.0.1")

    with pytest.raises(OSError):
        # Port defaults to 0, which will fail
        await bus.connect()

    assert bus._stream.closed
    assert bus._sock._closed


@pytest.mark.asyncio
async def test_tcp_socket_cleanup_with_port_only() -> None:
    """Test TCP connection with port option only (no host)."""
    bus = MessageBus("tcp:port=1")

    with pytest.raises(OSError):
        # Host defaults to empty string, which will fail
        await bus.connect()

    assert bus._stream.closed
    assert bus._sock._closed


@pytest.mark.asyncio
async def test_unix_socket_abstract_cleanup_on_connect_fail() -> None:
    """Test that socket resources are cleaned up on a failed abstract Unix socket connection."""
    bus = MessageBus("unix:abstract=/tmp/nonexistent-abstract-socket")

    # On Linux: ConnectionRefusedError, on macOS: FileNotFoundError
    with pytest.raises((FileNotFoundError, ConnectionRefusedError)):
        await bus.connect()

    assert bus._stream.closed
    assert bus._sock._closed


@pytest.mark.asyncio
async def test_unix_socket_invalid_path_specifier() -> None:
    """Test that Unix socket with invalid path specifier raises error."""

    with pytest.raises(
        InvalidAddressError, match="got unix transport with unknown path specifier"
    ):
        MessageBus("unix:invalid=foo")


@pytest.mark.asyncio
async def test_unknown_socket_type() -> None:
    """Test that unknown socket types raise InvalidAddressError."""

    with pytest.raises(InvalidAddressError, match="got unknown address transport"):
        MessageBus("unknown:works=nope")
