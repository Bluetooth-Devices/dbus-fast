from dbus_fast.constants import MESSAGE_FLAG_MAP, MessageFlag


def test_message_flag_map():
    assert 0 in MESSAGE_FLAG_MAP
    assert MessageFlag.NONE in MESSAGE_FLAG_MAP
