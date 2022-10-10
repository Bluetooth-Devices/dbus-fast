import io
import timeit

from dbus_fast._private.unmarshaller import Unmarshaller

#  cythonize -X language_level=3 -a -i  src/dbus_fast/_private/unmarshaller.py


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


def unmarhsall_bluez_rssi_message():
    stream.seek(0)
    unmarshaller.reset()
    unmarshaller.unmarshall()


count = 3000000
time = timeit.Timer(unmarhsall_bluez_rssi_message).timeit(count)
print(f"Unmarshalling {count} bluetooth rssi messages took {time} seconds")
