import pytest

from dbus_fast import (
    is_bus_name_valid,
    is_interface_name_valid,
    is_member_name_valid,
    is_object_path_valid,
)
from dbus_fast.errors import (
    InvalidBusNameError,
    InvalidInterfaceNameError,
    InvalidMemberNameError,
    InvalidObjectPathError,
)
from dbus_fast.validators import (
    assert_bus_name_valid,
    assert_interface_name_valid,
    assert_member_name_valid,
    assert_object_path_valid,
)


def test_object_path_validator():
    valid_paths = ["/", "/foo", "/foo/bar", "/foo/bar/bat"]
    invalid_paths = [
        None,
        "",
        "foo",
        "foo/bar",
        "/foo/bar/",
        "/$/foo/bar",
        "/foo//bar",
        "/foo$bar/baz",
    ]

    for path in valid_paths:
        assert is_object_path_valid(path), f'path should be valid: "{path}"'
    for path in invalid_paths:
        assert not is_object_path_valid(path), f'path should be invalid: "{path}"'


def test_bus_name_validator():
    valid_names = [
        "foo.bar",
        "foo.bar.bat",
        "_foo._bar",
        "foo.bar69",
        "foo.bar-69",
        "org.mpris.MediaPlayer2.google-play-desktop-player",
    ]
    invalid_names = [
        None,
        "",
        "5foo.bar",
        "foo.6bar",
        ".foo.bar",
        "bar..baz",
        "$foo.bar",
        "foo$.ba$r",
    ]

    for name in valid_names:
        assert is_bus_name_valid(name), f'bus name should be valid: "{name}"'
    for name in invalid_names:
        assert not is_bus_name_valid(name), f'bus name should be invalid: "{name}"'


def test_interface_name_validator():
    valid_names = ["foo.bar", "foo.bar.bat", "_foo._bar", "foo.bar69"]
    invalid_names = [
        None,
        "",
        "5foo.bar",
        "foo.6bar",
        ".foo.bar",
        "bar..baz",
        "$foo.bar",
        "foo$.ba$r",
        "org.mpris.MediaPlayer2.google-play-desktop-player",
    ]

    for name in valid_names:
        assert is_interface_name_valid(name), (
            f'interface name should be valid: "{name}"'
        )
    for name in invalid_names:
        assert not is_interface_name_valid(name), (
            f'interface name should be invalid: "{name}"'
        )


def test_member_name_validator():
    valid_members = ["foo", "FooBar", "Bat_Baz69", "foo-bar"]
    invalid_members = [None, "", "foo.bar", "5foo", "foo$bar"]

    for member in valid_members:
        assert is_member_name_valid(member), f'member name should be valid: "{member}"'
    for member in invalid_members:
        assert not is_member_name_valid(member), (
            f'member name should be invalid: "{member}"'
        )


def test_bus_name_requires_dot():
    """A single-element well-known bus name (no '.') is invalid."""
    assert not is_bus_name_valid("foo")


def test_unique_bus_name_is_valid():
    """Unique bus names start with ':' and bypass element validation."""
    assert is_bus_name_valid(":1.42")
    assert is_bus_name_valid(":1.0")


def test_bus_name_max_length():
    """Bus names must not exceed 255 characters."""
    name_255 = "a." + "b" * 253
    name_256 = "a." + "b" * 254
    assert len(name_255) == 255
    assert len(name_256) == 256
    assert is_bus_name_valid(name_255)
    assert not is_bus_name_valid(name_256)


def test_interface_name_max_length():
    """Interface names must not exceed 255 characters."""
    name_255 = "a." + "b" * 253
    name_256 = "a." + "b" * 254
    assert is_interface_name_valid(name_255)
    assert not is_interface_name_valid(name_256)


def test_interface_name_requires_dot():
    """A single-element name without '.' is not a valid interface name."""
    assert not is_interface_name_valid("foo")


def test_member_name_max_length():
    """Member names must not exceed 255 characters."""
    member_255 = "a" * 255
    member_256 = "a" * 256
    assert is_member_name_valid(member_255)
    assert not is_member_name_valid(member_256)


def test_assert_bus_name_valid():
    """assert_bus_name_valid returns None for valid names, raises for invalid."""
    assert assert_bus_name_valid("foo.bar") is None
    assert assert_bus_name_valid(":1.42") is None
    with pytest.raises(InvalidBusNameError):
        assert_bus_name_valid("5foo.bar")
    with pytest.raises(InvalidBusNameError):
        assert_bus_name_valid(".foo")


def test_assert_object_path_valid():
    """assert_object_path_valid returns None for valid paths, raises for invalid."""
    assert assert_object_path_valid("/") is None
    assert assert_object_path_valid("/foo/bar") is None
    with pytest.raises(InvalidObjectPathError):
        assert_object_path_valid("foo")
    with pytest.raises(InvalidObjectPathError):
        assert_object_path_valid("/foo/bar/")


def test_assert_interface_name_valid():
    """assert_interface_name_valid returns None for valid names, raises for invalid."""
    assert assert_interface_name_valid("foo.bar") is None
    with pytest.raises(InvalidInterfaceNameError):
        assert_interface_name_valid("foo")
    with pytest.raises(InvalidInterfaceNameError):
        assert_interface_name_valid("5foo.bar")


def test_assert_member_name_valid():
    """assert_member_name_valid returns None for valid names, raises for invalid."""
    assert assert_member_name_valid("Foo") is None
    assert assert_member_name_valid("foo-bar") is None
    with pytest.raises(InvalidMemberNameError):
        assert_member_name_valid("5foo")
    with pytest.raises(InvalidMemberNameError):
        assert_member_name_valid("foo.bar")
