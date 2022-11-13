import io
import timeit

from dbus_fast import unpack_variants
from dbus_fast._private.unmarshaller import Unmarshaller

# cythonize -X language_level=3 -a -i  src/dbus_fast/unpack.py

with open("tests/data/get_managed_objects.hex") as fp:
    msg = fp.read()


stream = io.BytesIO(bytes.fromhex(msg))

unmarshaller = Unmarshaller(stream)
message = unmarshaller.unmarshall()


def unpack_managed_objects():
    unpack_variants(message.body)


count = 30000
time = timeit.Timer(unpack_managed_objects).timeit(count)
print(f"Unpacked {count} get managed objects messages took {time} seconds")
