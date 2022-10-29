import io
import json
import os
from typing import Any, Dict
from unittest.mock import patch

import pytest

from dbus_fast import Message, MessageFlag, MessageType, SignatureTree, Variant
from dbus_fast._private._cython_compat import FakeCython
from dbus_fast._private.unmarshaller import Unmarshaller
from dbus_fast.unpack import unpack_variants


def print_buf(buf):
    i = 0
    while True:
        p = buf[i : i + 8]
        if not p:
            break
        print(p)
        i += 8


# these messages have been verified with another library
with open(os.path.dirname(__file__) + "/data/messages.json") as f:
    table = json.load(f)


def json_to_message(message: Dict[str, Any]) -> Message:
    copy = dict(message)
    if "message_type" in copy:
        copy["message_type"] = MessageType(copy["message_type"])
    if "flags" in copy:
        copy["flags"] = MessageFlag(copy["flags"])

    return Message(**copy)


# variants are an object in the json
def replace_variants(type_, item):
    if type_.token == "v" and type(item) is not Variant:
        item = Variant(
            item["signature"],
            replace_variants(SignatureTree(item["signature"]).types[0], item["value"]),
        )
    elif type_.token == "a":
        for i, item_child in enumerate(item):
            if type_.children[0].token == "{":
                for k, v in item.items():
                    item[k] = replace_variants(type_.children[0].children[1], v)
            else:
                item[i] = replace_variants(type_.children[0], item_child)
    elif type_.token == "(":
        for i, item_child in enumerate(item):
            if type_.children[0].token == "{":
                assert False
            else:
                item[i] = replace_variants(type_.children[i], item_child)

    return item


def json_dump(what):
    def dumper(obj):
        try:
            return obj.toJSON()
        except Exception:
            return obj.__dict__

    return json.dumps(what, default=dumper, indent=2)


def test_marshalling_with_table():
    for item in table:
        message = json_to_message(item["message"])

        body = []
        for i, type_ in enumerate(message.signature_tree.types):
            body.append(replace_variants(type_, message.body[i]))
        message.body = body

        buf = message._marshall(False)
        data = bytes.fromhex(item["data"])

        if buf != data:
            print("message:")
            print(json_dump(item["message"]))
            print("")
            print("mine:")
            print_buf(bytes(buf))
            print("")
            print("theirs:")
            print_buf(data)

        assert buf == data


@pytest.mark.parametrize("unmarshall_table", (table,))
def test_unmarshalling_with_table(unmarshall_table):
    from dbus_fast._private import unmarshaller

    for item in unmarshall_table:

        stream = io.BytesIO(bytes.fromhex(item["data"]))
        unmarshaller = Unmarshaller(stream)
        try:
            unmarshaller.unmarshall()
        except Exception as e:
            print("message failed to unmarshall:")
            print(json_dump(item["message"]))
            raise e

        message = json_to_message(item["message"])

        body = []
        for i, type_ in enumerate(message.signature_tree.types):
            body.append(replace_variants(type_, message.body[i]))
        message.body = body

        for attr in [
            "body",
            "signature",
            "message_type",
            "destination",
            "path",
            "interface",
            "member",
            "flags",
            "serial",
        ]:
            assert getattr(unmarshaller.message, attr) == getattr(
                message, attr
            ), f"attr doesnt match: {attr}"


def test_unmarshall_can_resume():
    """Verify resume works."""
    bluez_rssi_message = (
        "6c04010134000000e25389019500000001016f00250000002f6f72672f626c75657a2f686369302f6465"
        "765f30385f33415f46325f31455f32425f3631000000020173001f0000006f72672e667265656465736b"
        "746f702e444275732e50726f7065727469657300030173001100000050726f706572746965734368616e"
        "67656400000000000000080167000873617b73767d617300000007017300040000003a312e3400000000"
        "110000006f72672e626c75657a2e446576696365310000000e0000000000000004000000525353490001"
        "6e00a7ff000000000000"
    )
    message_bytes = bytes.fromhex(bluez_rssi_message)

    class SlowStream(io.IOBase):
        """A fake stream that will only give us one byte at a time."""

        def __init__(self):
            self.data = message_bytes
            self.pos = 0

        def read(self, n) -> bytes:
            data = self.data[self.pos : self.pos + 1]
            self.pos += 1
            return data

    stream = SlowStream()
    unmarshaller = Unmarshaller(stream)

    for _ in range(len(bluez_rssi_message)):
        if unmarshaller.unmarshall():
            break
    assert unmarshaller.message is not None


