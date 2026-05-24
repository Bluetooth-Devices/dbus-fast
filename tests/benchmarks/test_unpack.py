from pytest_codspeed import BenchmarkFixture

from dbus_fast import Variant, unpack_variants

ITERATIONS = 1000

bluez_managed_objects = {
    "/org/bluez/hci0": {
        "org.bluez.Adapter1": {
            "Address": Variant("s", "00:E0:4C:2A:25:63"),
            "AddressType": Variant("s", "public"),
            "Alias": Variant("s", "BlueZ 5.63"),
            "Class": Variant("u", 2883584),
            "Discoverable": Variant("b", False),
            "DiscoverableTimeout": Variant("u", 180),
            "Discovering": Variant("b", True),
            "Modalias": Variant("s", "usb:v1D6Bp0246d053F"),
            "Name": Variant("s", "BlueZ 5.63"),
            "Pairable": Variant("b", False),
            "PairableTimeout": Variant("u", 0),
            "Powered": Variant("b", True),
            "Roles": Variant("as", ["central", "peripheral"]),
            "UUIDs": Variant(
                "as",
                [
                    "0000110e-0000-1000-8000-00805f9b34fb",
                    "0000110a-0000-1000-8000-00805f9b34fb",
                    "00001200-0000-1000-8000-00805f9b34fb",
                ],
            ),
        },
        "org.bluez.GattManager1": {},
        "org.freedesktop.DBus.Properties": {},
    },
}

# An array-of-structs reply, the shape systemd's ListUnits returns. The BlueZ
# managed-objects fixture above is all dicts and never reaches the tuple branch
# of _unpack_variants; this one does.
_names = (
    "systemd-journald",
    "dbus",
    "NetworkManager",
    "sshd",
    "cron",
    "bluetooth",
    "polkit",
    "udev",
    "rsyslog",
    "getty@tty1",
    "user@1000",
    "accounts-daemon",
    "ModemManager",
    "thermald",
    "snapd",
)
systemd_list_units = [
    (
        f"{n}.service",
        f"{n} service daemon",
        "loaded",
        "active",
        "running",
        "",
        f"/org/freedesktop/systemd1/unit/{n}_2eservice",
        0,
        "",
        "/",
    )
    for n in _names
]


def test_unpack_bluez_managed_objects(benchmark: BenchmarkFixture) -> None:
    @benchmark
    def _():
        for _ in range(ITERATIONS):
            unpack_variants(bluez_managed_objects)


def test_unpack_systemd_list_units(benchmark: BenchmarkFixture) -> None:
    @benchmark
    def _():
        for _ in range(ITERATIONS):
            unpack_variants(systemd_list_units)
