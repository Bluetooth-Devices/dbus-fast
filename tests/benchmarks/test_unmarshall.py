import io
import socket

from pytest_codspeed import BenchmarkFixture

from dbus_fast._private.unmarshaller import Unmarshaller
from dbus_fast.constants import MessageType
from dbus_fast.message import Message
from dbus_fast.signature import Variant

ITERATIONS = 1000

bluez_rssi_message_bytes = bytes.fromhex(
    "6c04010134000000e25389019500000001016f00250000002f6f72672f626c75657a2f686369302f6465"
    "765f30385f33415f46325f31455f32425f3631000000020173001f0000006f72672e667265656465736b"
    "746f702e444275732e50726f7065727469657300030173001100000050726f706572746965734368616e"
    "67656400000000000000080167000873617b73767d617300000007017300040000003a312e3400000000"
    "110000006f72672e626c75657a2e446576696365310000000e0000000000000004000000525353490001"
    "6e00a7ff000000000000"
)


def test_unmarshall_bluez_rssi_message(benchmark: BenchmarkFixture) -> None:
    stream = io.BytesIO(bluez_rssi_message_bytes * ITERATIONS)

    unmarshaller = Unmarshaller(stream)
    unmarshall = unmarshaller.unmarshall
    seek = stream.seek

    @benchmark
    def _():
        seek(0)
        for _ in range(ITERATIONS):
            unmarshall()


