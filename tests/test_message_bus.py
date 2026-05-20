import asyncio
import socket

import pytest

from dbus_fast.aio import MessageBus
from dbus_fast.errors import AuthError, DBusError, InternalError, InvalidAddressError
from dbus_fast.message_bus import BaseMessageBus


@pytest.mark.asyncio
async def test_tcp_socket_cleanup_on_connect_fail() -> None:
    """Test that socket resources are cleaned up on a failed TCP connection."""
    bus = MessageBus("tcp:host=127.0.0.1,port=1")

    with pytest.raises(ConnectionRefusedError):
        await bus.connect()

    assert bus._stream is None
    assert bus._sock is None


@pytest.mark.asyncio
async def test_unix_socket_cleanup_on_connect_fail() -> None:
    """Test that socket resources are cleaned up on a failed Unix socket connection."""
    bus = MessageBus("unix:path=/there-is-no-way-that-this-file-should-exist")

    with pytest.raises(FileNotFoundError):
        await bus.connect()

    assert bus._stream is None
    assert bus._sock is None


@pytest.mark.asyncio
async def test_tcp_socket_cleanup_with_host_only() -> None:
    """Test TCP connection with host option only (no port)."""
    bus = MessageBus("tcp:host=127.0.0.1")

    with pytest.raises(OSError):
        # Port defaults to 0, which will fail
        await bus.connect()

    assert bus._stream is None
    assert bus._sock is None


@pytest.mark.asyncio
async def test_tcp_socket_cleanup_with_port_only() -> None:
    """Test TCP connection with port option only (no host)."""
    bus = MessageBus("tcp:port=1")

    with pytest.raises(OSError):
        # Host defaults to empty string, which will fail
        await bus.connect()

    assert bus._stream is None
    assert bus._sock is None


@pytest.mark.asyncio
async def test_unix_socket_abstract_cleanup_on_connect_fail() -> None:
    """Test that socket resources are cleaned up on a failed abstract Unix socket connection."""
    bus = MessageBus("unix:abstract=/tmp/nonexistent-abstract-socket")

    # On Linux: ConnectionRefusedError, on macOS: FileNotFoundError
    with pytest.raises((FileNotFoundError, ConnectionRefusedError)):
        await bus.connect()

    assert bus._stream is None
    assert bus._sock is None


@pytest.mark.asyncio
async def test_unix_socket_invalid_path_specifier() -> None:
    """Test that Unix socket with invalid path specifier raises error."""
    bus = MessageBus("unix:invalid=foo")

    with pytest.raises(
        InvalidAddressError, match="got unix transport with unknown path specifier"
    ):
        await bus.connect()


@pytest.mark.asyncio
async def test_unknown_socket_type() -> None:
    """Test that unknown socket types raise InvalidAddressError."""
    bus = MessageBus("unknown:works=nope")

    with pytest.raises(InvalidAddressError, match="got unknown address transport"):
        await bus.connect()


@pytest.mark.asyncio
async def test_tcp_socket_non_integer_port() -> None:
    """A non-integer tcp port option is reported as InvalidAddressError."""
    bus = MessageBus("tcp:host=127.0.0.1,port=not-a-number")

    with pytest.raises(
        InvalidAddressError, match="got tcp transport with invalid port"
    ):
        await bus.connect()


@pytest.mark.asyncio
async def test_aio_connect_falls_back_between_transports() -> None:
    """If the first transport fails, aio connect() tries the next one and
    raises the last error if all fail.
    """
    bus = MessageBus(
        "unix:path=/there-is-no-way-that-this-file-should-exist;"
        "tcp:host=127.0.0.1,port=1"
    )

    with pytest.raises(ConnectionRefusedError):
        await bus.connect()

    assert bus._stream is None
    assert bus._sock is None


@pytest.mark.asyncio
async def test_aio_connect_cleanup_after_socket_connected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failure after the socket is connected clears _sock/_stream/_fd/_writer."""
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    host, port = listener.getsockname()
    try:

        async def _boom(self: MessageBus) -> None:
            raise AuthError("simulated auth failure")

        monkeypatch.setattr(MessageBus, "_authenticate", _boom)

        bus = MessageBus(f"tcp:host={host},port={port}")

        with pytest.raises(AuthError, match="simulated auth failure"):
            await bus.connect()

        assert bus._sock is None
        assert bus._stream is None
        assert bus._fd is None
        assert bus._writer is None
    finally:
        listener.close()


@pytest.mark.parametrize(
    ("transport", "options", "family"),
    [
        ("unix", {"path": "/nope"}, socket.AF_UNIX),
        ("tcp", {"host": "127.0.0.1", "port": "1"}, socket.AF_INET),
    ],
    ids=["unix", "tcp"],
)
def test_create_socket_for_transport_makefile_failure_closes_socket(
    monkeypatch: pytest.MonkeyPatch,
    transport: str,
    options: dict[str, str],
    family: int,
) -> None:
    """A makefile() failure closes the socket before re-raising."""
    closed: list[int] = []
    real_close = socket.socket.close

    def tracking_close(self: socket.socket) -> None:
        closed.append(self.family)
        real_close(self)

    def boom(self: socket.socket, *args: object, **kwargs: object) -> None:
        raise OSError("makefile failed")

    monkeypatch.setattr(socket.socket, "close", tracking_close)
    monkeypatch.setattr(socket.socket, "makefile", boom)

    with pytest.raises(OSError, match="makefile failed"):
        BaseMessageBus._create_socket_for_transport(transport, options)

    assert family in closed


def test_get_proxy_object_raises_when_proxy_object_class_missing() -> None:
    # ProxyObject defaults to None on BaseMessageBus, which is the condition
    # under test. Passing an explicit bus_address avoids depending on
    # DBUS_SESSION_BUS_ADDRESS in the environment.
    bus = BaseMessageBus(bus_address="unix:path=/dev/null")
    with pytest.raises(InternalError):
        bus.get_proxy_object("com.example.Test", "/com/example/Test", "<node/>")


@pytest.mark.asyncio
async def test_aio_connect_hello_error_propagates_and_clears_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """on_hello with an error reply tears down sock/stream/fd/writer."""
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    host, port = listener.getsockname()
    try:

        async def _auth_noop(self: MessageBus) -> None:
            return

        monkeypatch.setattr(MessageBus, "_authenticate", _auth_noop)

        bus = MessageBus(f"tcp:host={host},port={port}")
        # Force next_serial() to return 2 so the else-branch that calls
        # _generate_hello_serialized() is exercised instead of the cached
        # HELLO_1_SERIALIZED constant.
        bus._serial = 1

        task = asyncio.create_task(bus.connect())

        for _ in range(200):
            if bus._method_return_handlers:
                break
            await asyncio.sleep(0)
        else:
            task.cancel()
            raise AssertionError("on_hello handler never registered")

        serial, handler = next(iter(bus._method_return_handlers.items()))
        assert serial == 2

        handler(None, DBusError("org.freedesktop.DBus.Error.Failed", "boom", None))

        with pytest.raises(DBusError, match="boom"):
            await task

        assert bus._sock is None
        assert bus._stream is None
        assert bus._fd is None
        assert bus._writer is None
    finally:
        listener.close()
