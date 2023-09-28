import io
import timeit

from dbus_fast._private.unmarshaller import Unmarshaller

bluez_passive_message = (
    b"l\1\0\1(\0\0\0F\1\0\0\255\0\0\0\1\1o\0:\0\0\0/org/bluez/hci0/dev_BD_24_6F_"
    b"85_AA_61/service001a/char001b\0\0\0\0\0\0\2\1s\0\35\0\0\0org.bluez.GattCha"
    b"racteristic1\0\0\0\3\1s\0\n\0\0\0WriteValue\0\0\0\0\0\0\6\1s\0\t\0\0\0org."
    b"bluez\0\0\0\0\0\0\0\10\1g\0\7aya{sv}\0\0\0\0\3\0\0\0\357\1w\0\30\0\0\0\0\0"
    b"\0\0\4\0\0\0type\0\1s\0\7\0\0\0command\0"
)


stream = io.BytesIO(bluez_passive_message)

unmarshaller = Unmarshaller(stream)


def unmarhsall_bluez_rssi_message():
    stream.seek(0)
    unmarshaller.unmarshall()


count = 3000000
time = timeit.Timer(unmarhsall_bluez_rssi_message).timeit(count)
print(f"Unmarshalling {count} bluetooth write value messages took {time} seconds")
