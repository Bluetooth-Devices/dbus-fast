import io
import logging
import socket
import traceback
from typing import Callable, Optional

from .._private.unmarshaller import Unmarshaller
from ..message import Message


def build_message_reader(
    sock: Optional[socket.socket],
    process: Callable[[Message], None],
    finalize: Callable[[Optional[Exception]], None],
    negotiate_unix_fd: bool,
) -> None:
    """Build a callable that reads messages from the unmarshaller and passes them to the process function."""
    unmarshaller = Unmarshaller(None, sock, negotiate_unix_fd)

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
                        f"got unexpected error processing a message: {e}.\n{traceback.format_exc()}"
                    )
                # If we are not negotiating unix fds, we can stop reading as soon as we have
                # the buffer is empty as asyncio will call us again when there is more data.
                if (
                    not negotiate_unix_fd
                    and not unmarshaller._has_another_message_in_buffer()
                ):
                    return
        except Exception as e:
            finalize(e)

    return _message_reader