def test_unmarshall_bluez_message():
    bluez_mfr_message = (
        "6c040101780000009aca0a009500000001016f00250000002f6f72672f626c75657a2f686369302f646576"
        "5f44305f43325f34455f30385f41425f3537000000020173001f0000006f72672e667265656465736b746f"
        "702e444275732e50726f7065727469657300030173001100000050726f706572746965734368616e676564"
        "00000000000000080167000873617b73767d617300000007017300040000003a312e340000000011000000"
        "6f72672e626c75657a2e446576696365310000005400000000000000040000005253534900016e00aaff00"
        "00100000004d616e756661637475726572446174610005617b71767d002400000075000261790000001800"
        "00004204010170d0c24e08ab57d2c24e08ab5601000000000000000000006c040101340000009bca0a0095"
        "00000001016f002500"
    )
    message_bytes = bytes.fromhex(bluez_mfr_message)
    stream = io.BytesIO(message_bytes)
    unmarshaller = Unmarshaller(stream)
    assert unmarshaller.unmarshall()
    message = unmarshaller.message
    assert message is not None
    assert message.body == [
        "org.bluez.Device1",
        {
            "ManufacturerData": Variant(
                "a{qv}",
                {
                    117: Variant(
                        "ay",
                        bytearray(
                            b"B\x04\x01\x01p\xd0\xc2N\x08\xabW\xd2\xc2N\x08\xabV\x01\x00\x00\x00\x00\x00\x00"
                        ),
                    )
                },
            ),
            "RSSI": Variant("n", -86),
        },
        [],
    ]
    assert message.sender == ":1.4"
    assert message.path == "/org/bluez/hci0/dev_D0_C2_4E_08_AB_57"
    assert message.interface == "org.freedesktop.DBus.Properties"
    assert message.member == "PropertiesChanged"
    assert message.signature == "sa{sv}as"
    assert message.message_type == MessageType.SIGNAL
    assert message.flags == MessageFlag.NO_REPLY_EXPECTED
    assert message.serial == 707226
    assert message.destination is None
    unpacked = unpack_variants(message.body)
    assert unpacked == [
        "org.bluez.Device1",
        {
            "ManufacturerData": {
                117: bytearray(
                    b"B\x04\x01\x01p\xd0\xc2N\x08\xabW\xd2"
                    b"\xc2N\x08\xabV\x01\x00\x00"
                    b"\x00\x00\x00\x00"
                )
            },
            "RSSI": -86,
        },
        [],
    ]


