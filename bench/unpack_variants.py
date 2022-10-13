import timeit

from dbus_fast import Variant, unpack_variants

# cythonize -X language_level=3 -a -i  src/dbus_fast/unpack.py


message = {
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
                    "0000110b-0000-1000-8000-00805f9b34fb",
                    "00001108-0000-1000-8000-00805f9b34fb",
                    "0000110c-0000-1000-8000-00805f9b34fb",
                    "00001800-0000-1000-8000-00805f9b34fb",
                    "00001801-0000-1000-8000-00805f9b34fb",
                    "0000180a-0000-1000-8000-00805f9b34fb",
                    "00001112-0000-1000-8000-00805f9b34fb",
                ],
            ),
        },
        "org.bluez.GattManager1": {},
        "org.bluez.LEAdvertisingManager1": {
            "ActiveInstances": Variant("y", 0),
            "SupportedIncludes": Variant(
                "as", ["tx-power", "appearance", "local-name"]
            ),
            "SupportedInstances": Variant("y", 4),
            "SupportedSecondaryChannels": Variant("as", ["1M", "2M", "Coded"]),
        },
        "org.bluez.Media1": {},
        "org.bluez.NetworkServer1": {},
        "org.freedesktop.DBus.Introspectable": {},
        "org.freedesktop.DBus.Properties": {},
    },
}


def unpack_managed_objects():
    unpack_variants(message)


count = 3000000
time = timeit.Timer(unpack_managed_objects).timeit(count)
print(f"Unpacked {count} get managed objects messages took {time} seconds")
