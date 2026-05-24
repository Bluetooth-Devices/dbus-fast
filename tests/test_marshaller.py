import io
import json
import os
import struct
from enum import Enum
from typing import Any

import pytest

from dbus_fast import Message, MessageFlag, MessageType, SignatureTree, Variant
from dbus_fast._private._cython_compat import FakeCython
from dbus_fast._private.constants import BIG_ENDIAN, LITTLE_ENDIAN
from dbus_fast._private.marshaller import Marshaller
from dbus_fast._private.unmarshaller import (
    MAX_CONTAINER_DEPTH,
    MAX_MESSAGE_SIZE,
    Unmarshaller,
    buffer_to_int16,
    buffer_to_uint16,
    buffer_to_uint32,
    is_compiled,
)
from dbus_fast.errors import InvalidMessageError
from dbus_fast.signature import SignatureType
from dbus_fast.unpack import unpack_variants


def test_bytearray_to_uint32_big_end():
    assert buffer_to_uint32(bytearray(b"\x01\x02\x03\x04"), 0, BIG_ENDIAN) == 16909060
    assert (
        buffer_to_uint32(
            bytearray((0xFFFFFFFF).to_bytes(4, byteorder="big", signed=False)),
            0,
            BIG_ENDIAN,
        )
        == 0xFFFFFFFF
    )


def test_bytearray_to_uint16_big_end():
    assert buffer_to_uint16(bytearray(b"\x01\x02"), 0, BIG_ENDIAN) == 258
    assert (
        buffer_to_uint16(
            bytearray((0xFFFF).to_bytes(2, byteorder="big", signed=False)),
            0,
            BIG_ENDIAN,
        )
        == 0xFFFF
    )


def test_bytearray_to_int16_big_end():
    assert buffer_to_int16(bytearray(b"\x01\x02"), 0, BIG_ENDIAN) == 258
    assert (
        buffer_to_int16(
            bytearray((32767).to_bytes(2, byteorder="big", signed=True)), 0, BIG_ENDIAN
        )
        == 32767
    )


@pytest.mark.skipif(not is_compiled(), reason="requires cython")
def test_bytearray_to_int16_big_end_signed():
    assert buffer_to_int16(bytearray(b"\xff\xff"), 0, BIG_ENDIAN) == -1
    assert (
        buffer_to_int16(
            bytearray((-32768).to_bytes(2, byteorder="big", signed=True)),
            0,
            BIG_ENDIAN,
        )
        == -32768
    )


def test_bytearray_to_uint32_little_end():
    assert (
        buffer_to_uint32(bytearray(b"\x01\x02\x03\x04"), 0, LITTLE_ENDIAN) == 67305985
    )
    assert (
        buffer_to_uint32(
            bytearray((0xFFFFFFFF).to_bytes(4, byteorder="little", signed=False)),
            0,
            LITTLE_ENDIAN,
        )
        == 0xFFFFFFFF
    )


def test_bytearray_to_uint16_little_end():
    assert buffer_to_uint16(bytearray(b"\x01\x02"), 0, LITTLE_ENDIAN) == 513
    assert (
        buffer_to_uint16(
            bytearray((0xFFFF).to_bytes(2, byteorder="little", signed=False)),
            0,
            LITTLE_ENDIAN,
        )
        == 0xFFFF
    )


def test_bytearray_to_int16_little_end():
    assert buffer_to_int16(bytearray(b"\x01\x02"), 0, LITTLE_ENDIAN) == 513
    assert (
        buffer_to_int16(
            bytearray((32767).to_bytes(2, byteorder="little", signed=True)),
            0,
            LITTLE_ENDIAN,
        )
        == 32767
    )


@pytest.mark.skipif(not is_compiled(), reason="requires cython")
def test_bytearray_to_int16_little_end_signed():
    assert buffer_to_int16(bytearray(b"\xff\xff"), 0, LITTLE_ENDIAN) == -1
    assert (
        buffer_to_int16(
            bytearray((-32768).to_bytes(2, byteorder="little", signed=True)),
            0,
            LITTLE_ENDIAN,
        )
        == -32768
    )


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

with open(os.path.dirname(__file__) + "/data/get_managed_objects.hex") as fp:
    get_managed_objects_msg = fp.read()


