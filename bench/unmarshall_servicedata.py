import io
import timeit

from dbus_fast._private.unmarshaller import Unmarshaller

#  cythonize -X language_level=3 -a -i  src/dbus_fast/_private/unmarshaller.py


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


def unmarshall_properties_changed_message():
    stream.seek(0)
    unmarshaller.unmarshall()


count = 3000000
time = timeit.Timer(unmarshall_properties_changed_message).timeit(count)
print(f"Unmarshalling {count} bluetooth PropertiesChanged messages took {time} seconds")
