import pytest

from dbus_fast import Message, MessageType, PropertyAccess
from dbus_fast.aio import MessageBus
from dbus_fast.service import ServiceInterface, dbus_method, dbus_property, dbus_signal


class ExampleInterface(ServiceInterface):
    """An interface that declares all D-Bus types via decorator signatures."""

    def __init__(self) -> None:
        super().__init__("test.interface")
        self._int_prop = 42

    @dbus_method(in_signature="su", out_signature="s")
    def echo_two(self, one: str, two: int) -> str:
        return f"{one}{two}"

    @dbus_method(in_signature="sasu", out_signature="i")
    def mixed(self, one, two, three) -> int:
        return 42

    @dbus_signal(signature="as")
    def list_signal(self) -> list:
        return ["a", "b"]

    @dbus_property(signature="u")
    def int_prop(self) -> int:
        return self._int_prop

    @int_prop.setter
    def int_prop(self, val: int) -> None:
        self._int_prop = val

    @dbus_property(signature="t", access=PropertyAccess.READ)
    def readonly_prop(self) -> int:
        return 7


def test_method_decorator_signatures():
    interface = ExampleInterface()
    methods = ServiceInterface._get_methods(interface)
    by_name = {m.name: m for m in methods}

    echo = by_name["echo_two"]
    assert echo.in_signature == "su"
    assert echo.out_signature == "s"
    # parameter names flow into introspection even though the annotations
    # were not inspected.
    in_args = echo.introspection.in_args
    assert [a.name for a in in_args] == ["one", "two"]
    assert [a.signature for a in in_args] == ["s", "u"]

    mixed = by_name["mixed"]
    assert mixed.in_signature == "sasu"
    assert mixed.out_signature == "i"
    assert [a.signature for a in mixed.introspection.in_args] == ["s", "as", "u"]


def test_signal_decorator_signature():
    interface = ExampleInterface()
    signals = ServiceInterface._get_signals(interface)
    sig = next(s for s in signals if s.name == "list_signal")
    assert sig.signature == "as"
    assert [a.signature for a in sig.introspection.args] == ["as"]


def test_property_decorator_signature():
    interface = ExampleInterface()
    props = {p.name: p for p in ServiceInterface._get_properties(interface)}

    int_prop = props["int_prop"]
    assert int_prop.signature == "u"
    assert int_prop.access == PropertyAccess.READWRITE
    assert int_prop.prop_setter is not None

    readonly = props["readonly_prop"]
    assert readonly.signature == "t"
    assert readonly.access == PropertyAccess.READ

    # getter/setter actually run
    assert interface.int_prop == 42
    interface.int_prop = 100
    assert interface._int_prop == 100


def test_introspection_xml_uses_decorator_signatures():
    interface = ExampleInterface()
    xml = interface.introspect().to_xml()
    methods = {m.attrib["name"]: m for m in xml.findall("method")}
    args = methods["echo_two"].findall("arg")
    assert [
        (a.attrib["name"], a.attrib["type"])
        for a in args
        if a.attrib["direction"] == "in"
    ] == [
        ("one", "s"),
        ("two", "u"),
    ]


def test_signature_must_be_string():
    # The compiled (Cython) build rejects the bad type via annotation typing
    # before the explicit check runs, so match only the argument name shared by
    # both messages.
    with pytest.raises(TypeError, match="in_signature"):
        dbus_method(in_signature=5)
    with pytest.raises(TypeError, match="out_signature"):
        dbus_method(out_signature=5)
    with pytest.raises(TypeError, match="signature"):
        dbus_signal(signature=5)
    with pytest.raises(TypeError, match="signature"):
        dbus_property(signature=5)


def test_method_without_signature_requires_annotations():
    def no_annotation(self, value) -> None:
        return None

    with pytest.raises(ValueError, match="method parameters must specify"):
        dbus_method()(no_annotation)


def test_property_signature_must_be_single_complete_type():
    def getter(self) -> int:
        return 0

    with pytest.raises(ValueError, match="single complete type"):
        dbus_property(signature="ss")(getter)


def test_property_without_signature_requires_return_annotation():
    def getter(self):
        return 0

    with pytest.raises(ValueError, match="return annotation"):
        dbus_property()(getter)


@pytest.mark.asyncio
async def test_decorator_signature_round_trip():
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    interface = ExampleInterface()
    export_path = "/test/path"
    bus1.export(export_path, interface)

    reply = await bus2.call(
        Message(
            destination=bus1.unique_name,
            path=export_path,
            interface=interface.name,
            member="echo_two",
            signature="su",
            body=["x", 9],
        )
    )
    assert reply.message_type == MessageType.METHOD_RETURN, reply.body
    assert reply.signature == "s"
    assert reply.body == ["x9"]

    get_reply = await bus2.call(
        Message(
            destination=bus1.unique_name,
            path=export_path,
            interface="org.freedesktop.DBus.Properties",
            member="Get",
            signature="ss",
            body=[interface.name, "int_prop"],
        )
    )
    assert get_reply.message_type == MessageType.METHOD_RETURN, get_reply.body
    assert get_reply.body[0].signature == "u"
    assert get_reply.body[0].value == 42

    bus1.disconnect()
    bus2.disconnect()
