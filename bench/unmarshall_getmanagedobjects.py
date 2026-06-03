import io
import timeit
from pathlib import Path

from dbus_fast._private.unmarshaller import Unmarshaller

#  cythonize -X language_level=3 -a -i  src/dbus_fast/_private/unmarshaller.py

with Path("tests/data/get_managed_objects.hex").open() as fp:
    msg = fp.read()


stream = io.BytesIO(bytes.fromhex(msg))

unmarshaller = Unmarshaller(stream)


def unmarhsall_bluez_get_managed_objects_message():
    stream.seek(0)
    unmarshaller.unmarshall()


count = 10000
time = timeit.Timer(unmarhsall_bluez_get_managed_objects_message).timeit(count)
print(f"Unmarshalling {count} bluetooth GetManagedObjects messages took {time} seconds")
