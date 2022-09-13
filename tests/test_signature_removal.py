"""Test signature removal."""
import pytest

from dbus_fast.proxy_object import BaseProxyInterface
from dbus_fast.signature import Variant


@pytest.mark.asyncio
async def test_dictionary():
    """Test signature stripped from dictionary."""
    assert BaseProxyInterface.remove_signature(
        {
            "string": Variant("s", "test"),
            "boolean": Variant("b", True),
            "int": Variant("u", 1),
            "object": Variant("o", "/test/path"),
            "array": Variant("as", ["test", "value"]),
            "tuple": Variant("(su)", ["test", 1]),
            "bytes": Variant("ay", b"\0x62\0x75\0x66"),
        }
    ) == {
        "string": "test",
        "boolean": True,
        "int": 1,
        "object": "/test/path",
        "array": ["test", "value"],
        "tuple": ["test", 1],
        "bytes": b"\0x62\0x75\0x66",
    }


@pytest.mark.asyncio
async def test_output_list():
    """Test signature stripping handles multiple outputs."""
    assert BaseProxyInterface.remove_signature(
        [{"hello": Variant("s", "world")}, {"boolean": Variant("b", True)}, 1]
    ) == [{"hello": "world"}, {"boolean": True}, 1]


@pytest.mark.asyncio
async def test_nested_variants():
    """Test signature stripping handles nesting."""
    assert BaseProxyInterface.remove_signature(
        {
            "dict": Variant("a{sv}", {"hello": Variant("s", "world")}),
            "array": Variant(
                "aa{sv}",
                [
                    {"hello": Variant("s", "world")},
                    {"bytes": Variant("ay", b"\0x62\0x75\0x66")},
                ],
            ),
        }
    ) == {
        "dict": {"hello": "world"},
        "array": [{"hello": "world"}, {"bytes": b"\0x62\0x75\0x66"}],
    }
