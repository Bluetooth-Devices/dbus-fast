import io
import socket

from pytest_codspeed import BenchmarkFixture

from dbus_fast._private.unmarshaller import Unmarshaller


def test_unmarshall_bluez_rssi_message(benchmark: BenchmarkFixture) -> None:
    bluez_rssi_message = (
        "6c04010134000000e25389019500000001016f00250000002f6f72672f626c75657a2f686369302f6465"
        "765f30385f33415f46325f31455f32425f3631000000020173001f0000006f72672e667265656465736b"
        "746f702e444275732e50726f7065727469657300030173001100000050726f706572746965734368616e"
        "67656400000000000000080167000873617b73767d617300000007017300040000003a312e3400000000"
        "110000006f72672e626c75657a2e446576696365310000000e0000000000000004000000525353490001"
        "6e00a7ff000000000000"
    )

    stream = io.BytesIO(bytes.fromhex(bluez_rssi_message))

    unmarshaller = Unmarshaller(stream)

    @benchmark
    def unmarhsall_bluez_rssi_message():
        stream.seek(0)
        unmarshaller.unmarshall()


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


def test_unmarshall_bluez_properties_message(benchmark: BenchmarkFixture) -> None:
    stream = io.BytesIO(bluez_properties_message)

    unmarshaller = Unmarshaller(stream)

    @benchmark
    def unmarshall_bluez_properties_message():
        stream.seek(0)
        unmarshaller.unmarshall()


def test_unmarshall_multiple_bluez_properties_message(
    benchmark: BenchmarkFixture,
) -> None:
    stream = io.BytesIO(bluez_properties_message)

    unmarshaller = Unmarshaller(stream)

    @benchmark
    def unmarshall_bluez_properties_message():
        stream.seek(0)
        for _ in range(9):
            unmarshaller.unmarshall()


def test_unmarshall_multiple_bluez_properties_message_socket(
    benchmark: BenchmarkFixture,
) -> None:
    sock1, sock2 = socket.socketpair()
    sock1.setblocking(False)
    sock2.setblocking(False)
    unmarshaller = Unmarshaller(None, sock1, False)

    @benchmark
    def unmarshall_bluez_properties_message():
        sock2.send(bluez_properties_message)
        for _ in range(9):
            unmarshaller.unmarshall()

    sock1.close()
    sock2.close()
