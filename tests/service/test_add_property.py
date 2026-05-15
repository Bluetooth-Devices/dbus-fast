"""Unit tests for ServiceInterface.add_property runtime registration."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from dbus_fast import PropertyAccess
from dbus_fast import introspection as intr
from dbus_fast.annotations import DBusStr
from dbus_fast.service import ServiceInterface, dbus_property


def _call_get(interface: ServiceInterface, prop: Any) -> Any:
    """Synchronously invoke _get_property_value for a sync getter."""
    out: dict[str, Any] = {}

    def cb(
        iface: ServiceInterface,
        p: Any,
        value: Any,
        err: Exception | None,
    ) -> None:
        out["iface"] = iface
        out["prop"] = p
        out["value"] = value
        out["err"] = err

    ServiceInterface._get_property_value(interface, prop, cb)
    return out


def _call_set(interface: ServiceInterface, prop: Any, value: Any) -> dict[str, Any]:
    out: dict[str, Any] = {}

    def cb(iface: ServiceInterface, p: Any, err: Exception | None) -> None:
        out["err"] = err

    ServiceInterface._set_property_value(interface, prop, value, cb)
    return out


def _find(interface: ServiceInterface, name: str) -> Any:
    for prop in ServiceInterface._get_properties(interface):
        if prop.name == name:
            return prop
    raise AssertionError(f"property {name!r} not found")


def test_add_property_read_only_appends_and_introspects() -> None:
    iface = ServiceInterface("test.dyn.read")
    state = {"v": 42}

    iface.add_property(
        "Counter",
        "u",
        getter=lambda _self: state["v"],
    )

    prop = _find(iface, "Counter")
    assert prop.signature == "u"
    assert prop.access == PropertyAccess.READ
    assert not prop.disabled
    assert type(prop.introspection) is intr.Property

    result = _call_get(iface, prop)
    assert result["err"] is None
    assert result["value"] == 42

    intr_iface = iface.introspect()
    names = [p.name for p in intr_iface.properties]
    assert "Counter" in names


def test_add_property_writable_invokes_setter() -> None:
    iface = ServiceInterface("test.dyn.write")
    state = {"v": "init"}

    iface.add_property(
        "Tag",
        "s",
        getter=lambda _self: state["v"],
        setter=lambda _self, value: state.__setitem__("v", value),
    )

    prop = _find(iface, "Tag")
    assert prop.access == PropertyAccess.READWRITE

    out = _call_set(iface, prop, "updated")
    assert out["err"] is None
    assert state["v"] == "updated"

    result = _call_get(iface, prop)
    assert result["value"] == "updated"


def test_add_property_write_only_inferred() -> None:
    iface = ServiceInterface("test.dyn.writeonly")
    state = {"v": 0}

    iface.add_property(
        "WriteOnly",
        "i",
        setter=lambda _self, value: state.__setitem__("v", value),
    )

    prop = _find(iface, "WriteOnly")
    assert prop.access == PropertyAccess.WRITE
    assert prop.prop_setter is not None

    _call_set(iface, prop, 7)
    assert state["v"] == 7


def test_add_property_disabled_is_hidden_from_introspection() -> None:
    iface = ServiceInterface("test.dyn.hidden")
    iface.add_property(
        "Hidden",
        "s",
        getter=lambda _self: "x",
        disabled=True,
    )
    prop = _find(iface, "Hidden")
    assert prop.disabled
    intr_iface = iface.introspect()
    assert all(p.name != "Hidden" for p in intr_iface.properties)


def test_add_property_explicit_access_overrides_inference() -> None:
    iface = ServiceInterface("test.dyn.explicit")
    iface.add_property(
        "ExplicitRead",
        "s",
        getter=lambda _self: "ro",
        setter=lambda _self, _v: None,
        access=PropertyAccess.READ,
    )
    prop = _find(iface, "ExplicitRead")
    assert prop.access == PropertyAccess.READ


def test_add_property_duplicate_name_rejected() -> None:
    iface = ServiceInterface("test.dyn.dup")
    iface.add_property("Same", "s", getter=lambda _self: "")
    with pytest.raises(ValueError, match="already defined"):
        iface.add_property("Same", "i", getter=lambda _self: 0)


def test_add_property_requires_getter_or_setter() -> None:
    iface = ServiceInterface("test.dyn.empty")
    with pytest.raises(ValueError, match="getter or setter"):
        iface.add_property("Nope", "s")


def test_add_property_readable_requires_getter() -> None:
    iface = ServiceInterface("test.dyn.noget")
    with pytest.raises(ValueError, match=r"readable.*getter"):
        iface.add_property(
            "X",
            "s",
            setter=lambda _self, _v: None,
            access=PropertyAccess.READWRITE,
        )


def test_add_property_writable_requires_setter() -> None:
    iface = ServiceInterface("test.dyn.noset")
    with pytest.raises(ValueError, match=r"writable.*setter"):
        iface.add_property(
            "X",
            "s",
            getter=lambda _self: "",
            access=PropertyAccess.READWRITE,
        )


def test_add_property_bad_signature_rejected() -> None:
    iface = ServiceInterface("test.dyn.sig")
    with pytest.raises(ValueError, match="single complete type"):
        iface.add_property("X", "ss", getter=lambda _self: ("", ""))


def test_add_property_bad_name_rejected() -> None:
    iface = ServiceInterface("test.dyn.name")
    with pytest.raises(Exception):  # InvalidMemberNameError descends from base
        iface.add_property("bad name", "s", getter=lambda _self: "")


def test_add_property_type_errors() -> None:
    iface = ServiceInterface("test.dyn.types")
    with pytest.raises(TypeError, match="name must be a string"):
        iface.add_property(123, "s", getter=lambda _self: "")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="signature must be a string"):
        iface.add_property("X", 1, getter=lambda _self: "")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="disabled must be a bool"):
        iface.add_property(
            "X",
            "s",
            getter=lambda _self: "",
            disabled="no",  # type: ignore[arg-type]
        )
    with pytest.raises(TypeError, match="access must be a PropertyAccess"):
        iface.add_property(
            "X",
            "s",
            getter=lambda _self: "",
            access="read",  # type: ignore[arg-type]
        )
    with pytest.raises(TypeError, match="getter must be callable"):
        iface.add_property("X", "s", getter="nope")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="setter must be callable"):
        iface.add_property("X", "s", setter="nope")  # type: ignore[arg-type]


class _Mixed(ServiceInterface):
    def __init__(self) -> None:
        super().__init__("test.mixed")
        self._a = "decorated"

    @dbus_property()
    def Static(self) -> DBusStr:
        return self._a

    @Static.setter
    def Static(self, val: DBusStr) -> None:
        self._a = val


def test_add_property_coexists_with_decorated_properties() -> None:
    iface = _Mixed()
    state = {"v": 0}
    iface.add_property(
        "Dynamic",
        "u",
        getter=lambda _self: state["v"],
        setter=lambda _self, v: state.__setitem__("v", v),
    )

    names = {p.name for p in ServiceInterface._get_properties(iface)}
    assert {"Static", "Dynamic"} <= names

    static = _find(iface, "Static")
    dynamic = _find(iface, "Dynamic")

    _call_set(iface, static, "patched")
    assert iface._a == "patched"

    _call_set(iface, dynamic, 9)
    assert state["v"] == 9
    assert _call_get(iface, dynamic)["value"] == 9


def test_add_property_async_getter_setter() -> None:
    iface = ServiceInterface("test.dyn.async")
    state = {"v": "old"}

    async def aget(_self: ServiceInterface) -> str:
        return state["v"]

    async def aset(_self: ServiceInterface, value: str) -> None:
        state["v"] = value

    iface.add_property("Async", "s", getter=aget, setter=aset)

    async def runner() -> None:
        prop = _find(iface, "Async")

        get_done = asyncio.get_running_loop().create_future()

        def gcb(_i: Any, _p: Any, value: Any, err: Exception | None) -> None:
            if err is not None:
                get_done.set_exception(err)
            else:
                get_done.set_result(value)

        ServiceInterface._get_property_value(iface, prop, gcb)
        assert await get_done == "old"

        set_done = asyncio.get_running_loop().create_future()

        def scb(_i: Any, _p: Any, err: Exception | None) -> None:
            if err is not None:
                set_done.set_exception(err)
            else:
                set_done.set_result(None)

        ServiceInterface._set_property_value(iface, prop, "new", scb)
        await set_done
        assert state["v"] == "new"

    asyncio.run(runner())


def test_add_property_getter_exception_routed_to_callback() -> None:
    iface = ServiceInterface("test.dyn.err")

    def boom(_self: ServiceInterface) -> Any:
        raise RuntimeError("nope")

    iface.add_property("Boom", "s", getter=boom)
    prop = _find(iface, "Boom")
    out = _call_get(iface, prop)
    assert out["value"] is None
    assert isinstance(out["err"], RuntimeError)


def test_add_property_setter_exception_routed_to_callback() -> None:
    iface = ServiceInterface("test.dyn.err2")

    def boom(_self: ServiceInterface, _v: Any) -> None:
        raise RuntimeError("setter-boom")

    iface.add_property(
        "Boom",
        "s",
        getter=lambda _self: "",
        setter=boom,
    )
    prop = _find(iface, "Boom")
    out = _call_set(iface, prop, "x")
    assert isinstance(out["err"], RuntimeError)


def test_emit_properties_changed_works_for_dynamic_property() -> None:
    """Dynamic properties participate in emit_properties_changed metadata."""
    iface = ServiceInterface("test.dyn.changed")
    state = {"v": 1}
    iface.add_property(
        "Live",
        "u",
        getter=lambda _self: state["v"],
        setter=lambda _self, v: state.__setitem__("v", v),
    )
    # No bus is attached, but the method must still resolve the property name
    # to its signature without raising.
    iface.emit_properties_changed({"Live": 5})
