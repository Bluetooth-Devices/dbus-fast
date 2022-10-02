"""Test unpack variants."""
import pytest

from dbus_fast.signature import Variant
from dbus_fast.unpack import unpack_variants


@pytest.mark.asyncio
async def test_dictionary():
    """Test variants unpacked from dictionary."""
    assert unpack_variants(
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
    """Test variants unpacked from multiple outputs."""
    assert unpack_variants(
        [{"hello": Variant("s", "world")}, {"boolean": Variant("b", True)}, 1]
    ) == [{"hello": "world"}, {"boolean": True}, 1]


@pytest.mark.asyncio
async def test_nested_variants():
    """Test unpack variants handles nesting."""
    assert unpack_variants(
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
