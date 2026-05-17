"""Pre-auth DoS guards for the auth-line readers."""

from __future__ import annotations

import asyncio
import socket
from types import SimpleNamespace

import pytest

from dbus_fast.aio.message_bus import MessageBus
from dbus_fast.errors import AuthError


def _fake_aio_self(sock: socket.socket) -> SimpleNamespace:
    return SimpleNamespace(_sock=sock, _loop=asyncio.get_running_loop())


@pytest.mark.asyncio
async def test_auth_readline_raises_on_eof() -> None:
    server, client = socket.socketpair()
    try:
        client.setblocking(False)
        server.close()  # peer EOF before any data is sent

        coro = MessageBus._auth_readline(_fake_aio_self(client))
        with pytest.raises(AuthError):
            await asyncio.wait_for(coro, timeout=1.0)
    finally:
        client.close()


@pytest.mark.asyncio
async def test_auth_readline_rejects_oversize_line() -> None:
    server, client = socket.socketpair()
    try:
        client.setblocking(False)
        server.setblocking(True)
        # Stream junk that never contains \r\n; cap is 16 KiB so 64 KiB is
        # well past the limit but small enough to fit a socket buffer.
        server.sendall(b"A" * 64 * 1024)
        server.close()

        coro = MessageBus._auth_readline(_fake_aio_self(client))
        with pytest.raises(AuthError):
            await asyncio.wait_for(coro, timeout=1.0)
    finally:
        client.close()


@pytest.mark.asyncio
async def test_auth_readline_returns_line() -> None:
    server, client = socket.socketpair()
    try:
        client.setblocking(False)
        server.setblocking(True)
        server.sendall(b"OK 1234\r\n")
        server.close()

        line = await asyncio.wait_for(
            MessageBus._auth_readline(_fake_aio_self(client)), timeout=1.0
        )
        assert line == "OK 1234"
    finally:
        client.close()
