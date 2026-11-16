from __future__ import annotations

import array
import asyncio
import errno
import os
import socket
from collections.abc import Iterator
from types import SimpleNamespace
from typing import Any

import pytest

from dbus_fast import Message
from dbus_fast.aio.message_bus import _MessageWriter


@pytest.fixture
def socket_pair() -> Iterator[tuple[socket.socket, socket.socket]]:
    ours, peer = socket.socketpair()
    ours.setblocking(False)
    peer.setblocking(False)
    try:
        yield ours, peer
    finally:
        ours.close()
        peer.close()


def _make_writer(
    sock: Any, negotiate_unix_fd: bool = False
) -> tuple[_MessageWriter, list[Exception | None]]:
    finalized: list[Exception | None] = []
    bus = SimpleNamespace(
        _negotiate_unix_fd=negotiate_unix_fd,
        _sock=sock,
        _loop=asyncio.get_running_loop(),
        _fd=sock.fileno(),
        _user_disconnect=False,
        _finalize=finalized.append,
        unique_name=":1.1",
    )
    return _MessageWriter(bus), finalized  # type: ignore[arg-type]


class _SendmsgBlocksOnce:
    """Socket wrapper whose first sendmsg() fails as if the send buffer was full."""

    def __init__(self, sock: socket.socket) -> None:
        self._sock = sock
        self.blocked = False

    def fileno(self) -> int:
        return self._sock.fileno()

    def send(self, data: Any) -> int:
        return self._sock.send(data)

    def sendmsg(self, buffers: Any, ancdata: Any) -> int:
        if not self.blocked:
            self.blocked = True
            raise BlockingIOError(errno.EAGAIN, os.strerror(errno.EAGAIN))
        return self._sock.sendmsg(buffers, ancdata)


@pytest.mark.asyncio
async def test_full_send_buffer_does_not_finalize_bus(
    socket_pair: tuple[socket.socket, socket.socket],
) -> None:
    """Messages queued while the send buffer is full are sent once it drains."""
    ours, peer = socket_pair
    ours.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096)
    loop = asyncio.get_running_loop()
    writer, finalized = _make_writer(ours)

    expected = bytearray()
    futures: list[asyncio.Future[None]] = []
    for serial in range(1, 9):
        msg = Message.new_signal("/test", "test.Flood", "Data", "s", ["x" * 65536])
        msg.serial = serial
        expected += msg._marshall(False)
        futures.append(loop.create_future())
        writer.schedule_write(msg, futures[-1])

    assert finalized == []
    assert not any(future.done() for future in futures[1:])

    received = bytearray()
    while len(received) < len(expected):
        received += await loop.sock_recv(peer, len(expected) - len(received))

    await asyncio.gather(*futures)
    assert received == expected
    assert finalized == []


@pytest.mark.asyncio
async def test_unix_fds_are_kept_when_sendmsg_would_block(
    socket_pair: tuple[socket.socket, socket.socket],
) -> None:
    """File descriptors are still attached when a blocked sendmsg() is retried."""
    ours, peer = socket_pair
    loop = asyncio.get_running_loop()
    sock = _SendmsgBlocksOnce(ours)
    writer, finalized = _make_writer(sock, negotiate_unix_fd=True)

    read_fd, write_fd = os.pipe()
    try:
        msg = Message.new_signal("/test", "test.Fd", "Data", "h", [0], [write_fd])
        msg.serial = 1
        future: asyncio.Future[None] = loop.create_future()
        writer.schedule_write(msg, future)

        assert sock.blocked
        assert finalized == []

        await future
        fds = array.array("i")
        _, ancdata, _, _ = peer.recvmsg(4096, socket.CMSG_LEN(fds.itemsize))
        assert finalized == []
        assert len(ancdata) == 1
        level, kind, data = ancdata[0]
        assert (level, kind) == (socket.SOL_SOCKET, socket.SCM_RIGHTS)
        fds.frombytes(data)
        os.close(fds[0])
    finally:
        os.close(read_fd)
        os.close(write_fd)
