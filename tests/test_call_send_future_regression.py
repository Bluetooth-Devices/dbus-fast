"""Regression tests for ownership of futures created by MessageBus.call."""

import asyncio
import gc
import socket

from dbus_fast import Message
from dbus_fast.aio.message_bus import MessageBus, _MessageWriter


def message():
    return Message(
        destination="org.bluez",
        path="/device",
        interface="org.bluez.Device1",
        member="Disconnect",
    )


def test_call_does_not_leave_send_failure_unobserved():
    async def scenario():
        loop = asyncio.get_running_loop()
        errors = []
        loop.set_exception_handler(lambda _loop, context: errors.append(context))
        sock, peer = socket.socketpair()
        sock.setblocking(False)
        peer.close()
        bus = MessageBus(bus_address="unix:path=/nonexistent")
        bus._sock, bus._fd = sock, sock.fileno()
        bus._stream = sock.makefile("rwb")
        bus._writer = _MessageWriter(bus)
        task = asyncio.create_task(bus.call(message()))
        await asyncio.sleep(0)
        assert not task.done()
        bus._writer.write_callback(remove_writer=False)
        try:
            await task
        except BrokenPipeError:
            pass
        else:
            raise AssertionError("call must report the failed write")
        bus._writer.fut = None
        del task, bus
        gc.collect()
        await asyncio.sleep(0)
        assert not errors
        sock.close()

    asyncio.run(scenario())


def test_call_success_and_cancellation_keep_reply_semantics():
    async def scenario():
        bus = MessageBus(bus_address="unix:path=/nonexistent")
        bus._writer = type(
            "Writer",
            (),
            {"schedule_write": lambda self, msg, future: future.set_result(None)},
        )()
        call = asyncio.create_task(bus.call(message()))
        await asyncio.sleep(0)
        serial, callback = next(iter(bus._method_return_handlers.items()))
        reply = Message.new_method_return(
            Message(serial=serial, path="/device", member="Disconnect")
        )
        callback(reply, None)
        assert await call is reply
        call = asyncio.create_task(bus.call(message()))
        await asyncio.sleep(0)
        call.cancel()
        try:
            await call
        except asyncio.CancelledError:
            pass
        else:
            raise AssertionError("cancellation must propagate")

    asyncio.run(scenario())


def test_synchronous_send_failure_does_not_orphan_futures():
    async def scenario():
        loop = asyncio.get_running_loop()
        errors = []
        loop.set_exception_handler(lambda _loop, context: errors.append(context))
        bus = MessageBus(bus_address="unix:path=/nonexistent")

        class FailingWriter:
            def schedule_write(self, msg, future):
                future.set_exception(BrokenPipeError("send failed"))
                callback = next(iter(bus._method_return_handlers.values()))
                callback(None, BrokenPipeError("reply failed"))
                raise OSError("writer registration failed")

        bus._writer = FailingWriter()
        try:
            await bus.call(message())
        except OSError as error:
            assert str(error) == "writer registration failed"
        else:
            raise AssertionError("synchronous writer failure must propagate")
        assert not bus._method_return_handlers
        del bus
        gc.collect()
        await asyncio.sleep(0)
        assert not errors

    asyncio.run(scenario())


def test_send_failure_before_future_completion_cleans_up_pending_futures():
    async def scenario():
        loop = asyncio.get_running_loop()
        errors = []
        loop.set_exception_handler(lambda _loop, context: errors.append(context))
        bus = MessageBus(bus_address="unix:path=/nonexistent")
        pending = []

        class FailingWriter:
            def schedule_write(self, msg, future):
                pending.append(future)
                raise OSError("writer registration failed")

        bus._writer = FailingWriter()
        try:
            await bus.call(message())
        except OSError as error:
            assert str(error) == "writer registration failed"
        else:
            raise AssertionError("writer failure must propagate")
        assert pending[0].cancelled()
        assert not bus._method_return_handlers
        del bus
        gc.collect()
        await asyncio.sleep(0)
        assert not errors

    asyncio.run(scenario())


def test_cancelled_send_and_call_leave_no_unhandled_exception():
    async def scenario():
        loop = asyncio.get_running_loop()
        errors = []
        loop.set_exception_handler(lambda _loop, context: errors.append(context))
        bus = MessageBus(bus_address="unix:path=/nonexistent")
        pending = []

        class PendingWriter:
            def schedule_write(self, msg, future):
                pending.append(future)

        bus._writer = PendingWriter()
        call = asyncio.create_task(bus.call(message()))
        await asyncio.sleep(0)
        pending[0].cancel()
        call.cancel()
        try:
            await call
        except asyncio.CancelledError:
            pass
        else:
            raise AssertionError("cancellation must propagate")
        await asyncio.sleep(0)
        assert not errors

    asyncio.run(scenario())
