import io
import logging
import socket
import traceback
from typing import Callable, Optional

from .._private.unmarshaller import Unmarshaller
from ..message import Message


def build_message_reader(
    stream: io.BufferedRWPair,
    sock: Optional[socket.socket],
    process: Callable[[Message], None],
    finalize: Callable[[Optional[Exception]], None],
) -> None:
    """Build a callable that reads messages from the unmarshaller and passes them to the process function."""
    unmarshaller = Unmarshaller(stream, sock)
    _tell = stream.tell if not sock else None

    def _message_reader() -> None:
        """Reads messages from the unmarshaller and passes them to the process function."""
        try:
            while True:
                message = unmarshaller._unmarshall()
                if not message:
                    return
                try:
                    process(message)
                except Exception as e:
                    logging.error(
                        "Unexpected error processing message: %s", e, exc_info=True
                    )
                unmarshaller._reset()
                if _tell:
                    logging.error("After read tell: %s", _tell())
        except Exception as e:
            finalize(e)

    return _message_reader