def test_unmarshall_bluez_interfaces_added_message():
    bluez_interfaces_added_message = (
        b'l\4\1\1\240\2\0\0\227\272\23\0u\0\0\0\1\1o\0\1\0\0\0/\0\0\0\0\0\0\0\2\1s\0"\0\0\0'
        b"org.freedesktop.DBus.ObjectManager\0\0\0\0\0\0\3\1s\0\17\0\0\0InterfacesAdded\0\10"
        b"\1g\0\noa{sa{sv}}\0\7\1s\0\4\0\0\0:1.4\0\0\0\0%\0\0\0/org/bluez/hci1/dev_58_2D_34"
        b"_60_26_36\0\0\0p\2\0\0#\0\0\0org.freedesktop.DBus.Introspectable\0\0\0\0\0\0\0\0\0"
        b"\21\0\0\0org.bluez.Device1\0\0\0\364\1\0\0\0\0\0\0\7\0\0\0Address\0\1s\0\0\21\0\0"
        b"\00058:2D:34:60:26:36\0\0\0\v\0\0\0AddressType\0\1s\0\0\6\0\0\0public\0\0\4\0\0\0"
        b"Name\0\1s\0\33\0\0\0Qingping Door/Window Sensor\0\0\0\0\0\5\0\0\0Alias\0\1s\0\0\0"
        b"\0\33\0\0\0Qingping Door/Window Sensor\0\6\0\0\0Paired\0\1b\0\0\0\0\0\0\0\0\0\0\0"
        b"\7\0\0\0Trusted\0\1b\0\0\0\0\0\0\0\0\0\0\7\0\0\0Blocked\0\1b\0\0\0\0\0\0\0\0\0\0\r"
        b"\0\0\0LegacyPairing\0\1b\0\0\0\0\0\0\0\0\0\0\0\0\4\0\0\0RSSI\0\1n\0\316\377\0\0\t"
        b"\0\0\0Connected\0\1b\0\0\0\0\0\0\0\0\5\0\0\0UUIDs\0\2as\0\0\0\0\0\0\0\0\0\0\0\7\0"
        b"\0\0Adapter\0\1o\0\0\17\0\0\0/org/bluez/hci1\0\0\0\0\0\v\0\0\0ServiceData\0\5a{sv}"
        b"\0\0@\0\0\0\0\0\0\0$\0\0\0000000fe95-0000-1000-8000-00805f9b34fb\0\2ay\0\0\0\0\f\0"
        b"\0\0000X\326\3\0026&`4-X\10\20\0\0\0ServicesResolved\0\1b\0\0\0\0\0\0\0\0\0\37\0\0"
        b"\0org.freedesktop.DBus.Properties\0\0\0\0\0"
    )

    stream = io.BytesIO(bluez_interfaces_added_message)
    unmarshaller = Unmarshaller(stream)
    assert unmarshaller.unmarshall()
    message = unmarshaller.message
    assert message is not None
    assert message.body == [
        "/org/bluez/hci1/dev_58_2D_34_60_26_36",
        {
            "org.bluez.Device1": {
                "Adapter": Variant("o", "/org/bluez/hci1"),
                "Address": Variant("s", "58:2D:34:60:26:36"),
                "AddressType": Variant("s", "public"),
                "Alias": Variant("s", "Qingping Door/Window Sensor"),
                "Blocked": Variant("b", False),
                "Connected": Variant("b", False),
                "LegacyPairing": Variant("b", False),
                "Name": Variant("s", "Qingping Door/Window Sensor"),
                "Paired": Variant("b", False),
                "RSSI": Variant("n", -50),
                "ServiceData": Variant(
                    "a{sv}",
                    {
                        "0000fe95-0000-1000-8000-00805f9b34fb": Variant(
                            "ay", bytearray(b"0X\xd6\x03\x026&`4-X\x08")
                        )
                    },
                ),
                "ServicesResolved": Variant("b", False),
                "Trusted": Variant("b", False),
                "UUIDs": Variant("as", []),
            },
            "org.freedesktop.DBus.Introspectable": {},
            "org.freedesktop.DBus.Properties": {},
        },
    ]
    assert message.sender == ":1.4"
    assert message.path == "/"
    assert message.interface == "org.freedesktop.DBus.ObjectManager"
    assert message.member == "InterfacesAdded"
    assert message.signature == "oa{sa{sv}}"
    assert message.message_type == MessageType.SIGNAL
    assert message.flags == MessageFlag.NO_REPLY_EXPECTED
    assert message.serial == 1292951
    assert message.destination is None
    unpacked = unpack_variants(message.body)
    assert unpacked == [
        "/org/bluez/hci1/dev_58_2D_34_60_26_36",
        {
            "org.bluez.Device1": {
                "Adapter": "/org/bluez/hci1",
                "Address": "58:2D:34:60:26:36",
                "AddressType": "public",
                "Alias": "Qingping Door/Window Sensor",
                "Blocked": False,
                "Connected": False,
                "LegacyPairing": False,
                "Name": "Qingping Door/Window Sensor",
                "Paired": False,
                "RSSI": -50,
                "ServiceData": {
                    "0000fe95-0000-1000-8000-00805f9b34fb": bytearray(
                        b"0X\xd6\x03" b"\x026&`" b"4-X\x08"
                    )
                },
                "ServicesResolved": False,
                "Trusted": False,
                "UUIDs": [],
            },
            "org.freedesktop.DBus.Introspectable": {},
            "org.freedesktop.DBus.Properties": {},
        },
    ]


