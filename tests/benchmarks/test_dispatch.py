import asyncio

from pytest_codspeed import BenchmarkFixture

from dbus_fast.aio import MessageBus
from dbus_fast.constants import MessageType
from dbus_fast.introspection import Arg, Interface, Node, Signal
from dbus_fast.message import Message
from dbus_fast.signature import Variant

ITERATIONS = 1000

# A realistic adapter load: a single BlueZ host commonly tracks dozens of
# advertising devices at once. Every PropertiesChanged delivered to the bus
# is offered to *every* subscribed proxy interface's handler, so the count
# below sets how many times the O(N) reject path runs per signal.
SUBSCRIBERS = 16

_BUS_NAME = ":1.5"
_PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"


class _OfflineBus(MessageBus):
    """An unconnected bus that skips the AddMatch calls subscribing would send."""

    def _init_high_level_client(self) -> None:
        pass

    def _add_match_rule(self, match_rule: str) -> None:
        pass


def _build_properties_node() -> Node:
    intf = Interface(_PROPERTIES_INTERFACE)
    intf.signals = [
        Signal("PropertiesChanged", args=[Arg("s"), Arg("a{sv}"), Arg("as")])
    ]
    return Node(interfaces=[intf])


def _build_signal(path: str) -> Message:
    return Message(
        message_type=MessageType.SIGNAL,
        sender=_BUS_NAME,
        path=path,
        interface=_PROPERTIES_INTERFACE,
        member="PropertiesChanged",
        signature="sa{sv}as",
        body=["org.bluez.Device1", {"RSSI": Variant("n", -88)}, []],
    )


def _build_dispatch_fixture(subscribers: int) -> tuple[MessageBus, Message]:
    """A bus with ``subscribers`` proxy interfaces subscribed to PropertiesChanged.

    Each subscriber is a proxy interface on its own object path, subscribed
    through ``on_properties_changed``. The returned signal targets the
    *last* subscriber's path; the other subscribers model the tracked
    devices a signal must not be delivered to.

    The bus is built inside a throwaway event loop because
    :class:`MessageBus` binds the running loop at construction; the signal
    dispatch path itself is synchronous and never touches it.
    """

    async def _setup() -> tuple[MessageBus, Message]:
        bus = _OfflineBus(bus_address="unix:path=/dev/null")
        bus._name_owners[_BUS_NAME] = _BUS_NAME
        node = _build_properties_node()
        last_path = ""
        for i in range(subscribers):
            last_path = f"/org/bluez/hci0/dev_{i:012X}"
            proxy = bus.get_proxy_object(_BUS_NAME, last_path, node)
            proxy.get_interface(_PROPERTIES_INTERFACE).on_properties_changed(
                lambda *args: None
            )
        return bus, _build_signal(last_path)

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_setup())
    finally:
        loop.close()


def test_dispatch_signal_to_matching_subscriber(benchmark: BenchmarkFixture) -> None:
    bus, msg = _build_dispatch_fixture(SUBSCRIBERS)
    process = bus._process_message

    @benchmark
    def _() -> None:
        for _ in range(ITERATIONS):
            process(msg)


def test_dispatch_signal_single_subscriber(benchmark: BenchmarkFixture) -> None:
    bus, msg = _build_dispatch_fixture(1)
    process = bus._process_message

    @benchmark
    def _() -> None:
        for _ in range(ITERATIONS):
            process(msg)
