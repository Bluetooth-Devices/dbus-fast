import pytest

from dbus_fast.aio import MessageBus


@pytest.mark.asyncio
async def test_tcp_socket_cleanup_on_connect_fail(
) -> None:
    """Test that socket resources are cleaned up on a failed TCP connection."""

    # A bit ugly, but we need to access members of the class after __init__()
    # raises, so we need to split __new__() and __init__().
    bus = MessageBus.__new__(MessageBus)

    with pytest.raises(ConnectionRefusedError):
        bus.__init__("tcp:host=127.0.0.1,port=1")

    assert bus._stream.closed
    assert bus._sock._closed


@pytest.mark.asyncio
async def test_unix_socket_cleanup_on_connect_fail(
) -> None:
    """Test that socket resources are cleaned up on a failed Unix socket connection."""

    # A bit ugly, but we need to access members of the class after __init__()
    # raises, so we need to split __new__() and __init__().
    bus = MessageBus.__new__(MessageBus)

    with pytest.raises(FileNotFoundError):
        bus.__init__("unix:path=/there-is-no-way-that-this-file-should-exist")

    assert bus._stream.closed
    assert bus._sock._closed
