import asyncio

from pytest_codspeed import BenchmarkFixture

from dbus_fast.aio import MessageBus
from dbus_fast.aio.proxy_object import ProxyInterface
from dbus_fast.constants import MessageType
from dbus_fast.introspection import Arg, Interface, Signal
from dbus_fast.message import Message
from dbus_fast.proxy_object import SignalHandler
from dbus_fast.signature import Variant

ITERATIONS = 1000

# A realistic adapter load: a single BlueZ host commonly tracks dozens of
# advertising devices at once. Every PropertiesChanged delivered to the bus
# is offered to *every* subscribed proxy interface's handler, so the count
# below sets how many times the O(N) reject path runs per signal.
SUBSCRIBERS = 16

_BUS_NAME = ":1.5"
_PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"


def _build_properties_interface() -> Interface:
    intf = Interface(_PROPERTIES_INTERFACE)
    intf.signals = [
        Signal("PropertiesChanged", args=[Arg("s"), Arg("a{sv}"), Arg("as")])
    ]
    return intf


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

    Mirrors the high-level client signal path: each
    :class:`ProxyInterface` registers one ``_message_handler`` into the
    bus's user-handler list. The returned signal targets the *last*
    subscriber's object path, so dispatching it walks the whole handler
    list — ``subscribers - 1`` path-mismatch rejects plus one match and
    callback. This is the per-signal cost that scales with the number of
    tracked devices, and nothing under ``tests/benchmarks/`` exercised the
    routing/dispatch layer before — only marshalling and unmarshalling.

    The bus is built inside a throwaway event loop because
    :class:`MessageBus` binds the running loop at construction; the signal
    dispatch path itself is synchronous and never touches it.
    """

    async def _setup() -> tuple[MessageBus, Message]:
        bus = MessageBus()
        bus._name_owners[_BUS_NAME] = _BUS_NAME
        intf = _build_properties_interface()
        last_path = ""
        for i in range(subscribers):
            last_path = f"/org/bluez/hci0/dev_{i:012X}"
            proxy = ProxyInterface(_BUS_NAME, last_path, intf, bus)
            proxy._signal_handlers["PropertiesChanged"] = [
                SignalHandler(lambda *args: None, False)
            ]
            bus.add_message_handler(proxy._message_handler)
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