def test_unmarshall_bluez_interfaces_removed_message():
    bluez_interfaces_removed_message = (
        b'l\4\1\1\222\0\0\0\377@-\0~\0\0\0\1\1o\0\1\0\0\0/\0\0\0\0\0\0\0\2\1s\0"\0\0\0'
        b"org.freedesktop.DBus.ObjectManager\0\0\0\0\0\0\3\1s\0\21\0\0\0InterfacesRemoved"
        b"\0\0\0\0\0\0\0\10\1g\0\3oas\0\0\0\0\0\0\0\0\7\1s\0\5\0\0\0:1.12\0\0\0%\0\0\0"
        b"/org/bluez/hci0/dev_5F_13_47_38_26_55\0\0\0b\0\0\0\37\0\0\0org.freedesktop.DBus"
        b".Properties\0#\0\0\0org.freedesktop.DBus.Introspectable\0\21\0\0\0org.bluez.Dev"
        b"ice1\0"
    )

    stream = io.BytesIO(bluez_interfaces_removed_message)
    unmarshaller = Unmarshaller(stream)
    assert unmarshaller.unmarshall()
    message = unmarshaller.message
    assert message is not None
    assert message.body == [
        "/org/bluez/hci0/dev_5F_13_47_38_26_55",
        [
            "org.freedesktop.DBus.Properties",
            "org.freedesktop.DBus.Introspectable",
            "org.bluez.Device1",
        ],
    ]
    assert message.sender == ":1.12"
    assert message.path == "/"
    assert message.interface == "org.freedesktop.DBus.ObjectManager"
    assert message.member == "InterfacesRemoved"
    assert message.signature == "oas"
    assert message.message_type == MessageType.SIGNAL
    assert message.flags == MessageFlag.NO_REPLY_EXPECTED
    assert message.serial == 2965759
    assert message.destination is None
    unpacked = unpack_variants(message.body)
    assert unpacked == [
        "/org/bluez/hci0/dev_5F_13_47_38_26_55",
        [
            "org.freedesktop.DBus.Properties",
            "org.freedesktop.DBus.Introspectable",
            "org.bluez.Device1",
        ],
    ]


def test_unmarshall_bluez_properties_changed_with_service_data():
    bluez_properties_changed_message = (
        b"l\4\1\1\334\0\0\0@\236.\0\226\0\0\0\1\1o\0%\0\0\0/org/bluez/hci0/dev_58_2D_34_60_DA_1F"
        b"\0\0\0\2\1s\0\37\0\0\0org.freedesktop.DBus.Properties\0\3\1s\0\21\0\0\0PropertiesChanged"
        b"\0\0\0\0\0\0\0\10\1g\0\10sa{sv}as\0\0\0\7\1s\0\5\0\0\0:1.12\0\0\0\21\0\0\0org.bluez.Devi"
        b"ce1\0\0\0\270\0\0\0\0\0\0\0\4\0\0\0RSSI\0\1n\0\301\377\0\0\v\0\0\0ServiceData\0\5a{sv}"
        b"\0\0\210\0\0\0\0\0\0\0$\0\0\0000000fdcd-0000-1000-8000-00805f9b34fb\0\2ay\0\0\0\0\24\0"
        b"\0\0\10\22\37\332`4-X\2\1U\17\1\315\t\4\5\0\0\0$\0\0\0000000fe95-0000-1000-8000-00805f"
        b"9b34fb\0\2ay\0\0\0\0\f\0\0\0000X\203\n\2\37\332`4-X\10\0\0\0\0"
    )

    stream = io.BytesIO(bluez_properties_changed_message)
    unmarshaller = Unmarshaller(stream)
    assert unmarshaller.unmarshall()
    message = unmarshaller.message
    assert message is not None
    assert message.body == [
        "org.bluez.Device1",
        {
            "RSSI": Variant("n", -63),
            "ServiceData": Variant(
                "a{sv}",
                {
                    "0000fdcd-0000-1000-8000-00805f9b34fb": Variant(
                        "ay",
                        bytearray(
                            b"\x08\x12\x1f\xda`4-X\x02\x01U\x0f\x01\xcd\t\x04\x05\x00\x00\x00"
                        ),
                    ),
                    "0000fe95-0000-1000-8000-00805f9b34fb": Variant(
                        "ay", bytearray(b"0X\x83\n\x02\x1f\xda`4-X\x08")
                    ),
                },
            ),
        },
        [],
    ]
    assert message.sender == ":1.12"
    assert message.path == "/org/bluez/hci0/dev_58_2D_34_60_DA_1F"
    assert message.interface == "org.freedesktop.DBus.Properties"
    assert message.member == "PropertiesChanged"
    assert message.signature == "sa{sv}as"
    assert message.message_type == MessageType.SIGNAL
    assert message.flags == MessageFlag.NO_REPLY_EXPECTED
    assert message.serial == 3055168
    assert message.destination is None
    unpacked = unpack_variants(message.body)
    assert unpacked == [
        "org.bluez.Device1",
        {
            "RSSI": -63,
            "ServiceData": {
                "0000fdcd-0000-1000-8000-00805f9b34fb": bytearray(
                    b"\x08\x12\x1f\xda"
                    b"`4-X"
                    b"\x02\x01U\x0f"
                    b"\x01\xcd\t\x04"
                    b"\x05\x00\x00\x00"
                ),
                "0000fe95-0000-1000-8000-00805f9b34fb": bytearray(
                    b"0X\x83\n" b"\x02\x1f\xda`" b"4-X\x08"
                ),
            },
        },
        [],
    ]


