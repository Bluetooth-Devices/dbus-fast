import timeit

from dbus_fast import Message

message = Message(
    destination="org.bluez",
    path="/",
    interface="org.freedesktop.DBus.ObjectManager",
    member="GetManagedObjects",
)


def marhsall_bluez_get_managed_objects_message():
    message._marshall()


count = 1000000
time = timeit.Timer(marhsall_bluez_get_managed_objects_message).timeit(count)
print(f"Marshalling {count} bluez get managed objects messages took {time} seconds")
