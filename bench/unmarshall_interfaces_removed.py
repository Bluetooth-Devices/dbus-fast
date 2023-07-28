import io
import timeit

from dbus_fast._private.unmarshaller import Unmarshaller

#  cythonize -X language_level=3 -a -i  src/dbus_fast/_private/unmarshaller.py


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


def unmarshall_interfaces_removed_message():
    stream.seek(0)
    unmarshaller.next_message()
    unmarshaller.unmarshall()


count = 3000000
time = timeit.Timer(unmarshall_interfaces_removed_message).timeit(count)
print(f"Unmarshalling {count} bluetooth InterfacesRemoved messages took {time} seconds")
