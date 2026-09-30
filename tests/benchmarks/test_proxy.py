import asyncio
import os
from typing import Any

from pytest_codspeed import BenchmarkFixture

from dbus_fast.aio import MessageBus
from dbus_fast.introspection import Node

# NetworkManager and UDisks2 export many objects whose introspection XML is
# identical: every wired device, every partition with a filesystem.
OBJECTS = 20

_BUS_NAME = ":1.5"
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
_STANDARD_INTERFACES = (
    "org.freedesktop.DBus.Properties",
    "org.freedesktop.DBus.Introspectable",
    "org.freedesktop.DBus.Peer",
)


def _read(name: str) -> str:
    with open(os.path.join(_DATA_DIR, name)) as f:
        return f.read()


NM_WIRED_DEVICE = _read("networkmanager-wired-device.xml")
UDISKS2_PARTITION_BLOCK = _read("udisks2-partition-block.xml")


def _replies(data: str) -> list[str]:
    """Distinct str objects with the same content, as separate replies are."""
    return ["".join(list(data)) for _ in range(OBJECTS)]


class _OfflineBus(MessageBus):
    """A bus that drops the AddMatch and GetNameOwner calls get_interface makes."""

    def _init_high_level_client(self) -> None:
        pass

    def _call(self, *args: Any, **kwargs: Any) -> None:
        pass


def _build_bus() -> MessageBus:
    async def _setup() -> MessageBus:
        bus = _OfflineBus()
        bus._name_owners[_BUS_NAME] = _BUS_NAME
        return bus

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_setup())
    finally:
        loop.close()


def test_parse_introspection_networkmanager_devices(
    benchmark: BenchmarkFixture,
) -> None:
    replies = _replies(NM_WIRED_DEVICE)

    @benchmark
    def _() -> None:
        for data in replies:
            Node.parse(data)


def test_parse_introspection_udisks2_blocks(benchmark: BenchmarkFixture) -> None:
    replies = _replies(UDISKS2_PARTITION_BLOCK)

    @benchmark
    def _() -> None:
        for data in replies:
            Node.parse(data)


def _get_all_interfaces(bus: MessageBus, nodes: list[Node]) -> None:
    for i, node in enumerate(nodes):
        proxy = bus.get_proxy_object(_BUS_NAME, f"/org/example/obj{i}", node)
        for interface in node.interfaces:
            proxy.get_interface(interface.name)


def test_get_interface_networkmanager_devices(benchmark: BenchmarkFixture) -> None:
    bus = _build_bus()
    nodes = [Node.parse(data) for data in _replies(NM_WIRED_DEVICE)]

    @benchmark
    def _() -> None:
        _get_all_interfaces(bus, nodes)


def test_get_interface_udisks2_blocks(benchmark: BenchmarkFixture) -> None:
    bus = _build_bus()
    nodes = [Node.parse(data) for data in _replies(UDISKS2_PARTITION_BLOCK)]

    @benchmark
    def _() -> None:
        _get_all_interfaces(bus, nodes)


def test_get_interface_standard_interfaces(benchmark: BenchmarkFixture) -> None:
    bus = _build_bus()
    nodes = [Node.parse(data) for data in _replies(NM_WIRED_DEVICE)]

    @benchmark
    def _() -> None:
        for i, node in enumerate(nodes):
            proxy = bus.get_proxy_object(_BUS_NAME, f"/org/example/obj{i}", node)
            for name in _STANDARD_INTERFACES:
                proxy.get_interface(name)
