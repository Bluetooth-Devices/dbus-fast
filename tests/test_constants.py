from dbus_fast.constants import MESSAGE_FLAG_MAP, ErrorType, MessageFlag
from dbus_fast.errors import DBusError


def test_message_flag_map():
    assert 0 in MESSAGE_FLAG_MAP
    assert MessageFlag.NONE in MESSAGE_FLAG_MAP


def test_error_type():
    err = DBusError(ErrorType.FAILED, "")
    assert ErrorType.FAILED == err.type
