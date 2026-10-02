"""Pre-auth DoS guards for the auth-line readers."""

from __future__ import annotations

import asyncio
import contextlib
import socket
from collections.abc import Generator
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from dbus_fast.aio.message_bus import MessageBus
from dbus_fast.auth import AuthExternal
from dbus_fast.errors import AuthError, AuthTimeoutError


def _fake_aio_self(sock: socket.socket) -> SimpleNamespace:
    return SimpleNamespace(_sock=sock, _loop=asyncio.get_running_loop())


@pytest.fixture
def socket_pair() -> Generator[tuple[socket.socket, socket.socket]]:
    server, client = socket.socketpair()
    server.setblocking(False)
    client.setblocking(False)
    try:
        yield server, client
    finally:
        server.close()
        client.close()


@pytest.mark.asyncio
async def test_auth_readline_raises_on_eof(
    socket_pair: tuple[socket.socket, socket.socket],
) -> None:
    server, client = socket_pair
    server.close()  # peer EOF before any data is sent

    coro = MessageBus._auth_readline(_fake_aio_self(client))
    with pytest.raises(AuthError, match=r"connection closed during authentication"):
        await asyncio.wait_for(coro, timeout=1.0)


@pytest.mark.asyncio
async def test_auth_readline_rejects_oversize_line(
    socket_pair: tuple[socket.socket, socket.socket],
) -> None:
    server, client = socket_pair
    # Stream junk that never contains \r\n; cap is 16 KiB so 64 KiB is
    # well past the limit. Drive the send from a background task so the
    # peer write progresses as the reader drains, regardless of the
    # socketpair send buffer size.
    loop = asyncio.get_running_loop()
    writer = asyncio.create_task(loop.sock_sendall(server, b"A" * 64 * 1024))
    try:
        coro = MessageBus._auth_readline(_fake_aio_self(client))
        with pytest.raises(AuthError, match=r"auth line exceeded maximum size"):
            await asyncio.wait_for(coro, timeout=1.0)
    finally:
        writer.cancel()
        with contextlib.suppress(asyncio.CancelledError, OSError):
            await writer


@pytest.mark.asyncio
async def test_auth_readline_returns_line(
    socket_pair: tuple[socket.socket, socket.socket],
) -> None:
    server, client = socket_pair
    await asyncio.get_running_loop().sock_sendall(server, b"OK 1234\r\n")

    line = await asyncio.wait_for(
        MessageBus._auth_readline(_fake_aio_self(client)), timeout=1.0
    )
    assert line == "OK 1234"


@pytest.mark.asyncio
async def test_authenticate_raises_auth_timeout_error_when_server_silent(
    socket_pair: tuple[socket.socket, socket.socket],
) -> None:
    """Verify authentication timeouts raise AuthTimeoutError."""
    _, client = socket_pair
    bus = MessageBus.__new__(MessageBus)
    bus._loop = asyncio.get_running_loop()
    bus._sock = client
    bus._auth = AuthExternal()
    bus._negotiate_unix_fd = False
    bus._auth_timeout = 0.05

    with pytest.raises(AuthTimeoutError, match="authentication timed out"):
        await asyncio.wait_for(MessageBus._authenticate(bus), timeout=1.0)


@pytest.mark.asyncio
async def test_authenticate_does_not_wrap_unrelated_timeout_error() -> None:
    """A TimeoutError from the handshake itself is not reported as AuthTimeoutError."""
    bus = MessageBus.__new__(MessageBus)
    bus._auth_timeout = 5.0

    async def _raise(self: MessageBus) -> None:
        raise TimeoutError("socket stalled")

    with (
        patch.object(MessageBus, "_inner_authenticate", _raise),
        pytest.raises(TimeoutError, match="socket stalled") as exc_info,
    ):
        await MessageBus._authenticate(bus)
    assert not isinstance(exc_info.value, AuthTimeoutError)
