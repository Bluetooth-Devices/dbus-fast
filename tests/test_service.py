"""Pure-function tests for the service-side decorators and ServiceInterface.

These pin the metadata and validation contract of ``dbus_method``,
``dbus_signal``, ``dbus_property`` and ``ServiceInterface`` without a
session bus. The decorators read the *decorated* function's annotations,
so the validation raises here fire identically on the pure-Python and
Cython builds; the decorator-parameter type guards (``name``/``disabled``)
are deliberately not pinned because Cython coerces those annotated
parameters, diverging from pure Python.
"""

from typing import Annotated

import pytest

from dbus_fast import introspection as intr
from dbus_fast.annotations import DBusInt32, DBusSignature, DBusStr
from dbus_fast.constants import PropertyAccess
from dbus_fast.errors import SignalDisabledError
from dbus_fast.service import (
    ServiceInterface,
    dbus_method,
    dbus_property,
    dbus_signal,
    method,
    signal,
)


def _method_meta(cls, attr):
    return getattr(cls, attr).__dict__["__DBUS_METHOD"]


def _signal_meta(cls, attr):
    return getattr(cls, attr).__dict__["__DBUS_SIGNAL"]


class TestDbusMethod:
    def test_default_name_is_function_name(self):
        """An unnamed @dbus_method takes the decorated function's name."""

        class Iface(ServiceInterface):
            @dbus_method()
            def Echo(self, val: DBusStr) -> DBusStr:
                return val

        assert _method_meta(Iface, "Echo").name == "Echo"

    def test_custom_name_overrides_function_name(self):
        """The name argument overrides the member name."""

        class Iface(ServiceInterface):
            @dbus_method(name="Renamed")
            def original(self) -> DBusStr:
                return "x"

        assert _method_meta(Iface, "original").name == "Renamed"

    def test_disabled_flag_recorded(self):
        """disabled=True is stored on the method metadata."""

        class Iface(ServiceInterface):
            @dbus_method(disabled=True)
            def Hidden(self) -> DBusStr:
                return "x"

        assert _method_meta(Iface, "Hidden").disabled is True

    def test_in_and_out_signatures(self):
        """Parameter and return annotations populate the signatures."""

        class Iface(ServiceInterface):
            @dbus_method()
            def Concat(self, a: DBusStr, b: DBusStr) -> DBusStr:
                return a + b

        meta = _method_meta(Iface, "Concat")
        assert meta.in_signature == "ss"
        assert meta.out_signature == "s"

    def test_no_arguments_yields_empty_signatures(self):
        """A no-arg, no-return method has empty in and out signatures."""

        class Iface(ServiceInterface):
            @dbus_method()
            def Ping(self):
                return None

        meta = _method_meta(Iface, "Ping")
        assert meta.in_signature == ""
        assert meta.out_signature == ""

    def test_multiple_out_arguments(self):
        """A multi-type return annotation produces multiple out args."""

        class Iface(ServiceInterface):
            @dbus_method()
            def Pair(self) -> Annotated[tuple, DBusSignature("su")]:
                return ("a", 1)

        meta = _method_meta(Iface, "Pair")
        assert meta.out_signature == "su"
        assert len(meta.introspection.out_args) == 2

    def test_parameter_without_annotation_raises(self):
        """A method parameter lacking a D-Bus annotation is rejected."""
        with pytest.raises(ValueError, match="must specify the dbus type"):

            class Iface(ServiceInterface):
                @dbus_method()
                def Bad(self, x) -> DBusStr:
                    return "x"

    def test_introspection_arg_directions_and_names(self):
        """In args carry the parameter name and IN direction; out args are OUT."""

        class Iface(ServiceInterface):
            @dbus_method()
            def Lookup(self, key: DBusStr) -> DBusInt32:
                return 0

        m = _method_meta(Iface, "Lookup").introspection
        assert isinstance(m, intr.Method)
        assert [(a.name, a.direction) for a in m.in_args] == [
            ("key", intr.ArgDirection.IN)
        ]
        assert [a.direction for a in m.out_args] == [intr.ArgDirection.OUT]

    def test_method_alias_is_dbus_method(self):
        """The legacy ``method`` name aliases ``dbus_method``."""
        assert method is dbus_method


