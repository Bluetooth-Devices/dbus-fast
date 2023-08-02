import io
import timeit

from dbus_fast._private.unmarshaller import Unmarshaller

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


def unmarhsall_bluez_rssi_message():
    stream.seek(0)
    unmarshaller.unmarshall()
    unmarshaller.unmarshall()


count = 3000000
time = timeit.Timer(unmarhsall_bluez_rssi_message).timeit(count)
print(f"Unmarshalling {count} bluetooth passive messages took {time} seconds")
