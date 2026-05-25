import io
import logging

from dbus_fast._private.unmarshaller import Unmarshaller
from dbus_fast.aio.message_reader import _message_reader

# A single valid BlueZ PropertiesChanged frame.
_BLUEZ_MESSAGE_BYTES = bytes.fromhex(
    "6c04010134000000e25389019500000001016f00250000002f6f72672f626c75657a2f686369302f6465"
    "765f30385f33415f46325f31455f32425f3631000000020173001f0000006f72672e667265656465736b"
    "746f702e444275732e50726f7065727469657300030173001100000050726f706572746965734368616e"
    "67656400000000000000080167000873617b73767d617300000007017300040000003a312e3400000000"
    "110000006f72672e626c75657a2e446576696365310000000e0000000000000004000000525353490001"
    "6e00a7ff000000000000"
)


def test_process_exception_is_logged_without_literal_format_token(caplog):
    """A handler exception is logged with its traceback and no stray %s."""
    unmarshaller = Unmarshaller(io.BytesIO(_BLUEZ_MESSAGE_BYTES))

    def process(_message):
        raise RuntimeError("boom")

    finalized = []

    with caplog.at_level(logging.ERROR, logger="dbus_fast.aio.message_reader"):
        _message_reader(unmarshaller, process, finalized.append, False)

    assert finalized == []
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert "%s" not in record.getMessage()
    assert record.exc_info is not None