class TestDbusSignal:
    def test_default_name_and_signature(self):
        """A signal takes the function name and its return signature."""

        class Iface(ServiceInterface):
            @dbus_signal()
            def Changed(self) -> DBusInt32:
                return 1

        meta = _signal_meta(Iface, "Changed")
        assert meta.name == "Changed"
        assert meta.signature == "i"

    def test_custom_name(self):
        """The name argument overrides the signal member name."""

        class Iface(ServiceInterface):
            @dbus_signal(name="Renamed")
            def original(self) -> DBusStr:
                return "x"

        assert _signal_meta(Iface, "original").name == "Renamed"

    def test_no_return_annotation_empty_signature(self):
        """A signal without a return annotation has an empty signature."""

        class Iface(ServiceInterface):
            @dbus_signal()
            def Bare(self):
                return None

        assert _signal_meta(Iface, "Bare").signature == ""

    def test_calling_disabled_signal_raises(self):
        """Invoking a disabled signal raises SignalDisabledError."""

        class Iface(ServiceInterface):
            @dbus_signal(disabled=True)
            def Quiet(self) -> DBusStr:
                return "q"

        with pytest.raises(SignalDisabledError, match="disabled signal"):
            Iface("com.example.E").Quiet()

    def test_calling_enabled_signal_returns_value(self):
        """An enabled signal with no buses attached returns the handler value."""

        class Iface(ServiceInterface):
            @dbus_signal()
            def Emit(self) -> DBusStr:
                return "payload"

        assert Iface("com.example.E").Emit() == "payload"

    def test_signal_alias_is_dbus_signal(self):
        """The legacy ``signal`` name aliases ``dbus_signal``."""
        assert signal is dbus_signal


class TestDbusProperty:
    def test_access_must_be_property_access(self):
        """A non-PropertyAccess access argument is rejected."""
        with pytest.raises(TypeError, match="access must be a PropertyAccess"):
            dbus_property(access=object())

    def test_property_requires_only_self(self):
        """A getter with extra parameters is rejected."""
        with pytest.raises(ValueError, match='only have the "self"'):

            @dbus_property()
            def bad(self, extra) -> DBusStr:
                return "x"

    def test_property_requires_return_annotation(self):
        """A getter without a return annotation is rejected."""
        with pytest.raises(ValueError, match="must specify the dbus type"):

            @dbus_property()
            def bad(self):
                return "x"

    def test_property_signature_must_be_single_type(self):
        """A getter whose signature is more than one type is rejected."""
        with pytest.raises(ValueError, match="single complete type"):

            @dbus_property()
            def bad(self) -> Annotated[tuple, DBusSignature("ss")]:
                return ("a", "b")

    def test_default_name_and_access(self):
        """An unnamed property defaults to the getter name and READWRITE."""

        class Iface(ServiceInterface):
            @dbus_property()
            def Prop(self) -> DBusStr:
                return self._p

            @Prop.setter
            def Prop(self, v: DBusStr):
                self._p = v

        prop = ServiceInterface._get_properties(Iface("com.example.E"))[0]
        assert prop.name == "Prop"
        assert prop.access == PropertyAccess.READWRITE

    def test_custom_name_and_read_access(self):
        """The name and access arguments flow onto the property metadata."""

        class Iface(ServiceInterface):
            @dbus_property(name="Renamed", access=PropertyAccess.READ)
            def prop(self) -> DBusStr:
                return "x"

        prop = ServiceInterface._get_properties(Iface("com.example.E"))[0]
        assert prop.name == "Renamed"
        assert prop.access == PropertyAccess.READ

    def test_setter_preserves_options(self):
        """Defining a setter retains the name and access from the getter."""

        class Iface(ServiceInterface):
            @dbus_property(name="Custom", access=PropertyAccess.READWRITE)
            def prop(self) -> DBusStr:
                return self._p

            @prop.setter
            def prop(self, v: DBusStr):
                self._p = v

        prop = ServiceInterface._get_properties(Iface("com.example.E"))[0]
        assert prop.name == "Custom"
        assert prop.access == PropertyAccess.READWRITE
        assert prop.prop_setter is not None


