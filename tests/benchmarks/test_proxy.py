import asyncio
import itertools
import json
import os

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

# The 38 distinct introspection documents a Home Assistant Supervisor sees on
# its host: systemd, NetworkManager, UDisks2, logind, resolved, hostname,
# timedate, rauc and os-agent. Generated from Supervisor's dbus service mocks,
# which mirror `gdbus introspect` output of the real services.
SUPERVISOR_DOCS = list(json.loads(_read("supervisor-introspection.json")).values())

# Inserting a fresh token into every name attribute yields documents,
# interfaces and member shapes no cache can have seen, however many times the
# benchmark runs.
_TOKEN = "zz0zz"
_SUPERVISOR_TEMPLATES = [
    data.replace('name="', f'name="{_TOKEN}') for data in SUPERVISOR_DOCS
]
_unique_counter = itertools.count()


def _unique_supervisor_docs() -> list[str]:
    token = f"u{next(_unique_counter)}x"
    return [template.replace(_TOKEN, token) for template in _SUPERVISOR_TEMPLATES]


def _replies(data: str) -> list[str]:
    """Distinct str objects with the same content, as separate replies are."""
    return ["".join(list(data)) for _ in range(OBJECTS)]


class _OfflineBus(MessageBus):
    """An unconnected bus that skips the AddMatch rules get_interface would send."""

    def _init_high_level_client(self) -> None:
        pass


def _build_bus() -> MessageBus:
    async def _setup() -> MessageBus:
        return _OfflineBus(bus_address="unix:path=/dev/null")

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


def test_parse_introspection_supervisor_cold_start(
    benchmark: BenchmarkFixture,
) -> None:
    @benchmark
    def _() -> None:
        for data in _unique_supervisor_docs():
            Node.parse(data)


def test_parse_introspection_unique_documents_shared_interfaces(
    benchmark: BenchmarkFixture,
) -> None:
    """Document bytes never repeat but every interface in them does."""

    @benchmark
    def _() -> None:
        for data in SUPERVISOR_DOCS:
            n = next(_unique_counter)
            Node.parse(data.replace("</node>", f'<node name="u{n}x"/></node>'))


def test_get_interface_supervisor_cold_start(benchmark: BenchmarkFixture) -> None:
    bus = _build_bus()

    @benchmark
    def _() -> None:
        docs = _unique_supervisor_docs()
        nodes = [Node.parse(data) for data in docs]
        _get_all_interfaces(bus, nodes)


_UNIQUE_MEMBERS_TEMPLATE = f"""
<node>
  <interface name="org.example.{_TOKEN}">
    <method name="Get{_TOKEN}">
      <arg direction="in" type="s"/>
      <arg direction="out" type="v"/>
    </method>
    <method name="Set{_TOKEN}">
      <arg direction="in" type="v"/>
    </method>
    <property name="PropA{_TOKEN}" type="s" access="readwrite"/>
    <property name="PropB{_TOKEN}" type="u" access="read"/>
    <signal name="Changed{_TOKEN}">
      <arg type="s"/>
    </signal>
  </interface>
</node>
"""


def test_get_interface_unique_members(benchmark: BenchmarkFixture) -> None:
    """Member shapes never repeat, so nothing about the proxy can be reused."""
    bus = _build_bus()

    @benchmark
    def _() -> None:
        for i in range(OBJECTS):
            token = f"u{next(_unique_counter)}x"
            node = Node.parse(_UNIQUE_MEMBERS_TEMPLATE.replace(_TOKEN, token))
            proxy = bus.get_proxy_object(_BUS_NAME, f"/org/example/obj{i}", node)
            proxy.get_interface(f"org.example.{token}")
