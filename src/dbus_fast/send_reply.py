from __future__ import annotations

import logging
from types import TracebackType
from typing import TYPE_CHECKING

from .constants import ErrorType
from .errors import DBusError
from .message import Message

if TYPE_CHECKING:
    from .message_bus import BaseMessageBus

_LOGGER = logging.getLogger(__name__)


class SendReply:
    """A context manager to send a reply to a message."""

    __slots__ = ("_bus", "_msg")

    def __init__(self, bus: BaseMessageBus, msg: Message) -> None:
        """Create a new reply context manager."""
        self._bus = bus
        self._msg = msg

    def __enter__(self) -> SendReply:
        return self

    def __call__(self, reply: Message) -> None:
        self._bus.send(reply)

    def _exit(
        self,
        exc_type: type[Exception] | None,
        exc_value: Exception | None,
        tb: TracebackType | None,
    ) -> bool:
        if exc_value:
            if isinstance(exc_value, DBusError):
                self(exc_value._as_message(self._msg))
            else:
                # Log the traceback for the operator; never send it back to
                # the caller — it discloses install paths, line numbers,
                # locals and version fingerprints to any peer that can
                # invoke a method on this service.
                _LOGGER.exception(
                    "Service interface raised an exception",
                    exc_info=(exc_type, exc_value, tb),
                )
                self(
                    Message.new_error(
                        self._msg,
                        ErrorType.SERVICE_ERROR,
                        f"The service interface raised an error: {type(exc_value).__name__}",
                    )
                )
            return True

        return False

    def __exit__(
        self,
        exc_type: type[Exception] | None,
        exc_value: Exception | None,
        tb: TracebackType | None,
    ) -> bool:
        return self._exit(exc_type, exc_value, tb)

    def send_error(self, exc: Exception) -> None:
        self._exit(exc.__class__, exc, exc.__traceback__)