class TestServiceInterface:
    def test_name_is_stored(self):
        """The interface keeps the name passed to its constructor."""
        assert ServiceInterface("com.example.Sample").name == "com.example.Sample"

    def test_members_are_collected(self):
        """Methods, signals and properties are gathered at construction."""

        class Iface(ServiceInterface):
            @dbus_method()
            def M(self) -> DBusStr:
                return "x"

            @dbus_signal()
            def S(self) -> DBusInt32:
                return 1

            @dbus_property(access=PropertyAccess.READ)
            def P(self) -> DBusStr:
                return "x"

        iface = Iface("com.example.E")
        assert [m.name for m in ServiceInterface._get_methods(iface)] == ["M"]
        assert [s.name for s in ServiceInterface._get_signals(iface)] == ["S"]
        assert [p.name for p in ServiceInterface._get_properties(iface)] == ["P"]

    def test_writable_property_without_setter_raises(self):
        """A READWRITE property with no setter fails interface construction."""

        class Iface(ServiceInterface):
            @dbus_property()
            def Prop(self) -> DBusStr:
                return "x"

        with pytest.raises(ValueError, match="writable but does not have a setter"):
            Iface("com.example.E")

    def test_readonly_property_without_setter_ok(self):
        """A READ-only property needs no setter."""

        class Iface(ServiceInterface):
            @dbus_property(access=PropertyAccess.READ)
            def Prop(self) -> DBusStr:
                return "x"

        assert isinstance(Iface("com.example.E"), Iface)

    def test_introspect_includes_enabled_members(self):
        """introspect() reports enabled methods, signals and properties."""

        class Iface(ServiceInterface):
            @dbus_method()
            def M(self) -> DBusStr:
                return "x"

            @dbus_signal()
            def S(self) -> DBusInt32:
                return 1

            @dbus_property(access=PropertyAccess.READ)
            def P(self) -> DBusStr:
                return "x"

        intro = Iface("com.example.E").introspect()
        assert isinstance(intro, intr.Interface)
        assert [m.name for m in intro.methods] == ["M"]
        assert [s.name for s in intro.signals] == ["S"]
        assert [p.name for p in intro.properties] == ["P"]

    def test_introspect_excludes_disabled_members(self):
        """Disabled members are omitted from introspection output."""

        class Iface(ServiceInterface):
            @dbus_method(disabled=True)
            def M(self) -> DBusStr:
                return "x"

            @dbus_signal(disabled=True)
            def S(self) -> DBusInt32:
                return 1

            @dbus_property(access=PropertyAccess.READ, disabled=True)
            def P(self) -> DBusStr:
                return "x"

        intro = Iface("com.example.E").introspect()
        assert intro.methods == []
        assert intro.signals == []
        assert intro.properties == []


class _RecordingBus:
    """Minimal stand-in capturing _interface_signal_notify calls."""

    def __init__(self):
        self.notifications = []

    def _interface_signal_notify(
        self, interface, interface_name, member, signature, body
    ):
        self.notifications.append((interface_name, member, signature, body))


class TestEmitPropertiesChanged:
    def _iface(self):
        class Iface(ServiceInterface):
            def __init__(self):
                super().__init__("com.example.E")
                self._p = "v"

            @dbus_property()
            def Prop(self) -> DBusStr:
                return self._p

            @Prop.setter
            def Prop(self, v: DBusStr):
                self._p = v

        return Iface()

    def _attach(self, iface):
        bus = _RecordingBus()
        ServiceInterface._add_bus(iface, bus, lambda i, m: lambda msg, sr: None)
        return bus

    def test_changed_property_emitted_as_variant(self):
        """A changed property is wrapped in a Variant with its signature."""
        iface = self._iface()
        bus = self._attach(iface)
        iface.emit_properties_changed({"Prop": "new"})

        _, member, signature, body = bus.notifications[0]
        assert member == "PropertiesChanged"
        assert signature == "sa{sv}as"
        assert body[0] == "com.example.E"
        variant = body[1]["Prop"]
        assert variant.signature == "s"
        assert variant.value == "new"
        assert body[2] == []

    def test_unknown_property_is_ignored(self):
        """A name not exposed by the interface is not emitted."""
        iface = self._iface()
        bus = self._attach(iface)
        iface.emit_properties_changed({"Nonexistent": "x"})

        body = bus.notifications[0][3]
        assert body[1] == {}

    def test_invalidated_properties_passed_through(self):
        """The invalidated list reaches the signal body unchanged."""
        iface = self._iface()
        bus = self._attach(iface)
        iface.emit_properties_changed({}, ["Prop"])

        body = bus.notifications[0][3]
        assert body[2] == ["Prop"]
