import sys

import pytest
from dbus_fast import Message, MessageFlag, MessageType
from dbus_fast.glib import MessageBus

from tests.util import check_gi_repository, skip_reason_no_gi

has_gi = check_gi_repository()

if has_gi:
    from gi.repository import GLib


@pytest.mark.skipif(not has_gi, reason=skip_reason_no_gi)
@pytest.mark.skipif(
    sys.version_info[:3][1] in (10, 11, 12, 13),
    reason="segfaults on py3.10,py3.11,py3.12,py3.13",
)
def test_standard_interfaces():
    bus = MessageBus().connect_sync()
    msg = Message(
        destination="org.freedesktop.DBus",
        path="/org/freedesktop/DBus",
        interface="org.freedesktop.DBus",
        member="ListNames",
        serial=bus.next_serial(),
    )
    reply = bus.call_sync(msg)

    assert reply.message_type == MessageType.METHOD_RETURN
    assert reply.reply_serial == msg.serial
    assert reply.signature == "as"
    assert bus.unique_name in reply.body[0]

    msg.interface = "org.freedesktop.DBus.Introspectable"
    msg.member = "Introspect"
    msg.serial = bus.next_serial()

    reply = bus.call_sync(msg)
    assert reply.message_type == MessageType.METHOD_RETURN
    assert reply.reply_serial == msg.serial
    assert reply.signature == "s"
    assert type(reply.body[0]) is str

    msg.member = "MemberDoesNotExist"
    msg.serial = bus.next_serial()

    reply = bus.call_sync(msg)
    assert reply.message_type == MessageType.ERROR
    assert reply.reply_serial == msg.serial
    assert reply.error_name
    assert reply.signature == "s"
    assert type(reply.body[0]) is str

    bus.disconnect()


@pytest.mark.skipif(not has_gi, reason=skip_reason_no_gi)
@pytest.mark.skipif(
    sys.version_info[:3][1] in (10, 11, 12, 13),
    reason="segfaults on py3.10,py3.11,py3.12,py3.13",
)
def test_sending_messages_between_buses():
    bus1 = MessageBus().connect_sync()
    bus2 = MessageBus().connect_sync()

    msg = Message(
        destination=bus1.unique_name,
        path="/org/test/path",
        interface="org.test.iface",
        member="SomeMember",
        serial=bus2.next_serial(),
    )

    def message_handler(sent):
        if sent.sender == bus2.unique_name and sent.serial == msg.serial:
            assert sent.path == msg.path
            assert sent.serial == msg.serial
            assert sent.interface == msg.interface
            assert sent.member == msg.member
            bus1.send(Message.new_method_return(sent, "s", ["got it"]))
            bus1.remove_message_handler(message_handler)
            return True

    bus1.add_message_handler(message_handler)

    reply = bus2.call_sync(msg)

    assert reply.message_type == MessageType.METHOD_RETURN, reply.body[0]
    assert reply.sender == bus1.unique_name
    assert reply.signature == "s"
    assert reply.body == ["got it"]
    assert reply.reply_serial == msg.serial

    def message_handler_error(sent):
        if sent.sender == bus2.unique_name and sent.serial == msg.serial:
            assert sent.path == msg.path
            assert sent.serial == msg.serial
            assert sent.interface == msg.interface
            assert sent.member == msg.member
            bus1.send(Message.new_error(sent, "org.test.Error", "throwing an error"))
            bus1.remove_message_handler(message_handler_error)
            return True

    bus1.add_message_handler(message_handler_error)

    msg.serial = bus2.next_serial()

    reply = bus2.call_sync(msg)

    assert reply.message_type == MessageType.ERROR
    assert reply.sender == bus1.unique_name
    assert reply.reply_serial == msg.serial
    assert reply.error_name == "org.test.Error"
    assert reply.signature == "s"
    assert reply.body == ["throwing an error"]

    msg.serial = bus2.next_serial()
    msg.flags = MessageFlag.NO_REPLY_EXPECTED
    reply = bus2.call_sync(msg)
    assert reply is None

    bus1.disconnect()
    bus2.disconnect()
    bus1._sock.close()
    bus2._sock.close()


@pytest.mark.skipif(not has_gi, reason=skip_reason_no_gi)
@pytest.mark.skipif(
    sys.version_info[:3][1] in (10, 11, 12, 13),
    reason="segfaults on py3.10,py3.11,py3.12,py3.13",
)
def test_sending_signals_between_buses():
    bus1 = MessageBus().connect_sync()
    bus2 = MessageBus().connect_sync()

    add_match_msg = Message(
        destination="org.freedesktop.DBus",
        path="/org/freedesktop/DBus",
        interface="org.freedesktop.DBus",
        member="AddMatch",
        signature="s",
        body=[f"sender={bus2.unique_name}"],
    )

    bus1.call_sync(add_match_msg)

    main = GLib.MainLoop()

    def wait_for_message():
        ret = None

        def message_handler(signal):
            nonlocal ret
            if signal.sender == bus2.unique_name:
                ret = signal
                bus1.remove_message_handler(message_handler)
                main.quit()

        bus1.add_message_handler(message_handler)
        main.run()
        return ret

    bus2.send(
        Message.new_signal(
            "/org/test/path", "org.test.interface", "SomeSignal", "s", ["a signal"]
        )
    )

    signal = wait_for_message()

    assert signal.message_type == MessageType.SIGNAL
    assert signal.path == "/org/test/path"
    assert signal.interface == "org.test.interface"
    assert signal.member == "SomeSignal"
    assert signal.signature == "s"
    assert signal.body == ["a signal"]

    bus1.disconnect()
    bus2.disconnect()
    bus1._sock.close()
    bus2._sock.close()
