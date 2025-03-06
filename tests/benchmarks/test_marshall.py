from pytest_codspeed import BenchmarkFixture

from dbus_fast import Message

message = Message(
    destination="org.bluez",
    path="/",
    interface="org.freedesktop.DBus.ObjectManager",
    member="GetManagedObjects",
)


def test_marshall_bluez_get_managed_objects_message(
    benchmark: BenchmarkFixture,
) -> None:
    @benchmark
    def marhsall_bluez_get_managed_objects_message():
        message._marshall(False)
