class DBusFastError(Exception):
    """Common base class for all dbus-fast exceptions.

    Catch this to handle any error raised by dbus-fast regardless of which
    Python built-in exception type the specific error also derives from.
    Existing ``except ValueError`` / ``except TypeError`` handlers continue
    to work because individual error classes still inherit from those.
    """


class SignatureBodyMismatchError(ValueError, DBusFastError):
    pass


class InvalidSignatureError(ValueError, DBusFastError):
    pass


class InvalidAddressError(ValueError, DBusFastError):
    pass


class AuthError(ValueError, DBusFastError):
    pass


class InternalError(RuntimeError, DBusFastError):
    """Indicates a bug inside dbus-fast itself."""


class InvalidMessageError(ValueError, DBusFastError):
    pass


class InvalidIntrospectionError(ValueError, DBusFastError):
    pass


class InterfaceNotFoundError(DBusFastError):
    pass


class SignalDisabledError(DBusFastError):
    pass


class InvalidBusNameError(TypeError, DBusFastError):
    def __init__(self, name: str) -> None:
        super().__init__(f"invalid bus name: {name}")


class InvalidObjectPathError(TypeError, DBusFastError):
    def __init__(self, path: str) -> None:
        super().__init__(f"invalid object path: {path}")


class InvalidInterfaceNameError(TypeError, DBusFastError):
    def __init__(self, name: str) -> None:
        super().__init__(f"invalid interface name: {name}")


class InvalidMemberNameError(TypeError, DBusFastError):
    def __init__(self, member: str) -> None:
        super().__init__(f"invalid member name: {member}")


from .constants import ErrorType, MessageType  # noqa: E402
from .message import Message  # noqa: E402
from .validators import assert_interface_name_valid  # noqa: E402


class DBusError(DBusFastError):
    def __init__(
        self, type_: ErrorType | str, text: str, reply: Message | None = None
    ) -> None:
        super().__init__(text)

        if type(type_) is ErrorType:
            type_ = type_.value

        assert_interface_name_valid(type_)  # type: ignore[arg-type]
        if reply is not None and type(reply) is not Message:
            raise TypeError("reply must be of type Message")

        self.type = type_
        self.text = text
        self.reply = reply

    @staticmethod
    def _from_message(msg: Message) -> "DBusError":
        assert msg.message_type == MessageType.ERROR
        return DBusError(msg.error_name or "unknown", msg.body[0], reply=msg)

    def _as_message(self, msg: Message) -> Message:
        return Message.new_error(msg, self.type, self.text)
