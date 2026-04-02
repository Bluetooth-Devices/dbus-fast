from pytest_codspeed import BenchmarkFixture

from dbus_fast import Message

ITERATIONS = 1000

message = Message(
    destination="org.bluez",
    path="/",
    interface="org.freedesktop.DBus.ObjectManager",
    member="GetManagedObjects",
)


def test_marshall_bluez_get_managed_objects_message(
    benchmark: BenchmarkFixture,
) -> None:
    _marshall = message._marshall

    @benchmark
    def _():
        for _ in range(ITERATIONS):
            _marshall(False)