bluez_properties_message = (
    b"l\4\1\0014\0\0\0\16Q\16\0\225\0\0\0\1\1o\0%\0\0\0/org/bluez/hci2/dev_08_3A_F2_1E_28_89\0\0\0\2\1s\0\37\0\0\0"
    b"org.freedesktop.DBus.Properties\0\3\1s\0\21\0\0\0PropertiesChanged\0\0\0\0\0\0\0\10\1g\0\10sa{sv}as\0\0\0\7\1"
    b"s\0\4\0\0\0:1.5\0\0\0\0\21\0\0\0org.bluez.Device1\0\0\0\16\0\0\0\0\0\0\0\4\0\0\0RSSI\0\1n\0\242\377\0\0\0\0\0\0"
    b"l\4\1\1\220\0\0\0\17Q\16\0\225\0\0\0\1\1o\0%\0\0\0/org/bluez/hci2/dev_A4_C1_38_6E_9F_7C\0\0\0\2\1s\0\37\0\0\0"
    b"org.freedesktop.DBus.Properties\0\3\1s\0\21\0\0\0PropertiesChanged\0\0\0\0\0\0\0\10\1g\0\10sa{sv}as\0\0\0\7\1s"
    b"\0\4\0\0\0:1.5\0\0\0\0\21\0\0\0org.bluez.Device1\0\0\0k\0\0\0\0\0\0\0\4\0\0\0RSSI\0\1n\0\250\377\0\0\20\0\0\0"
    b"ManufacturerData\0\5a{qv}\0;\0\0\0\1\0\2ay\0\0\0\t\0\0\0\1\1\1\3\361\234\\\0\1\0\0\0L\0\2ay\0\0\0\27\0\0\0\2\25"
    b"INTELLI_ROCKS_HWPu\362\377\302\0\0\0\0\0l\4\1\0014\0\0\0\20Q\16\0\225\0\0\0\1\1o\0%\0\0\0/org/bluez/hci2/dev_F8"
    b"_04_2E_E1_9F_19\0\0\0\2\1s\0\37\0\0\0org.freedesktop.DBus.Properties\0\3\1s\0\21\0\0\0PropertiesChanged\0\0\0\0"
    b"\0\0\0\10\1g\0\10sa{sv}as\0\0\0\7\1s\0\4\0\0\0:1.5\0\0\0\0\21\0\0\0org.bluez.Device1\0\0\0\16\0\0\0\0\0\0\0\4\0"
    b"\0\0RSSI\0\1n\0\262\377\0\0\0\0\0\0l\4\1\0014\0\0\0\21Q\16\0\225\0\0\0\1\1o\0%\0\0\0/org/bluez/hci3/dev_54_E6_"
    b"1B_F0_20_97\0\0\0\2\1s\0\37\0\0\0org.freedesktop.DBus.Properties\0\3\1s\0\21\0\0\0PropertiesChanged\0\0\0\0\0\0"
    b"\0\10\1g\0\10sa{sv}as\0\0\0\7\1s\0\4\0\0\0:1.5\0\0\0\0\21\0\0\0org.bluez.Device1\0\0\0\16\0\0\0\0\0\0\0\4\0\0\0"
    b"RSSI\0\1n\0\254\377\0\0\0\0\0\0l\4\1\0014\0\0\0\22Q\16\0\225\0\0\0\1\1o\0%\0\0\0/org/bluez/hci3/dev_D8_EF_2F_41"
    b"_B1_34\0\0\0\2\1s\0\37\0\0\0org.freedesktop.DBus.Properties\0\3\1s\0\21\0\0\0PropertiesChanged\0\0\0\0\0\0\0\10"
    b"\1g\0\10sa{sv}as\0\0\0\7\1s\0\4\0\0\0:1.5\0\0\0\0\21\0\0\0org.bluez.Device1\0\0\0\16\0\0\0\0\0\0\0\4\0\0\0RSSI\0"
    b"\1n\0\244\377\0\0\0\0\0\0l\4\1\0014\0\0\0\23Q\16\0\225\0\0\0\1\1o\0%\0\0\0/org/bluez/hci3/dev_34_AB_95_85_66_6D\0"
    b"\0\0\2\1s\0\37\0\0\0org.freedesktop.DBus.Properties\0\3\1s\0\21\0\0\0PropertiesChanged\0\0\0\0\0\0\0\10\1g\0\10"
    b"sa{sv}as\0\0\0\7\1s\0\4\0\0\0:1.5\0\0\0\0\21\0\0\0org.bluez.Device1\0\0\0\16\0\0\0\0\0\0\0\4\0\0\0RSSI\0\1n\0\236"
    b"\377\0\0\0\0\0\0l\4\1\0014\0\0\0\24Q\16\0\225\0\0\0\1\1o\0%\0\0\0/org/bluez/hci3/dev_08_3A_F2_1E_32_69\0\0\0\2\1s"
    b"\0\37\0\0\0org.freedesktop.DBus.Properties\0\3\1s\0\21\0\0\0PropertiesChanged\0\0\0\0\0\0\0\10\1g\0\10sa{sv}as\0"
    b"\0\0\7\1s\0\4\0\0\0:1.5\0\0\0\0\21\0\0\0org.bluez.Device1\0\0\0\16\0\0\0\0\0\0\0\4\0\0\0RSSI\0\1n\0\246\377\0\0\0"
    b"\0\0\0l\4\1\0014\0\0\0\25Q\16\0\225\0\0\0\1\1o\0%\0\0\0/org/bluez/hci3/dev_34_AB_95_85_71_D1\0\0\0\2\1s\0\37\0\0\0"
    b"org.freedesktop.DBus.Properties\0\3\1s\0\21\0\0\0PropertiesChanged\0\0\0\0\0\0\0\10\1g\0\10sa{sv}as\0\0\0\7\1s\0\4"
    b"\0\0\0:1.5\0\0\0\0\21\0\0\0org.bluez.Device1\0\0\0\16\0\0\0\0\0\0\0\4\0\0\0RSSI\0\1n\0\232\377\0\0\0\0\0\0l\4\1\001"
    b"4\0\0\0\26Q\16\0\225\0\0\0\1\1o\0%\0\0\0/org/bluez/hci3/dev_F8_04_2E_E1_9F_19\0\0\0\2\1s\0\37\0\0\0org.freedesktop.D"
    b"Bus.Properties\0\3\1s\0\21\0\0\0PropertiesChanged\0\0\0\0\0\0\0\10\1g\0\10sa{sv}as\0\0\0\7\1s\0\4\0\0\0:1.5\0\0\0\0"
    b"\21\0\0\0org.bluez.Device1\0\0\0\16\0\0\0\0\0\0\0\4\0\0\0RSSI\0\1n\0\306\377\0\0\0\0\0\0"
)

# 9 messages per chunk
MESSAGES_PER_CHUNK = 9


def test_unmarshall_bluez_properties_message(benchmark: BenchmarkFixture) -> None:
    stream = io.BytesIO(bluez_properties_message * ITERATIONS)

    unmarshaller = Unmarshaller(stream)
    unmarshall = unmarshaller.unmarshall
    seek = stream.seek

    @benchmark
    def _():
        seek(0)
        for _ in range(ITERATIONS):
            unmarshall()


