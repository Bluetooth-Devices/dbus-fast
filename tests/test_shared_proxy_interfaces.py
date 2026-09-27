"""Proxy interfaces that share their members through a per-interface class."""

import inspect
from unittest.mock import patch

import pytest

from dbus_fast import introspection as intr
from dbus_fast import proxy_object
from dbus_fast.aio import MessageBus
from dbus_fast.aio.proxy_object import ProxyInterface, ProxyObject
from dbus_fast.constants import MessageType
from dbus_fast.message import Message
from dbus_fast.signature import Variant

_XML = (
    "<node>"
    '<interface name="org.example.Iface">'
    '<method name="Echo"><arg type="s" direction="in"/><arg type="s" direction="out"/></method>'
    '<method name="Pair"><arg type="u" direction="out"/><arg type="u" direction="out"/></method>'
    '<method name="Nothing"/>'
    '<property name="Level" type="u" access="readwrite"/>'
    '<signal name="Tick"><arg type="s"/></signal>'
    "</interface>"
    '<interface name="org.example.Other">'
    '<method name="Echo"><arg type="u" direction="in"/><arg type="u" direction="out"/></method>'
    "</interface>"
    "</node>"
)

pytestmark = pytest.mark.asyncio

_MEMBER_PREFIXES = ("call_", "get_", "set_", "on_", "off_")


class _Bus(MessageBus):
    """An aio bus that records messages instead of using a socket."""

    def __init__(self) -> None:
        super().__init__(bus_address="unix:path=/dev/null")
        self.sent: list[Message] = []
        self.match_rules: list[str] = []
        self._name_owners["org.example"] = ":1.1"

    def _init_high_level_client(self) -> None:
        pass

    def _call(self, msg, callback=None) -> None:
        pass

    def _add_match_rule(self, match_rule):
        self.match_rules.append(match_rule)

    def _remove_match_rule(self, match_rule):
        self.match_rules.remove(match_rule)

    async def call(self, msg: Message) -> Message:
        self.sent.append(msg)
        if msg.member == "Get":
            return Message(
                message_type=MessageType.METHOD_RETURN,
                reply_serial=1,
                signature="v",
                body=[Variant("u", 7)],
            )
        if msg.member == "Pair":
            return Message(
                message_type=MessageType.METHOD_RETURN,
                reply_serial=1,
                signature="uu",
                body=[1, 2],
            )
        if msg.member == "Echo":
            return Message(
                message_type=MessageType.METHOD_RETURN,
                reply_serial=1,
                signature=msg.signature,
                body=list(msg.body),
            )
        return Message(message_type=MessageType.METHOD_RETURN, reply_serial=1)


class _PerInstanceInterface(ProxyInterface):
    """Overrides a hook, so members are added per instance as before."""

    added: list[str] = []

    def _add_method(self, intr_method: intr.Method) -> None:
        _PerInstanceInterface.added.append(intr_method.name)
        super()._add_method(intr_method)


class _PerInstanceObject(ProxyObject):
    def __init__(self, bus_name, path, introspection, bus) -> None:
        proxy_object.BaseProxyObject.__init__(
            self, bus_name, path, introspection, bus, _PerInstanceInterface
        )


def _members(interface) -> dict[str, inspect.Signature]:
    return {
        name: inspect.signature(getattr(interface, name))
        for name in dir(interface)
        if name.startswith(_MEMBER_PREFIXES) and callable(getattr(interface, name))
    }


def _proxy(bus: _Bus, path: str = "/a") -> ProxyObject:
    return ProxyObject("org.example", path, intr.Node.parse(_XML), bus)


async def test_shared_interfaces_use_one_class() -> None:
    bus = _Bus()
    first = _proxy(bus, "/a").get_interface("org.example.Iface")
    second = _proxy(bus, "/b").get_interface("org.example.Iface")

    assert type(first) is type(second)
    assert isinstance(first, ProxyInterface)
    assert type(first).__name__ == "ProxyInterface"
    assert type(first).__module__ == ProxyInterface.__module__
    assert "call_echo" not in vars(first)
    assert first.path == "/a"
    assert second.path == "/b"
    assert first._signal_handlers is not second._signal_handlers


