"""Pre-auth DoS guards for the auth-line readers."""

from __future__ import annotations

import asyncio
import contextlib
import socket
from collections.abc import Generator
from types import SimpleNamespace

import pytest

from dbus_fast.aio.message_bus import MessageBus
from dbus_fast.errors import AuthError


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
