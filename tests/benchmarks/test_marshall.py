from pytest_codspeed import BenchmarkFixture

from dbus_fast import Message
from dbus_fast.constants import MessageType
from dbus_fast.signature import Variant

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


def _build_get_all_reply() -> Message:
    """A GetAll reply (a{sv}), the flat dict shape property reads return."""
    props = {
        "Address": Variant("s", "AA:BB:CC:DD:EE:FF"),
        "AddressType": Variant("s", "public"),
        "Name": Variant("s", "Living Room Speaker"),
        "Alias": Variant("s", "Living Room Speaker"),
        "Class": Variant("u", 2360344),
        "Appearance": Variant("q", 0),
        "Icon": Variant("s", "audio-card"),
        "Paired": Variant("b", True),
        "Trusted": Variant("b", True),
        "Blocked": Variant("b", False),
        "LegacyPairing": Variant("b", False),
        "RSSI": Variant("n", -64),
        "Connected": Variant("b", True),
        "UUIDs": Variant("as", ["0000110b-0000-1000-8000-00805f9b34fb"]),
        "Adapter": Variant("o", "/org/bluez/hci0"),
        "ServicesResolved": Variant("b", True),
    }
    return Message(
        message_type=MessageType.METHOD_RETURN,
        reply_serial=1,
        signature="a{sv}",
        body=[props],
    )


get_all_reply = _build_get_all_reply()


def test_marshall_get_all_reply(benchmark: BenchmarkFixture) -> None:
    _marshall = get_all_reply._marshall

    @benchmark
    def _():
        for _ in range(ITERATIONS):
            _marshall(False)


def _build_get_managed_objects_reply() -> Message:
    """A GetManagedObjects reply (a{oa{sa{sv}}}), BlueZ's nested dict shape."""
    objects = {
        f"/org/bluez/hci0/dev_AA_BB_CC_DD_EE_{i:02X}": {
            "org.bluez.Device1": {
                "Address": Variant("s", f"AA:BB:CC:DD:EE:{i:02X}"),
                "AddressType": Variant("s", "public"),
                "Name": Variant("s", f"Device {i}"),
                "Alias": Variant("s", f"Device {i}"),
                "Paired": Variant("b", False),
                "Trusted": Variant("b", False),
                "Blocked": Variant("b", False),
                "Connected": Variant("b", False),
                "RSSI": Variant("n", -60 - i),
                "Adapter": Variant("o", "/org/bluez/hci0"),
                "UUIDs": Variant("as", []),
            }
        }
        for i in range(16)
    }
    return Message(
        message_type=MessageType.METHOD_RETURN,
        reply_serial=1,
        signature="a{oa{sa{sv}}}",
        body=[objects],
    )


get_managed_objects_reply = _build_get_managed_objects_reply()


def test_marshall_get_managed_objects_reply(benchmark: BenchmarkFixture) -> None:
    _marshall = get_managed_objects_reply._marshall

    @benchmark
    def _():
        for _ in range(ITERATIONS):
            _marshall(False)
