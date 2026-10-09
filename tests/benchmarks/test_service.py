from pytest_codspeed import BenchmarkFixture

from dbus_fast.annotations import DBusBytes, DBusInt16
from dbus_fast.message import Message
from dbus_fast.message_bus import BaseMessageBus
from dbus_fast.service import ServiceInterface, dbus_property, signal

ITERATIONS = 1000

# A GATT server exporting a handful of services, each with a few
# characteristics, is a typical service-side object tree.
EXPORTS = 64


class _OfflineBus(BaseMessageBus):
    def send(self, msg: Message) -> None:
        pass


class _Characteristic(ServiceInterface):
    def __init__(self) -> None:
        super().__init__("org.bluez.GattCharacteristic1")
        self._value = b"\x00"

    @dbus_property()
    def Value(self) -> DBusBytes:
        return self._value

    @Value.setter
    def Value(self, value: DBusBytes) -> None:
        self._value = value

    @signal()
    def Changed(self) -> DBusInt16:
        return 1


def _build_exported(exports: int) -> tuple[_OfflineBus, _Characteristic]:
    """Export ``exports`` characteristics and return the bus and the first one."""
    bus = _OfflineBus(bus_address="unix:path=/dev/null")
    chars = [_Characteristic() for _ in range(exports)]
    for i, char in enumerate(chars):
        bus.export(f"/org/example/service{i // 8}/char{i % 8}", char)
    return bus, chars[0]


def test_emit_properties_changed_many_exports(benchmark: BenchmarkFixture) -> None:
    _bus, char = _build_exported(EXPORTS)
    emit = char.emit_properties_changed
    changed = {"Value": b"\x01\x02"}

    @benchmark
    def _() -> None:
        for _ in range(ITERATIONS):
            emit(changed)


def test_emit_signal_many_exports(benchmark: BenchmarkFixture) -> None:
    _bus, char = _build_exported(EXPORTS)
    emit = char.Changed

    @benchmark
    def _() -> None:
        for _ in range(ITERATIONS):
            emit()


def test_emit_properties_changed_single_export(benchmark: BenchmarkFixture) -> None:
    _bus, char = _build_exported(1)
    emit = char.emit_properties_changed
    changed = {"Value": b"\x01\x02"}

    @benchmark
    def _() -> None:
        for _ in range(ITERATIONS):
            emit(changed)