def test_unmarshall_multiple_bluez_properties_message(
    benchmark: BenchmarkFixture,
) -> None:
    stream = io.BytesIO(bluez_properties_message * ITERATIONS)

    unmarshaller = Unmarshaller(stream)
    unmarshall = unmarshaller.unmarshall
    seek = stream.seek

    @benchmark
    def _():
        seek(0)
        for _ in range(ITERATIONS * MESSAGES_PER_CHUNK):
            unmarshall()


def test_unmarshall_multiple_bluez_properties_message_socket(
    benchmark: BenchmarkFixture,
) -> None:
    sock1, sock2 = socket.socketpair()
    sock1.setblocking(False)
    sock2.setblocking(False)
    unmarshaller = Unmarshaller(None, sock1, False)
    unmarshall = unmarshaller.unmarshall
    send = sock2.send

    @benchmark
    def _():
        for _ in range(ITERATIONS):
            send(bluez_properties_message)
            for _ in range(MESSAGES_PER_CHUNK):
                unmarshall()

    sock1.close()
    sock2.close()


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


def test_unmarshall_bluez_interfaces_added_message(benchmark: BenchmarkFixture) -> None:
    stream = io.BytesIO(bluez_interfaces_added_message * ITERATIONS)

    unmarshaller = Unmarshaller(stream)
    unmarshall = unmarshaller.unmarshall
    seek = stream.seek

    @benchmark
    def _():
        seek(0)
        for _ in range(ITERATIONS):
            unmarshall()


def _build_systemd_list_units_message() -> bytes:
    """An array-of-structs reply, the shape systemd's ListUnits returns.

    Built via the marshaller once at import so the benchmark exercises the
    struct reader, which the BlueZ dict/array fixtures above never touch.
    """
    names = (
        "systemd-journald",
        "dbus",
        "NetworkManager",
        "sshd",
        "cron",
        "bluetooth",
        "polkit",
        "udev",
        "rsyslog",
        "getty@tty1",
        "user@1000",
        "accounts-daemon",
        "ModemManager",
        "thermald",
        "snapd",
    )
    units = [
        (
            f"{n}.service",
            f"{n} service daemon",
            "loaded",
            "active",
            "running",
            "",
            f"/org/freedesktop/systemd1/unit/{n}_2eservice",
            0,
            "",
            "/",
        )
        for n in names
    ]
    return bytes(
        Message(
            path="/org/freedesktop/systemd1",
            interface="org.freedesktop.systemd1.Manager",
            member="ListUnits",
            message_type=MessageType.METHOD_RETURN,
            reply_serial=1,
            signature="a(ssssssouso)",
            body=[units],
        )._marshall(False)
    )


systemd_list_units_message = _build_systemd_list_units_message()


def test_unmarshall_systemd_list_units_message(benchmark: BenchmarkFixture) -> None:
    stream = io.BytesIO(systemd_list_units_message * ITERATIONS)

    unmarshaller = Unmarshaller(stream)
    unmarshall = unmarshaller.unmarshall
    seek = stream.seek

    @benchmark
    def _():
        seek(0)
        for _ in range(ITERATIONS):
            unmarshall()


def _build_bluez_manufacturer_data_message() -> bytes:
    """A BLE advertisement PropertiesChanged carrying ManufacturerData.

    ManufacturerData is ``a{qv}`` (uint16 company id -> variant), the one
    dict shape with integer keys the unmarshaller inlines separately from
    the string-keyed ``a{sv}`` path, with ``ay`` byte-array values. The
    other BlueZ fixtures only reach it bundled behind eight RSSI-only
    messages, so a regression in that branch would be diluted out of range.
    """
    body = [
        "org.bluez.Device1",
        {
            "RSSI": Variant("n", -66),
            "ManufacturerData": Variant(
                "a{qv}",
                {
                    0x0075: Variant(
                        "ay", b"\x42\x04\x01\x01\x70\xd0\xc2\x4e\x08\xab\x57"
                    ),
                    0x004C: Variant("ay", b"\x02\x15\x49\x4e\x54\x45\x4c\x4c\x49"),
                },
            ),
        },
        [],
    ]
    return bytes(
        Message(
            path="/org/bluez/hci0/dev_D0_C2_4E_08_AB_57",
            interface="org.freedesktop.DBus.Properties",
            member="PropertiesChanged",
            message_type=MessageType.SIGNAL,
            signature="sa{sv}as",
            body=body,
        )._marshall(False)
    )


bluez_manufacturer_data_message = _build_bluez_manufacturer_data_message()