def json_to_message(message: dict[str, Any]) -> Message:
    copy = dict(message)
    if "message_type" in copy:
        copy["message_type"] = MessageType(copy["message_type"])
    if "flags" in copy:
        copy["flags"] = MessageFlag(copy["flags"])

    return Message(**copy)


# variants are an object in the json
def replace_variants(type_: SignatureType, item: Any) -> Any:
    if type_.token == "v" and type(item) is not Variant:
        item = Variant(
            item["signature"],
            replace_variants(SignatureTree(item["signature"]).types[0], item["value"]),
        )
    elif type_.token == "a":
        for i, item_child in enumerate(item):
            if type_.children[0].token == "{":
                assert type(item) is dict
                for k, v in item.items():
                    item[k] = replace_variants(type_.children[0].children[1], v)
            else:
                item[i] = replace_variants(type_.children[0], item_child)
    elif type_.token == "(":
        # tuples are immutable, so convert to list to modify then back
        tuple_as_list = list(item)

        for i, item_child in enumerate(tuple_as_list):
            if type_.children[0].token == "{":
                assert False
            else:
                tuple_as_list[i] = replace_variants(type_.children[i], item_child)

        item = tuple(tuple_as_list)

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
            print()
            print("mine:")
            print_buf(bytes(buf))
            print()
            print("theirs:")
            print_buf(data)

        assert buf == data


@pytest.mark.parametrize("unmarshall_table", (table,))
def test_unmarshalling_with_table(unmarshall_table):
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
            assert getattr(unmarshaller.message, attr) == getattr(message, attr), (
                f"attr doesnt match: {attr}"
            )


items: list[dict[str, Any]] = [
    {
        "message": {
            "destination": "org.freedesktop.DBus",
            "path": "/org/freedesktop/DBus",
            "interface": "org.freedesktop.DBus",
            "member": "Hello",
            "serial": 1,
            "signature": "a(uu)",
            "body": [[(1, 1), (2, 2)]],
        },
        "data": "6c01000118000000010000007b00000001016f00150000002f6f72672f667265656465736b746f702f4442757300000002017300140000006f72672e667265656465736b746f702e4442757300000000030173000500000048656c6c6f00000006017300140000006f72672e667265656465736b746f702e444275730000000008016700056128757529000000000000100000000000000001000000010000000200000002000000",
    },
    {
        "message": {
            "destination": "org.freedesktop.DBus",
            "path": "/org/freedesktop/DBus",
            "interface": "org.freedesktop.DBus",
            "member": "Hello",
            "serial": 1,
            "signature": "a(as(uu(a{ss})))",
            "body": [
                [
                    (["hello", "there"], (5, 6, ({"five": "six", "seven": "eight"},))),
                    (
                        ["to", "the", "world"],
                        (7, 8, ({"seven": "eight", "nine": "ten"},)),
                    ),
                ]
            ],
        },
        "data": "6c010001c4000000010000008600000001016f00150000002f6f72672f667265656465736b746f702f4442757300000002017300140000006f72672e667265656465736b746f702e4442757300000000030173000500000048656c6c6f00000006017300140000006f72672e667265656465736b746f702e444275730000000008016700106128617328757528617b73737d292929000000bc00000000000000160000000500000068656c6c6f0000000500000074686572650000000000000005000000060000002e0000000000000004000000666976650000000003000000736978000000000005000000736576656e0000000500000065696768740000001a00000002000000746f0000030000007468650005000000776f726c6400000007000000080000002c0000000000000005000000736576656e000000050000006569676874000000040000006e696e65000000000300000074656e00",
    },
]


