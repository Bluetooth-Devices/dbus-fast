import io
import timeit

from dbus_fast._private.unmarshaller import Unmarshaller

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


stream = io.BytesIO(bluez_properties_message)

unmarshaller = Unmarshaller(stream)


def unmarhsall_bluez_rssi_message():
    stream.seek(0)
    unmarshaller.reset()
    unmarshaller.unmarshall()


count = 3000000
time = timeit.Timer(unmarhsall_bluez_rssi_message).timeit(count)
print(
    f"Unmarshalling {count} bluetooth properties changed messages took {time} seconds"
)
