import logging
import traceback
from typing import Callable, Optional

from .._private.unmarshaller import Unmarshaller
from ..message import Message


def build_message_reader(
    unmarshaller: Unmarshaller,
    process: Callable[[Message], None],
    finalize: Callable[[Optional[Exception]], None],
) -> None:
    """Build a callable that reads messages from the unmarshaller and passes them to the process function."""
    unmarshall = unmarshaller.unmarshall
    reset = unmarshaller.reset

    def _message_reader() -> None:
        """Reads messages from the unmarshaller and passes them to the process function."""
        try:
            while True:
                message = unmarshall()
                if not message:
                    return
                try:
                    process(message)
                except Exception as e:
                    logging.error(
                        f"got unexpected error processing a message: {e}.\n{traceback.format_exc()}"
                    )
                reset()
        except Exception as e:
            finalize(e)

    return _message_reader
