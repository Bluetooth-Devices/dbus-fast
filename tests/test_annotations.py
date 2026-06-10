import dataclasses
from typing import Annotated, Any, get_args

import pytest

from dbus_fast import annotations
from dbus_fast.annotations import (
    DBusBool,
    DBusByte,
    DBusBytes,
    DBusDict,
    DBusDouble,
    DBusInt16,
    DBusInt32,
    DBusInt64,
    DBusObjectPath,
    DBusSignature,
    DBusSignatureType,
    DBusStr,
    DBusUInt16,
    DBusUInt32,
    DBusUInt64,
    DBusUnixFd,
    DBusVariant,
)
from dbus_fast.signature import Variant

# (alias, expected base type, expected D-Bus signature code)
ALIAS_TABLE: list[tuple[Any, Any, str]] = [
    (DBusBool, bool, "b"),
    (DBusByte, int, "y"),
    (DBusInt16, int, "n"),
    (DBusUInt16, int, "q"),
    (DBusInt32, int, "i"),
    (DBusUInt32, int, "u"),
    (DBusInt64, int, "x"),
    (DBusUInt64, int, "t"),
    (DBusDouble, float, "d"),
    (DBusStr, str, "s"),
    (DBusObjectPath, str, "o"),
    (DBusSignatureType, str, "g"),
    (DBusVariant, Variant, "v"),
    (DBusDict, dict[str, Variant], "a{sv}"),
    (DBusUnixFd, int, "h"),
    (DBusBytes, bytes, "ay"),
]


@pytest.mark.parametrize(("alias", "base", "code"), ALIAS_TABLE)
def test_alias_resolves_to_base_and_signature(alias: Any, base: Any, code: str) -> None:
    resolved, sig = get_args(alias)
    assert resolved == base
    assert sig == DBusSignature(code)


def test_signature_carries_string() -> None:
    assert DBusSignature("(is)").signature == "(is)"


def test_signature_equal_by_value() -> None:
    assert DBusSignature("i") == DBusSignature("i")
    assert DBusSignature("i") != DBusSignature("u")


def test_signature_is_hashable() -> None:
    assert hash(DBusSignature("i")) == hash(DBusSignature("i"))
    assert {DBusSignature("i"), DBusSignature("i")} == {DBusSignature("i")}


def test_signature_is_frozen() -> None:
    sig = DBusSignature("i")
    with pytest.raises(dataclasses.FrozenInstanceError):
        sig.signature = "u"


def test_custom_annotation_round_trips() -> None:
    my_struct = Annotated[tuple[int, str], DBusSignature("(is)")]
    base, sig = get_args(my_struct)
    assert base == tuple[int, str]
    assert sig.signature == "(is)"


def test_all_names_are_exported() -> None:
    for name in annotations.__all__:
        assert hasattr(annotations, name), name
