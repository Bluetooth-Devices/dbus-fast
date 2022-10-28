import io
import timeit

from dbus_fast._private.unmarshaller import Unmarshaller

#  cythonize -X language_level=3 -a -i  src/dbus_fast/_private/unmarshaller.py


bluez_mfr_data_message = (
    b"l\4\1\1x\0\0\0\232\312\n\0\225\0\0\0\1\1o\0%\0\0\0/org/bluez/hci0/dev_D0_C2_4E_08_AB_57\0\0\0\2\1s"
    b"\0\37\0\0\0org.freedesktop.DBus.Properties\0\3\1s\0\21\0\0\0PropertiesChanged\0\0\0\0\0\0\0\10\1g\0"
    b"\10sa{sv}as\0\0\0\7\1s\0\4\0\0\0:1.4\0\0\0\0\21\0\0\0org.bluez.Device1\0\0\0T\0\0\0\0\0\0\0\4\0\0\0"
    b"RSSI\0\1n\0\252\377\0\0\20\0\0\0ManufacturerData\0\5a{qv}\0$\0\0\0u\0\2ay\0\0\0\30\0\0\0B\4\1\1p\320"
    b"\302N\10\253W\322\302N\10\253V\1\0\0\0\0\0\0\0\0\0\0l\4\1\0014\0\0\0\233\312\n\0\225\0\0\0\1\1o\0%\0"
    b"\0\0/org/bluez/hci0/dev_FF_D8_66_58_A5_7C\0\0\0\2\1s\0\37\0\0\0org.freedesktop.DBus.Properties\0\3\1s"
    b"\0\21\0\0\0PropertiesChanged\0\0\0\0\0\0\0\10\1g\0\10sa{sv}as\0\0\0\7\1s\0\4\0\0\0:1.4\0\0\0\0\21\0\0"
    b"\0org.bluez.Device1\0\0\0\16\0\0\0\0\0\0\0\4\0\0\0RSSI\0\1n\0\320\377\0\0\0\0\0\0l\4\1\0014\0\0\0\234"
    b"\312\n\0\225\0\0\0\1\1o\0%\0\0\0/org/bluez/hci0/dev_B4_E8_42_DB_56_5B\0\0\0\2\1s\0\37\0\0\0org.freede"
    b"sktop.DBus.Properties\0\3\1s\0\21\0\0\0PropertiesChanged\0\0\0\0\0\0\0\10\1g\0\10sa{sv}as\0\0\0\7\1s"
    b"\0\4\0\0\0:1.4\0\0\0\0\21\0\0\0org.bluez.Device1\0\0\0\16\0\0\0\0\0\0\0\4\0\0\0RSSI\0\1n\0\246\377\0"
    b"\0\0\0\0\0l\4\1\0014\0\0\0\235\312\n\0\225\0\0\0\1\1o\0%\0\0\0/org/bluez/hci0/dev_3F_70_98_0F_08_CB\0"
    b"\0\0\2\1s\0\37\0\0\0org.freedesktop.DBus.Properties\0\3\1s\0\21\0\0\0PropertiesChanged\0\0\0\0\0\0\0"
    b"\10\1g\0\10sa{sv}as\0\0\0\7\1s\0\4\0\0\0:1.4\0\0\0\0\21\0\0\0org.bluez.Device1\0\0\0\16\0\0\0\0\0\0"
    b"\0\4\0\0\0RSSI\0\1n\0\256\377\0\0\0\0\0\0"
)

stream = io.BytesIO(bluez_mfr_data_message)

unmarshaller = Unmarshaller(stream)


def unmarshall_mfr_data_message():
    stream.seek(0)
    unmarshaller.reset()
    unmarshaller.unmarshall()


count = 3000000
time = timeit.Timer(unmarshall_mfr_data_message).timeit(count)
print(f"Unmarshalling {count} bluetooth ManufacturerData messages took {time} seconds")
