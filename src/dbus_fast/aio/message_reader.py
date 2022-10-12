import logging
import traceback
from typing import Callable, Optional

from .._private.unmarshaller import Unmarshaller
from ..message import Message


def message_reader(
    unmarshaller: Unmarshaller,
    process: Callable[[Message], None],
    finalize: Callable[[Optional[Exception]], None],
) -> None:
    """Reads messages from the unmarshaller and passes them to the process function."""
    try:
        while True:
            message = unmarshaller.unmarshall()
            if not message:
                return
            try:
                process(message)
            except Exception as e:
                logging.error(
                    f"got unexpected error processing a message: {e}.\n{traceback.format_exc()}"
                )
            unmarshaller.reset()
    except Exception as e:
        finalize(e)