def test_unmarshall_bluez_manufacturer_data_message(
    benchmark: BenchmarkFixture,
) -> None:
    stream = io.BytesIO(bluez_manufacturer_data_message * ITERATIONS)

    unmarshaller = Unmarshaller(stream)
    unmarshall = unmarshaller.unmarshall
    seek = stream.seek

    @benchmark
    def _():
        seek(0)
        for _ in range(ITERATIONS):
            unmarshall()


def _build_bluez_service_data_message() -> bytes:
    """A BLE advertisement PropertiesChanged carrying ServiceData.

    ServiceData is the string-keyed counterpart to ManufacturerData: a
    ``Variant("a{sv}", {uuid_str: Variant("ay", bytes)})`` nested inside
    the outer ``a{sv}`` property dict, exercising the string-keyed dict
    fast path at two levels plus the ``ay`` variant unpack. The other
    BlueZ fixtures only reach this shape bundled behind eight RSSI-only
    messages, so a regression in the nested-a{sv}/ay-variant branch
    would be diluted out of range — the same dilution argument that
    motivated the dedicated ManufacturerData benchmark above.
    """
    body = [
        "org.bluez.Device1",
        {
            "RSSI": Variant("n", -72),
            "ServiceData": Variant(
                "a{sv}",
                {
                    "0000fe95-0000-1000-8000-00805f9b34fb": Variant(
                        "ay",
                        b"\x30\x58\xd6\x03\x02\x36\x26\x60\x34\x2d\x58\x08",
                    ),
                    "0000fdcd-0000-1000-8000-00805f9b34fb": Variant(
                        "ay",
                        b"\x08\x12\x1f\xda\x60\x34\x2d\x58\x02\x01\x55\x0f"
                        b"\x01\xcd\x09\x04\x05",
                    ),
                },
            ),
        },
        [],
    ]
    return bytes(
        Message(
            path="/org/bluez/hci0/dev_58_2D_34_60_DA_1F",
            interface="org.freedesktop.DBus.Properties",
            member="PropertiesChanged",
            message_type=MessageType.SIGNAL,
            signature="sa{sv}as",
            body=body,
        )._marshall(False)
    )


bluez_service_data_message = _build_bluez_service_data_message()


def test_unmarshall_bluez_service_data_message(
    benchmark: BenchmarkFixture,
) -> None:
    stream = io.BytesIO(bluez_service_data_message * ITERATIONS)

    unmarshaller = Unmarshaller(stream)
    unmarshall = unmarshaller.unmarshall
    seek = stream.seek

    @benchmark
    def _():
        seek(0)
        for _ in range(ITERATIONS):
            unmarshall()


def _build_bluez_interfaces_removed_message() -> bytes:
    """An ObjectManager.InterfacesRemoved signal carrying ``oas``.

    InterfacesRemoved fires whenever BlueZ tears down a device entry —
    a high-frequency event on a noisy 2.4 GHz channel. The body is an
    object path plus a bare ``as`` of interface names, so the hot path
    is the top-level string-array reader with several short-string
    allocations per message. None of the existing fixtures exercise
    ``as`` at the top level with non-empty entries (the ``as`` tail of
    ``sa{sv}as`` in PropertiesChanged is always empty in the BlueZ
    traffic), so a regression in the top-level string-array branch
    would not show up on CodSpeed without a dedicated benchmark.
    """
    body = [
        "/org/bluez/hci0/dev_5F_13_47_38_26_55",
        [
            "org.freedesktop.DBus.Properties",
            "org.freedesktop.DBus.Introspectable",
            "org.bluez.Device1",
        ],
    ]
    return bytes(
        Message(
            path="/",
            interface="org.freedesktop.DBus.ObjectManager",
            member="InterfacesRemoved",
            message_type=MessageType.SIGNAL,
            signature="oas",
            body=body,
        )._marshall(False)
    )


bluez_interfaces_removed_message = _build_bluez_interfaces_removed_message()


def test_unmarshall_bluez_interfaces_removed_message(
    benchmark: BenchmarkFixture,
) -> None:
    stream = io.BytesIO(bluez_interfaces_removed_message * ITERATIONS)

    unmarshaller = Unmarshaller(stream)
    unmarshall = unmarshaller.unmarshall
    seek = stream.seek

    @benchmark
    def _():
        seek(0)
        for _ in range(ITERATIONS):
            unmarshall()