def test_unmarshall_multiple_messages():
    """Test we can unmarshall multiple messages in a single packet."""
    multiple_message_packet = (
        b"l\4\1\0014\0\0\0J\27\230\0\225\0\0\0\1\1o\0%\0\0\0/org/bluez/hci0/dev_F0_B3_EC_15_7F_8E\0\0\0\2\1s\0\37\0\0\0"
        b"org.freedesktop.DBus.Properties\0\3\1s\0\21\0\0\0PropertiesChanged\0\0\0\0\0\0\0\10\1g\0\10sa{sv}as\0\0\0\7\1"
        b"s\0\4\0\0\0:1.4\0\0\0\0\21\0\0\0org.bluez.Device1\0\0\0\16\0\0\0\0\0\0\0\4\0\0\0RSSI\0\1n\0\264\377\0\0\0\0\0"
        b"\0l\4\1\0014\0\0\0K\27\230\0\225\0\0\0\1\1o\0%\0\0\0/org/bluez/hci0/dev_3F_70_98_0F_08_CB\0\0\0\2\1s\0\37\0\0"
        b"\0org.freedesktop.DBus.Properties\0\3\1s\0\21\0\0\0PropertiesChanged\0\0\0\0\0\0\0\10\1g\0\10sa{sv}as\0\0\0\7"
        b"\1s\0\4\0\0\0:1.4\0\0\0\0\21\0\0\0org.bluez.Device1\0\0\0\16\0\0\0\0\0\0\0\4\0\0\0RSSI\0\1n\0\260\377\0\0\0\0"
        b"\0\0l\4\1\0014\0\0\0L\27\230\0\225\0\0\0\1\1o\0%\0\0\0/org/bluez/hci0/dev_D8_35_67_A4_F5_A5\0\0\0\2\1s\0\37\0"
        b"\0\0org.freedesktop.DBus.Properties\0\3\1s\0\21\0\0\0PropertiesChanged\0\0\0\0\0\0\0\10\1g\0\10sa{sv}as\0\0\0"
        b"\7\1s\0\4\0\0\0:1.4\0\0\0\0\21\0\0\0org.bluez.Device1\0\0\0\16\0\0\0\0\0\0\0\4\0\0\0RSSI\0\1n\0\242\377\0\0\0"
        b"\0\0\0"
    )
    stream = io.BytesIO(multiple_message_packet)
    unmarshaller = Unmarshaller(stream)
    assert unmarshaller.unmarshall()
    message = unmarshaller.message
    assert message is not None
    unpacked = unpack_variants(message.body)
    assert unpacked == ["org.bluez.Device1", {"RSSI": -76}, []]

    unmarshaller.reset()
    assert unmarshaller.unmarshall()
    message = unmarshaller.message
    assert message is not None
    unpacked = unpack_variants(message.body)
    assert unpacked == ["org.bluez.Device1", {"RSSI": -80}, []]

    unmarshaller.reset()
    assert unmarshaller.unmarshall()
    message = unmarshaller.message
    assert message is not None
    unpacked = unpack_variants(message.body)
    assert unpacked == ["org.bluez.Device1", {"RSSI": -94}, []]

    unmarshaller.reset()
    with pytest.raises(EOFError):
        unmarshaller.unmarshall()


def test_ay_buffer():
    body = [bytes(10000)]
    msg = Message(path="/test", member="test", signature="ay", body=body)
    marshalled = msg._marshall(False)
    unmarshalled_msg = Unmarshaller(io.BytesIO(marshalled)).unmarshall()
    assert unmarshalled_msg.body[0] == body[0]


def tests_fallback_no_cython():
    assert FakeCython().compiled is False
