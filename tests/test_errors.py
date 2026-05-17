"""Tests for the exception hierarchy in ``dbus_fast.errors``.

The hierarchy was introduced to let callers catch every dbus-fast error with
``except DBusFastError`` without giving up the historical ability to catch
specific built-in types like ``ValueError`` or ``TypeError`` for individual
classes (see GH #507).
"""

from __future__ import annotations

import pytest

from dbus_fast import (
    AuthError,
    DBusError,
    DBusFastError,
    InterfaceNotFoundError,
    InternalError,
    InvalidAddressError,
    InvalidBusNameError,
    InvalidInterfaceNameError,
    InvalidIntrospectionError,
    InvalidMemberNameError,
    InvalidMessageError,
    InvalidObjectPathError,
    InvalidSignatureError,
    SignalDisabledError,
    SignatureBodyMismatchError,
)

_ALL_ERRORS = [
    AuthError,
    DBusError,
    InterfaceNotFoundError,
    InternalError,
    InvalidAddressError,
    InvalidBusNameError,
    InvalidInterfaceNameError,
    InvalidIntrospectionError,
    InvalidMemberNameError,
    InvalidMessageError,
    InvalidObjectPathError,
    InvalidSignatureError,
    SignalDisabledError,
    SignatureBodyMismatchError,
]


@pytest.mark.parametrize("err_cls", _ALL_ERRORS)
def test_all_errors_share_dbus_fast_base(err_cls: type[BaseException]) -> None:
    assert issubclass(err_cls, DBusFastError)
    assert issubclass(err_cls, Exception)


@pytest.mark.parametrize(
    "err_cls",
    [
        SignatureBodyMismatchError,
        InvalidSignatureError,
        InvalidAddressError,
        InvalidMessageError,
        InvalidIntrospectionError,
    ],
)
def test_value_error_subclasses_preserved(err_cls: type[BaseException]) -> None:
    assert issubclass(err_cls, ValueError)


@pytest.mark.parametrize(
    "err_cls",
    [
        InvalidBusNameError,
        InvalidObjectPathError,
        InvalidInterfaceNameError,
        InvalidMemberNameError,
    ],
)
def test_type_error_subclasses_preserved(err_cls: type[BaseException]) -> None:
    assert issubclass(err_cls, TypeError)


def test_value_error_subclass_mro_order() -> None:
    """Built-in ``ValueError`` must precede ``DBusFastError`` in the MRO.

    This ordering ensures ``super().__init__`` routes through
    ``ValueError.__init__`` rather than skipping straight to
    ``Exception.__init__``, preserving the behavior of the historical
    single-inheritance ``ValueError`` subclasses.
    """
    mro = InvalidSignatureError.__mro__
    assert mro.index(ValueError) < mro.index(DBusFastError)


def test_type_error_subclass_mro_order() -> None:
    """Built-in ``TypeError`` must precede ``DBusFastError`` in the MRO.

    Same rationale as the ``ValueError`` MRO test: keeps ``super().__init__``
    routing through ``TypeError.__init__`` to match the original
    single-inheritance ``TypeError`` subclasses.
    """
    mro = InvalidBusNameError.__mro__
    assert mro.index(TypeError) < mro.index(DBusFastError)


def test_dbus_fast_error_catches_value_error_subclass() -> None:
    with pytest.raises(DBusFastError):
        raise SignatureBodyMismatchError("body mismatch")


def test_dbus_fast_error_catches_type_error_subclass() -> None:
    with pytest.raises(DBusFastError):
        raise InvalidBusNameError("not.a.valid.bus.name!")


def test_value_error_still_catches_signature_errors() -> None:
    with pytest.raises(ValueError):
        raise InvalidSignatureError("bad signature")


def test_type_error_still_catches_name_errors() -> None:
    with pytest.raises(TypeError):
        raise InvalidMemberNameError("1bad")


def test_invalid_bus_name_error_message_unchanged() -> None:
    err = InvalidBusNameError("bad")
    assert str(err) == "invalid bus name: bad"


def test_invalid_object_path_error_message_unchanged() -> None:
    err = InvalidObjectPathError("nope")
    assert str(err) == "invalid object path: nope"


def test_invalid_interface_name_error_message_unchanged() -> None:
    err = InvalidInterfaceNameError("bad.iface")
    assert str(err) == "invalid interface name: bad.iface"


def test_invalid_member_name_error_message_unchanged() -> None:
    err = InvalidMemberNameError("1bad")
    assert str(err) == "invalid member name: 1bad"


def test_dbus_error_inherits_dbus_fast_error() -> None:
    err = DBusError("org.freedesktop.DBus.Error.Failed", "boom")
    assert isinstance(err, DBusFastError)
    assert err.type == "org.freedesktop.DBus.Error.Failed"
    assert err.text == "boom"


def test_dbus_fast_error_directly_raisable() -> None:
    with pytest.raises(DBusFastError):
        raise DBusFastError("plain base class")


def test_internal_error_is_runtime_error() -> None:
    assert issubclass(InternalError, RuntimeError)


def test_internal_error_is_dbus_fast_error() -> None:
    assert issubclass(InternalError, DBusFastError)


def test_internal_error_mro_order() -> None:
    """``RuntimeError`` must precede ``DBusFastError`` in the MRO.

    Same rationale as the ``ValueError`` / ``TypeError`` MRO tests: keeps
    ``super().__init__`` routing through ``RuntimeError.__init__``.
    """
    mro = InternalError.__mro__
    assert mro.index(RuntimeError) < mro.index(DBusFastError)


def test_runtime_error_still_catches_internal_error() -> None:
    with pytest.raises(RuntimeError):
        raise InternalError("boom")


def test_dbus_fast_error_catches_internal_error() -> None:
    with pytest.raises(DBusFastError):
        raise InternalError("boom")


def test_internal_error_message_unchanged() -> None:
    err = InternalError("internal boom")
    assert str(err) == "internal boom"
