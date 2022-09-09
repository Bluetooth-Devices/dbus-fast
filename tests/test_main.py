from dbus_fast.main import add


def test_add():
    assert add(1, 1) == 2