async def test_same_members_as_per_instance_path() -> None:
    bus = _Bus()
    shared = _proxy(bus).get_interface("org.example.Iface")
    legacy = _PerInstanceObject(
        "org.example", "/a", intr.Node.parse(_XML), bus
    ).get_interface("org.example.Iface")

    assert "call_echo" in vars(legacy)
    assert _members(shared) == _members(legacy)
    assert set(_members(shared)) == {
        "call_echo",
        "call_pair",
        "call_nothing",
        "get_level",
        "set_level",
        "on_tick",
        "off_tick",
    }


async def test_overridden_hook_is_still_called() -> None:
    _PerInstanceInterface.added.clear()
    bus = _Bus()
    _PerInstanceObject("org.example", "/a", intr.Node.parse(_XML), bus).get_interface(
        "org.example.Iface"
    )
    assert _PerInstanceInterface.added == ["Echo", "Pair", "Nothing"]
    assert not _PerInstanceInterface._shares_members()
    assert ProxyInterface._shares_members()


async def test_different_shapes_get_different_classes() -> None:
    bus = _Bus()
    proxy = _proxy(bus)
    iface = proxy.get_interface("org.example.Iface")
    other = proxy.get_interface("org.example.Other")
    assert type(iface) is not type(other)
    assert inspect.signature(iface.call_echo) == inspect.signature(other.call_echo)


async def test_equal_shapes_share_a_class_without_shared_introspection() -> None:
    bus = _Bus()
    node_a = intr.Node.parse(_XML)
    intr._SHARED_INTERFACES.clear()
    intr._PARSED_NODES.clear()
    node_b = intr.Node.parse(_XML)
    assert node_a.interfaces[0] is not node_b.interfaces[0]

    first = ProxyObject("org.example", "/a", node_a, bus).get_interface(
        "org.example.Iface"
    )
    second = ProxyObject("org.example", "/b", node_b, bus).get_interface(
        "org.example.Iface"
    )
    assert type(first) is type(second)
    assert first.introspection is node_a.interfaces[0]
    assert second.introspection is node_b.interfaces[0]


async def test_calls_use_the_instance_state() -> None:
    bus = _Bus()
    first = _proxy(bus, "/a").get_interface("org.example.Iface")
    second = _proxy(bus, "/b").get_interface("org.example.Iface")

    assert await first.call_echo("hi") == "hi"
    assert await second.call_pair() == [1, 2]
    assert await first.call_nothing() is None
    assert await second.get_level() == 7
    await first.set_level(3)

    sent = [(m.path, m.interface, m.member, m.body) for m in bus.sent]
    assert sent[0] == ("/a", "org.example.Iface", "Echo", ["hi"])
    assert sent[1][:3] == ("/b", "org.example.Iface", "Pair")
    assert sent[2][:3] == ("/a", "org.example.Iface", "Nothing")
    assert sent[3] == (
        "/b",
        "org.freedesktop.DBus.Properties",
        "Get",
        ["org.example.Iface", "Level"],
    )
    assert sent[4][:3] == ("/a", "org.freedesktop.DBus.Properties", "Set")
    assert sent[4][3][2] == Variant("u", 3)


async def test_signal_handlers_are_per_instance() -> None:
    bus = _Bus()
    first = _proxy(bus, "/a").get_interface("org.example.Iface")
    second = _proxy(bus, "/b").get_interface("org.example.Iface")

    def handler(value: str) -> None:
        pass

    first.on_tick(handler)
    assert list(first._signal_handlers) == ["Tick"]
    assert second._signal_handlers == {}
    assert bus.match_rules == [first._signal_match_rule]

    second.on_tick(handler)
    first.off_tick(handler)
    assert first._signal_handlers == {}
    assert list(second._signal_handlers) == ["Tick"]
    assert bus.match_rules == [second._signal_match_rule]

    with pytest.raises(TypeError, match="positional parameters"):
        first.on_tick(lambda: None)


async def test_members_can_be_patched_per_instance() -> None:
    bus = _Bus()
    first = _proxy(bus, "/a").get_interface("org.example.Iface")
    second = _proxy(bus, "/b").get_interface("org.example.Iface")

    with patch.object(first, "call_echo") as mock_echo:
        mock_echo.return_value = "patched"
        assert await first.call_echo("x") == "patched"
        assert await second.call_echo("y") == "y"
    assert "call_echo" not in vars(first)
    assert await first.call_echo("z") == "z"