@pytest.mark.parametrize("item", items)
def test_unmarshalling(item: dict[str, Any]) -> None:
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
        assert getattr(unmarshaller.message, attr) == getattr(message, attr), (
            f"attr doesnt match: {attr}"
        )


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
                        b"0X\xd6\x03\x026&`4-X\x08"
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
                    b"\x08\x12\x1f\xda`4-X\x02\x01U\x0f\x01\xcd\t\x04\x05\x00\x00\x00"
                ),
                "0000fe95-0000-1000-8000-00805f9b34fb": bytearray(
                    b"0X\x83\n\x02\x1f\xda`4-X\x08"
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

    assert unmarshaller.unmarshall()
    message = unmarshaller.message
    assert message is not None
    unpacked = unpack_variants(message.body)
    assert unpacked == ["org.bluez.Device1", {"RSSI": -80}, []]

    assert unmarshaller.unmarshall()
    message = unmarshaller.message
    assert message is not None
    unpacked = unpack_variants(message.body)
    assert unpacked == ["org.bluez.Device1", {"RSSI": -94}, []]

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


def test_unmarshall_large_message():
    stream = io.BytesIO(bytes.fromhex(get_managed_objects_msg))
    unmarshaller = Unmarshaller(stream)
    unmarshaller.unmarshall()
    message = unmarshaller.message
    unpacked = unpack_variants(message.body)
    objects = unpacked[0]
    assert objects["/org/bluez/hci0"] == {
        "org.bluez.Adapter1": {
            "Address": "00:1A:7D:DA:71:04",
            "AddressType": "public",
            "Alias": "homeassistant",
            "Class": 2883584,
            "Discoverable": False,
            "DiscoverableTimeout": 180,
            "Discovering": True,
            "Modalias": "usb:v1D6Bp0246d053F",
            "Name": "homeassistant",
            "Pairable": False,
            "PairableTimeout": 0,
            "Powered": True,
            "Roles": ["central", "peripheral"],
            "UUIDs": [
                "0000110e-0000-1000-8000-00805f9b34fb",
                "0000110a-0000-1000-8000-00805f9b34fb",
                "00001200-0000-1000-8000-00805f9b34fb",
                "0000110b-0000-1000-8000-00805f9b34fb",
                "00001108-0000-1000-8000-00805f9b34fb",
                "0000110c-0000-1000-8000-00805f9b34fb",
                "00001800-0000-1000-8000-00805f9b34fb",
                "00001801-0000-1000-8000-00805f9b34fb",
                "0000180a-0000-1000-8000-00805f9b34fb",
                "00001112-0000-1000-8000-00805f9b34fb",
            ],
        },
        "org.bluez.GattManager1": {},
        "org.bluez.LEAdvertisingManager1": {
            "ActiveInstances": 0,
            "SupportedIncludes": ["tx-power", "appearance", "local-name"],
            "SupportedInstances": 5,
        },
        "org.bluez.Media1": {},
        "org.bluez.NetworkServer1": {},
        "org.freedesktop.DBus.Introspectable": {},
        "org.freedesktop.DBus.Properties": {},
    }
    assert objects["/org/bluez/hci0/dev_CD_A3_FA_D1_50_56/service000b/char000c"] == {
        "org.bluez.GattCharacteristic1": {
            "Flags": ["read"],
            "Service": "/org/bluez/hci0/dev_CD_A3_FA_D1_50_56/service000b",
            "UUID": "e604e95d-a759-4817-87d3-aa005083a0d1",
            "Value": bytearray(b""),
        },
        "org.freedesktop.DBus.Introspectable": {},
        "org.freedesktop.DBus.Properties": {},
    }


def test_unmarshall_big_end_message():
    """Test we can unmarshall a big endian message."""
    msg = (
        b"B\x01\x00\x01\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x82"
        b"\x01\x01o\x00\x00\x00\x00\x01/\x00\x00\x00\x00\x00\x00\x00"
        b'\x02\x01s\x00\x00\x00\x00"org.freedesktop.DBus.ObjectManag'
        b"er\x00\x00\x00\x00\x00\x00\x03\x01s\x00\x00\x00\x00\x11GetManagedOb"
        b"jects\x00\x00\x00\x00\x00\x00\x00\x06\x01s\x00\x00\x00\x00\torg."
        b"bluez\x00\x00\x00\x00\x00\x00\x00\x08\x01g\x00\x04ussv\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00*\x00\x00\x00\x03zip\x00"
        b"\x00\x00\x00\x07Trusted\x00\x01b\x00\x00\x00\x00\x00\x01"
    )

    stream = io.BytesIO(msg)
    unmarshaller = Unmarshaller(stream)
    unmarshaller.unmarshall()
    message = unmarshaller.message
    unpacked = unpack_variants(message.body)
    assert unpacked == [42, "zip", "Trusted", True]


class RaucState(str, Enum):
    """Rauc slot states."""

    GOOD = "good"
    BAD = "bad"
    ACTIVE = "active"


def test_marshalling_enum():
    """Test marshalling an enum."""
    msg = Message(
        path="/test",
        member="test",
        signature="s",
        body=[RaucState.GOOD],
    )
    marshalled = msg._marshall(False)
    unmarshalled_msg = Unmarshaller(io.BytesIO(marshalled)).unmarshall()
    assert unpack_variants(unmarshalled_msg.body)[0] == RaucState.GOOD.value


def test_unmarshall_bluez_passive_message():
    """Test we can unmarshall a bluez passive message."""

    bluez_passive_message = (
        b"l\1\1\1*\0\0\0\205D\267\3\215\0\0\0\1\1o\0\35\0\0\0/org/bleak/61/281472597302272\0\0\0\6\1s\0\7\0\0"
        b"\0:1.1450\0\2\1s\0\37\0\0\0org.bluez.AdvertisementMonitor1\0\3\1s\0\v\0\0\0DeviceFound\0\0\0\0\0\10"
        b"\1g\0\1o\0\0\7\1s\0\4\0\0\0:1.4\0\0\0\0%\0\0\0/org/bluez/hci0/dev_58_D3_49_E6_02_6E\0l\1\1\1*\0\0\0"
        b"\206D\267\3\215\0\0\0\1\1o\0\35\0\0\0/org/bleak/61/281472593362560\0\0\0\6\1s\0\7\0\0\0:1.1450\0\2"
        b"\1s\0\37\0\0\0org.bluez.AdvertisementMonitor1\0\3\1s\0\v\0\0\0DeviceFound\0\0\0\0\0\10\1g\0\1o\0\0"
        b"\7\1s\0\4\0\0\0:1.4\0\0\0\0%\0\0\0/org/bluez/hci1/dev_58_D3_49_E6_02_6E\0"
    )

    stream = io.BytesIO(bluez_passive_message)
    unmarshaller = Unmarshaller(stream)
    unmarshaller.unmarshall()
    message = unmarshaller.message
    assert "/org/bluez/hci0/dev_58_D3_49_E6_02_6E" in str(message)
    unpacked = unpack_variants(message.body)
    assert unpacked == ["/org/bluez/hci0/dev_58_D3_49_E6_02_6E"]


def test_unmarshall_mount_message():
    """Test we mount message unmarshall."""

    mount_message = (
        b"l\1\0\1\30\1\0\0\213\1\0\0\266\0\0\0\1\1o\0\31\0\0\0/org/freedesktop/systemd1"
        b"\0\0\0\0\0\0\0\2\1s\0 \0\0\0org.freedesktop.systemd1.Manager\0\0\0\0\0\0\0\0"
        b"\3\1s\0\22\0\0\0StartTransientUnit\0\0\0\0\0\0\6\1s\0\30\0\0\0org.freedesktop"
        b".systemd1\0\0\0\0\0\0\0\0\10\1g\0\20ssa(sv)a(sa(sv))\0\0\0)\0\0\0mnt-data-sup"
        b"ervisor-mounts-test1234.mount\0\0\0\4\0\0\0fail\0\0\0\0\314\0\0\0\7\0\0\0Opti"
        b"ons\0\1s\0\0I\0\0\0noserverino,credentials=/mnt/data/supervisor/.mounts_crede"
        b"ntials/test1234\0\0\0\4\0\0\0Type\0\1s\0\4\0\0\0cifs\0\0\0\0\v\0\0\0Descripti"
        b"on\0\1s\0\0\37\0\0\0Supervisor cifs mount: test1234\0\4\0\0\0What\0\1s\0\v\0\0"
        b"\0//\303\274ber/test\0\0\0\0\0\0\0\0\0\0\0\0"
    )

    stream = io.BytesIO(mount_message)
    unmarshaller = Unmarshaller(stream)
    unmarshaller.unmarshall()
    message = unmarshaller.message
    assert unmarshaller.message.signature == "ssa(sv)a(sa(sv))"
    unpacked = unpack_variants(message.body)
    assert unpacked == [
        "mnt-data-supervisor-mounts-test1234.mount",
        "fail",
        [
            (
                "Options",
                "noserverino,credentials=/mnt/data/supervisor/.mounts_credentials/test1234",
            ),
            ("Type", "cifs"),
            ("Description", "Supervisor cifs mount: test1234"),
            ("What", "//über/tes"),
        ],
        [],
    ]


def test_unmarshall_mount_message_2():
    """Test we mount message unmarshall version 2."""

    mount_message = (
        b"l\1\0\1 \1\0\0+\6\0\0\266\0\0\0\1\1o\0\31\0\0\0/org/freedesktop/systemd1"
        b"\0\0\0\0\0\0\0\2\1s\0 \0\0\0org.freedesktop.systemd1.Manager\0\0\0\0\0\0"
        b"\0\0\3\1s\0\22\0\0\0StartTransientUnit\0\0\0\0\0\0\6\1s\0\30\0\0\0org.fr"
        b"eedesktop.systemd1\0\0\0\0\0\0\0\0\10\1g\0\20ssa(sv)a(sa(sv))\0\0\0(\0\0"
        b"\0mnt-data-supervisor-mounts-BadTest.mount\0\0\0\0\4\0\0\0fail\0\0\0\0\324"
        b"\0\0\0\7\0\0\0Options\0\1s\0\0H\0\0\0noserverino,credentials=/mnt/data/su"
        b"pervisor/.mounts_credentials/BadTest\0\0\0\0\4\0\0\0Type\0\1s\0\4\0\0\0cifs"
        b"\0\0\0\0\v\0\0\0Description\0\1s\0\0\36\0\0\0Supervisor cifs mount: BadTest"
        b"\0\0\4\0\0\0What\0\1s\0\23\0\0\0//doesntmatter/\303\274ber\0\0\0\0\0\0\0\0\0"
        b"\0\0\0"
    )

    stream = io.BytesIO(mount_message)
    unmarshaller = Unmarshaller(stream)
    unmarshaller.unmarshall()
    message = unmarshaller.message
    assert unmarshaller.message.signature == "ssa(sv)a(sa(sv))"
    unpacked = unpack_variants(message.body)
    assert unpacked == [
        "mnt-data-supervisor-mounts-BadTest.mount",
        "fail",
        [
            (
                "Options",
                "noserverino,credentials=/mnt/data/supervisor/.mounts_credentials/BadTest",
            ),
            ("Type", "cifs"),
            ("Description", "Supervisor cifs mount: BadTest"),
            ("What", "//doesntmatter/übe"),
        ],
        [],
    ]


def test_unmarshall_multi_byte_string():
    """Test unmarshall a multi-byte string."""

    mount_message = (
        b"l\x01\x00\x01\x1d\x00\x00\x00"
        b"\x01\x00\x00\x00x\x00\x00\x00"
        b"\x01\x01o\x00\x15\x00\x00\x00"
        b"/org/fre"
        b"edesktop"
        b"/DBus\x00\x00\x00"
        b"\x02\x01s\x00\x14\x00\x00\x00"
        b"org.free"
        b"desktop."
        b"DBus\x00\x00\x00\x00"
        b"\x03\x01s\x00\x05\x00\x00\x00"
        b"Hello\x00\x00\x00"
        b"\x06\x01s\x00\x14\x00\x00\x00"
        b"org.free"
        b"desktop."
        b"DBus\x00\x00\x00\x00"
        b"\x08\x01g\x00\x02as\x00"
        b"\x19\x00\x00\x00\x14\x00\x00\x00"
        b"//doesnt"
        b"matter/\xc3"
        b"\xbcber\x00"
    )

    stream = io.BytesIO(mount_message)
    unmarshaller = Unmarshaller(stream)
    unmarshaller.unmarshall()
    message = unmarshaller.message
    assert unmarshaller.message.signature == "as"
    unpacked = unpack_variants(message.body)
    assert unpacked == [["//doesntmatter/über"]]


def test_marshalling_struct_accepts_tuples():
    """Test marshalling a struct accepts tuples."""
    msg = Message(
        path="/test",
        member="test",
        signature="(s)",
        body=[(RaucState.GOOD,)],
    )
    marshalled = msg._marshall(False)
    unmarshalled_msg = Unmarshaller(io.BytesIO(marshalled)).unmarshall()
    assert unpack_variants(unmarshalled_msg.body)[0] == (RaucState.GOOD.value,)


def test_marshalling_struct_accepts_lists():
    """Test marshalling a struct accepts lists."""
    msg = Message(
        path="/test",
        member="test",
        signature="(s)",
        body=[[RaucState.GOOD]],
    )
    marshalled = msg._marshall(False)
    unmarshalled_msg = Unmarshaller(io.BytesIO(marshalled)).unmarshall()
    assert unpack_variants(unmarshalled_msg.body)[0] == (RaucState.GOOD.value,)


def _build_variant_message(variant: Variant) -> bytearray:
    """Build a minimal METHOD_RETURN message with a single variant body."""
    msg = Message(
        message_type=MessageType.METHOD_RETURN,
        reply_serial=1,
        signature="v",
        body=[variant],
    )
    return bytearray(msg._marshall(False))


def _truncate_body(data: bytearray, body_bytes: int) -> bytearray:
    """Truncate a message to keep only the first body_bytes of body data.

    Adjusts the body_len header field to match.
    """
    header_len = struct.unpack_from("<I", data, 12)[0]
    pad = (-header_len) & 7
    body_start = 16 + header_len + pad
    trunc = bytearray(data[: body_start + body_bytes])
    struct.pack_into("<I", trunc, 4, body_bytes)
    return trunc


@pytest.mark.skipif(not is_compiled(), reason="requires cython for bounds checks")
def test_read_variant_truncated_signature() -> None:
    """Truncating after the signature length byte should raise IndexError."""
    full = _build_variant_message(Variant("n", -89))
    # Body is: 01 6e 00 <padding> <int16>
    # Keep only 1 byte of body (just the signature_len byte)
    trunc = _truncate_body(full, 1)
    with pytest.raises(IndexError):
        Unmarshaller(io.BytesIO(bytes(trunc))).unmarshall()


@pytest.mark.skipif(not is_compiled(), reason="requires cython for bounds checks")
def test_read_variant_truncated_signature_no_null() -> None:
    """Truncating after the signature char but before null should raise."""
    full = _build_variant_message(Variant("n", -89))
    # Body is: 01 6e 00 <padding> <int16>
    # Keep only 2 bytes (signature_len + signature char, no null terminator)
    trunc = _truncate_body(full, 2)
    with pytest.raises(IndexError):
        Unmarshaller(io.BytesIO(bytes(trunc))).unmarshall()


@pytest.mark.skipif(not is_compiled(), reason="requires cython for bounds checks")
def test_read_variant_truncated_byte_value() -> None:
    """A byte variant truncated before its value should raise IndexError."""
    full = _build_variant_message(Variant("y", 42))
    # Body is: 01 79 00 2a (sig_len, 'y', null, value)
    # Keep only 3 bytes (signature complete, but no value byte)
    trunc = _truncate_body(full, 3)
    with pytest.raises(IndexError):
        Unmarshaller(io.BytesIO(bytes(trunc))).unmarshall()


def _forged_header(body_len: int, header_len: int, endian: str = "<") -> bytes:
    """Build a 16-byte header with attacker-chosen body_len and header_len."""
    endian_byte = b"l" if endian == "<" else b"B"
    header = bytearray(endian_byte + bytes([1, 0, 1]))
    header += struct.pack(f"{endian}I", body_len)
    header += struct.pack(f"{endian}I", 1)
    header += struct.pack(f"{endian}I", header_len)
    return bytes(header)


def test_unmarshall_rejects_oversized_body_len() -> None:
    """body_len above the 128 MiB cap raises before any body read."""
    forged = _forged_header(body_len=MAX_MESSAGE_SIZE + 1, header_len=0)
    with pytest.raises(InvalidMessageError, match="exceeds maximum"):
        Unmarshaller(io.BytesIO(forged)).unmarshall()


def test_unmarshall_rejects_oversized_header_len() -> None:
    """header_len above the 128 MiB cap raises before any body read."""
    forged = _forged_header(body_len=0, header_len=MAX_MESSAGE_SIZE + 1)
    with pytest.raises(InvalidMessageError, match="exceeds maximum"):
        Unmarshaller(io.BytesIO(forged)).unmarshall()


def test_unmarshall_rejects_oversized_combined_size() -> None:
    """body_len + header_len above the cap raises even when each is in range."""
    half = MAX_MESSAGE_SIZE // 2 + 1
    forged = _forged_header(body_len=half, header_len=half)
    with pytest.raises(InvalidMessageError, match="exceeds maximum"):
        Unmarshaller(io.BytesIO(forged)).unmarshall()


def test_unmarshall_rejects_max_uint32_body_len_big_endian() -> None:
    """A forged big-endian header with body_len=0xFFFFFFFF raises."""
    forged = _forged_header(body_len=0xFFFFFFFF, header_len=0, endian=">")
    with pytest.raises(InvalidMessageError, match="exceeds maximum"):
        Unmarshaller(io.BytesIO(forged)).unmarshall()


@pytest.mark.parametrize("message_type", [0, 5, 255])
def test_unmarshall_rejects_unknown_message_type(message_type: int) -> None:
    """A header carrying a message-type byte outside 1-4 raises InvalidMessageError."""
    header = bytearray(b"l" + bytes([message_type, 0, 1]))
    header += struct.pack("<I", 0)  # body_len
    header += struct.pack("<I", 1)  # serial
    header += struct.pack("<I", 0)  # header_len
    with pytest.raises(InvalidMessageError, match="unknown message type"):
        Unmarshaller(io.BytesIO(bytes(header))).unmarshall()


def _replace_body(template: bytearray, new_body: bytes) -> bytes:
    """Swap a `v`-signature message's body bytes and fix up body_len."""
    header_len = struct.unpack_from("<I", template, 12)[0]
    pad = (-header_len) & 7
    body_start = 16 + header_len + pad
    result = bytearray(template[:body_start])
    result.extend(new_body)
    struct.pack_into("<I", result, 4, len(new_body))
    return bytes(result)


def _nested_variant_body(depth: int) -> bytes:
    """Wire bytes for `depth` levels of variant-in-variant ending in a 'y' byte."""
    return (b"\x01v\x00" * (depth - 1)) + b"\x01y\x00\x01"


def _build_nested_variant_message(depth: int) -> bytes:
    template = _build_variant_message(Variant("y", 1))
    return _replace_body(template, _nested_variant_body(depth))


def test_unmarshall_accepts_variant_nesting_at_cap() -> None:
    """A message right at the cap depth must still parse."""
    data = _build_nested_variant_message(MAX_CONTAINER_DEPTH)
    msg = Unmarshaller(io.BytesIO(data)).unmarshall()
    assert msg is not None
    # Walk to the innermost byte to confirm full parse.
    inner = msg.body[0]
    for _ in range(MAX_CONTAINER_DEPTH - 1):
        inner = inner.value
    assert inner.value == 1


def test_unmarshall_rejects_variant_nesting_above_cap() -> None:
    """One past the cap raises InvalidMessageError before the stack blows."""
    data = _build_nested_variant_message(MAX_CONTAINER_DEPTH + 1)
    with pytest.raises(InvalidMessageError, match="container nesting exceeds maximum"):
        Unmarshaller(io.BytesIO(data)).unmarshall()


def test_unmarshall_rejects_deeply_nested_variant_dos() -> None:
    """A million levels of variant-in-variant must be rejected, not crash."""
    data = _build_nested_variant_message(1_000_000)
    with pytest.raises(InvalidMessageError, match="container nesting exceeds maximum"):
        Unmarshaller(io.BytesIO(data)).unmarshall()


def test_unmarshall_accepts_many_sibling_variants() -> None:
    """Many variants at the same depth must not trip the cap (siblings, not nested)."""
    entries = {f"k{i}": Variant("y", i & 0xFF) for i in range(MAX_CONTAINER_DEPTH * 4)}
    msg = Message(
        message_type=MessageType.METHOD_RETURN,
        reply_serial=1,
        signature="a{sv}",
        body=[entries],
    )
    marshalled = msg._marshall(False)
    result = Unmarshaller(io.BytesIO(marshalled)).unmarshall()
    assert result is not None
    assert len(result.body[0]) == len(entries)


def test_unmarshall_depth_counter_resets_between_messages() -> None:
    """Two cap-depth messages back-to-back must both parse on the same unmarshaller."""
    data1 = _build_nested_variant_message(MAX_CONTAINER_DEPTH)
    data2 = _build_nested_variant_message(MAX_CONTAINER_DEPTH)
    stream = io.BytesIO(data1 + data2)
    unmarshaller = Unmarshaller(stream)
    assert unmarshaller.unmarshall() is not None
    assert unmarshaller.unmarshall() is not None


def _nested_variants_then_signature(outer_count: int, inner_signature: bytes) -> bytes:
    """`outer_count` 'v' variant levels then a final variant carrying `inner_signature`.

    The final variant's value bytes are intentionally omitted; the per-reader
    depth check raises before any value bytes are read.
    """
    body = bytearray()
    for _ in range(outer_count):
        body.extend(b"\x01v\x00")
    body.append(len(inner_signature))
    body.extend(inner_signature)
    body.append(0)  # null terminator
    return bytes(body)


def test_unmarshall_rejects_struct_nesting_above_cap() -> None:
    """64 'v' levels wrapping a struct trips read_struct's depth check."""
    template = _build_variant_message(Variant("y", 1))
    inner_body = _nested_variants_then_signature(MAX_CONTAINER_DEPTH - 1, b"(y)")
    data = _replace_body(template, inner_body)
    with pytest.raises(InvalidMessageError, match="container nesting exceeds maximum"):
        Unmarshaller(io.BytesIO(data)).unmarshall()


def test_unmarshall_rejects_array_nesting_above_cap() -> None:
    """64 'v' levels wrapping an array trips read_array's depth check."""
    template = _build_variant_message(Variant("y", 1))
    inner_body = _nested_variants_then_signature(MAX_CONTAINER_DEPTH - 1, b"ay")
    data = _replace_body(template, inner_body)
    with pytest.raises(InvalidMessageError, match="container nesting exceeds maximum"):
        Unmarshaller(io.BytesIO(data)).unmarshall()


def test_unmarshall_rejects_dict_entry_nesting_above_cap() -> None:
    """64 'v' levels wrapping a {sv} dict entry trips read_dict_entry's depth check."""
    # `{sv}` parses as a top-level signature, so wrapping it in variants routes
    # the deepest dispatch through self._readers["{"] = read_dict_entry rather
    # than the inline `{` handling in read_array.
    template = _build_variant_message(Variant("y", 1))
    inner_body = _nested_variants_then_signature(MAX_CONTAINER_DEPTH - 1, b"{sv}")
    data = _replace_body(template, inner_body)
    with pytest.raises(InvalidMessageError, match="container nesting exceeds maximum"):
        Unmarshaller(io.BytesIO(data)).unmarshall()


def test_unmarshall_accepts_variant_of_dict_entry() -> None:
    """A variant carrying a `{sv}` dict entry exercises read_dict_entry's success path."""
    # Variant._construct rejects `{sv}` as a top-level signature, so we forge
    # the body bytes directly. Routes the deepest dispatch through
    # self._readers["{"] = read_dict_entry instead of read_array's inline path.
    template = _build_variant_message(Variant("y", 1))
    header_len = struct.unpack_from("<I", template, 12)[0]
    body_start = 16 + header_len + ((-header_len) & 7)

    new_body = bytearray(b"\x04{sv}\x00")  # variant header for `{sv}`
    align_pad = (-(body_start + len(new_body))) & 7
    new_body.extend(b"\x00" * align_pad)
    new_body.extend(struct.pack("<I", 1))  # key length
    new_body.extend(b"k\x00")  # key chars + null
    new_body.extend(b"\x01y\x00\x07")  # value variant of 'y' = 7

    data = _replace_body(template, bytes(new_body))
    msg = Unmarshaller(io.BytesIO(data)).unmarshall()
    assert msg is not None
    outer = msg.body[0]
    assert outer.signature == "{sv}"
    key, value = outer.value
    assert key == "k"
    assert value.signature == "y"
    assert value.value == 7


def test_marshaller_write_dict_entry_matches_array_path() -> None:
    """The public write_dict_entry delegate writes the same bytes as the array path."""
    dict_entry_type = SignatureTree("a{sv}").types[0].children[0]
    full = Marshaller("a{sv}", [{"k": Variant("s", "v")}]).marshall()

    # marshall() returns the live buffer; an empty signature leaves it empty, so
    # write_dict_entry's appends are observable without reaching into the cdef
    # _buf attribute (which is not Python-accessible in the Cython build).
    marshaller = Marshaller("", [])
    buf = marshaller.marshall()
    written = marshaller.write_dict_entry(["k", Variant("s", "v")], dict_entry_type)

    # full array = 4-byte length + 4-byte alignment pad + dict-entry bytes
    assert bytes(buf) == bytes(full[8:])
    assert written == len(full) - 8
