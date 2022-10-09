import array
import io
import socket
import sys
from struct import Struct
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..constants import MESSAGE_FLAG_MAP, MESSAGE_TYPE_MAP
from ..errors import InvalidMessageError
from ..message import Message
from ..signature import SignatureType, Variant, get_signature_tree
from .constants import BIG_ENDIAN, LITTLE_ENDIAN, PROTOCOL_VERSION

IS_LITTLE_ENDIAN = sys.byteorder == "little"
IS_BIG_ENDIAN = sys.byteorder == "big"

MAX_UNIX_FDS = 16

UNPACK_SYMBOL = {LITTLE_ENDIAN: "<", BIG_ENDIAN: ">"}
UNPACK_LENGTHS = {BIG_ENDIAN: Struct(">III"), LITTLE_ENDIAN: Struct("<III")}

UINT32_CAST = "I"
UINT32_SIZE = 4
UINT32_DBUS_TYPE = "u"
UINT32_SIGNATURE = get_signature_tree(UINT32_DBUS_TYPE).types[0]

INT16_CAST = "h"
INT16_SIZE = 2
INT16_DBUS_TYPE = "n"

DBUS_TO_CTYPE = {
    "y": ("B", 1),  # byte
    INT16_DBUS_TYPE: (INT16_CAST, INT16_SIZE),  # int16
    "q": ("H", 2),  # uint16
    "i": ("i", 4),  # int32
    UINT32_DBUS_TYPE: (UINT32_CAST, UINT32_SIZE),  # uint32
    "x": ("q", 8),  # int64
    "t": ("Q", 8),  # uint64
    "d": ("d", 8),  # double
    "h": (UINT32_CAST, UINT32_SIZE),  # uint32
}

UINT32_UNPACK_BY_ENDIAN = {
    LITTLE_ENDIAN: Struct("<I").unpack_from,
    BIG_ENDIAN: Struct(">I").unpack_from,
}

HEADER_SIGNATURE_SIZE = 16
HEADER_ARRAY_OF_STRUCT_SIGNATURE_POSITION = 12


HEADER_MESSAGE_ARG_NAME = {
    1: "path",
    2: "interface",
    3: "member",
    4: "error_name",
    5: "reply_serial",
    6: "destination",
    7: "sender",
    8: "signature",
    9: "unix_fds",
}


READER_TYPE = Callable[["Unmarshaller", SignatureType], Any]


def cast_parser_factory(ctype: str, size: int) -> READER_TYPE:
    """Build a parser that casts the bytes to the given ctype."""

    def _cast_parser(self: "Unmarshaller", signature: SignatureType) -> Any:
        self._pos += size + (-self._pos & (size - 1))  # align
        return self._view[self._pos - size : self._pos].cast(ctype)[0]

    return _cast_parser


def unpack_parser_factory(unpack_from: Callable, size: int) -> READER_TYPE:
    """Build a parser that unpacks the bytes using the given unpack_from function."""

    def _unpack_from_parser(self: "Unmarshaller", signature: SignatureType) -> Any:
        self._pos += size + (-self._pos & (size - 1))  # align
        return unpack_from(self._view, self._pos - size)[0]

    return _unpack_from_parser


def build_simple_parsers(
    endian: int, can_cast: bool
) -> Dict[str, Callable[["Unmarshaller", SignatureType], Any]]:
    """Build a dict of parsers for simple types."""
    parsers: Dict[str, Callable[["Unmarshaller", SignatureType], Any]] = {}
    for dbus_type, ctype_size in DBUS_TO_CTYPE.items():
        ctype, size = ctype_size
        size = ctype_size[1]
        if can_cast:
            parsers[dbus_type] = cast_parser_factory(ctype, size)
        else:
            parsers[dbus_type] = unpack_parser_factory(
                Struct(f"{UNPACK_SYMBOL[endian]}{ctype}").unpack_from, size
            )
    return parsers


class MarshallerStreamEndError(Exception):
    """This exception is raised when the end of the stream is reached.

    This means more data is expected on the wire that has not yet been
    received. The caller should call unmarshall later when more data is
    available.
    """

    pass


#
# Alignment padding is handled with the following formula below
#
# For any align value, the correct padding formula is:
#
#    (align - (pos % align)) % align
#
# However, if align is a power of 2 (always the case here), the slow MOD
# operator can be replaced by a bitwise AND:
#
#    (align - (pos & (align - 1))) & (align - 1)
#
# Which can be simplified to:
#
#    (-pos) & (align - 1)
#
#
class Unmarshaller:

    __slots__ = (
        "_unix_fds",
        "_buf",
        "_view",
        "_pos",
        "_stream",
        "_sock",
        "_message",
        "_readers",
        "_body_len",
        "_serial",
        "_header_len",
        "_message_type",
        "_flag",
        "_msg_len",
        "_uint32_unpack",
    )

    def __init__(self, stream: io.BufferedRWPair, sock=None):
        self._unix_fds: List[int] = []
        self._buf = bytearray()  # Actual buffer
        self._view = None  # Memory view of the buffer
        self._stream = stream
        self._sock = sock
        self._message: Message | None = None
        self._readers: Dict[str, READER_TYPE] = {}
        self._pos = 0
        self._body_len = 0
        self._serial = 0
        self._header_len = 0
        self._message_type = 0
        self._flag = 0
        self._msg_len = 0
        # Only set if we cannot cast
        self._uint32_unpack: Callable | None = None

    def reset(self) -> None:
        """Reset the unmarshaller to its initial state.

        Call this before processing a new message.
        """
        self._unix_fds: List[int] = []
        self._view = None
        self._buf.clear()
        self._message = None
        self._pos = 0
        self._body_len = 0
        self._serial = 0
        self._header_len = 0
        self._message_type = 0
        self._flag = 0
        self._msg_len = 0
        self._uint32_unpack = None

    @property
    def message(self) -> Message:
        """Return the message that has been unmarshalled."""
        return self._message

    def read_sock(self, length: int) -> bytes:
        """reads from the socket, storing any fds sent and handling errors
        from the read itself"""
        unix_fd_list = array.array("i")

        try:
            msg, ancdata, *_ = self._sock.recvmsg(
                length, socket.CMSG_LEN(MAX_UNIX_FDS * unix_fd_list.itemsize)
            )
        except BlockingIOError:
            raise MarshallerStreamEndError()

        for level, type_, data in ancdata:
            if not (level == socket.SOL_SOCKET and type_ == socket.SCM_RIGHTS):
                continue
            unix_fd_list.frombytes(
                data[: len(data) - (len(data) % unix_fd_list.itemsize)]
            )
            self._unix_fds.extend(list(unix_fd_list))

        return msg

    def read_to_pos(self, pos) -> None:
        """
        Read from underlying socket into buffer.

        Raises MarshallerStreamEndError if there is not enough data to be read.

        :arg pos:
            The pos to read to. If not enough bytes are available in the
            buffer, read more from it.

        :returns:
            None
        """
        start_len = len(self._buf)
        missing_bytes = pos - (start_len - self._pos)
        if self._sock is None:
            data = self._stream.read(missing_bytes)
        else:
            data = self.read_sock(missing_bytes)
        if data == b"":
            raise EOFError()
        if data is None:
            raise MarshallerStreamEndError()
        self._buf.extend(data)
        if len(data) + start_len != pos:
            raise MarshallerStreamEndError()

    def read_uint32_cast(self, type_: SignatureType) -> int:
        self._pos += UINT32_SIZE + (-self._pos & (UINT32_SIZE - 1))  # align
        return self._view[self._pos - UINT32_SIZE : self._pos].cast(UINT32_CAST)[0]

    def read_int16_cast(self, type_: SignatureType) -> int:
        self._pos += INT16_SIZE + (-self._pos & (INT16_SIZE - 1))  # align
        return self._view[self._pos - INT16_SIZE : self._pos].cast(INT16_CAST)[0]

    def read_boolean(self, type_: SignatureType) -> bool:
        return bool(self._readers[UINT32_SIGNATURE.token](self, UINT32_SIGNATURE))

    def read_string_cast(self, type_: SignatureType) -> str:
        """Read a string using cast."""
        self._pos += UINT32_SIZE + (-self._pos & (UINT32_SIZE - 1))  # align
        str_start = self._pos
        # read terminating '\0' byte as well (str_length + 1)
        start_pos = self._pos - UINT32_SIZE
        self._pos += self._view[start_pos : self._pos].cast(UINT32_CAST)[0] + 1
        return self._buf[str_start : self._pos - 1].decode()

    def read_string_unpack(self, type_: SignatureType) -> str:
        """Read a string using unpack."""
        self._pos += UINT32_SIZE + (-self._pos & (UINT32_SIZE - 1))  # align
        str_start = self._pos
        # read terminating '\0' byte as well (str_length + 1)
        self._pos += self._uint32_unpack(self._view, str_start - UINT32_SIZE)[0] + 1
        return self._buf[str_start : self._pos - 1].decode()

    def read_signature(self, type_: SignatureType) -> str:
        signature_len = self._buf[self._pos]  # byte
        o = self._pos + 1
        # read terminating '\0' byte as well (str_length + 1)
        self._pos = o + signature_len + 1
        return self._buf[o : o + signature_len].decode()

    def read_variant(self, type_: SignatureType) -> Variant:
        tree = get_signature_tree(self.read_signature(type_))
        signature_type = tree.types[0]
        # verify in Variant is only useful on construction not unmarshalling
        return Variant(
            tree,
            self._readers[signature_type.token](self, signature_type),
            verify=False,
        )

    def read_struct(self, type_: SignatureType) -> List[Any]:
        self._pos += -self._pos & 7  # align 8
        readers = self._readers
        return [
            readers[child_type.token](self, child_type) for child_type in type_.children
        ]

    def read_dict_entry(self, type_: SignatureType) -> Dict[Any, Any]:
        self._pos += -self._pos & 7  # align 8
        return self._readers[type_.children[0].token](
            self, type_.children[0]
        ), self._readers[type_.children[1].token](self, type_.children[1])

    def read_array(self, type_: SignatureType) -> List[Any]:
        self._pos += -self._pos & 3  # align 4 for the array
        self._pos += (
            -self._pos & (UINT32_SIZE - 1)
        ) + UINT32_SIZE  # align for the uint32
        if self._uint32_unpack:
            array_length = self._uint32_unpack(self._view, self._pos - UINT32_SIZE)[0]
        else:
            array_length = self._view[self._pos - UINT32_SIZE : self._pos].cast(
                UINT32_CAST
            )[0]

        child_type = type_.children[0]
        token = child_type.token

        if token in "xtd{(":
            # the first alignment is not included in the array size
            self._pos += -self._pos & 7  # align 8

        if token == "y":
            self._pos += array_length
            return self._buf[self._pos - array_length : self._pos]

        beginning_pos = self._pos
        readers = self._readers

        if token == "{":
            result_dict = {}
            child_0 = child_type.children[0]
            reader_0 = readers[child_0.token]
            child_1 = child_type.children[1]
            reader_1 = readers[child_1.token]
            while self._pos - beginning_pos < array_length:
                self._pos += -self._pos & 7  # align 8
                key = reader_0(self, child_0)
                result_dict[key] = reader_1(self, child_1)
            return result_dict

        result_list = []
        reader = readers[child_type.token]
        while self._pos - beginning_pos < array_length:
            result_list.append(reader(self, child_type))
        return result_list

    def header_fields(self, header_length) -> Dict[str, Any]:
        """Header fields are always a(yv)."""
        beginning_pos = self._pos
        headers = {}
        buf = self._buf
        readers = self._readers
        while self._pos - beginning_pos < header_length:
            # Now read the y (byte) of struct (yv)
            self._pos += (-self._pos & 7) + 1  # align 8 + 1 for 'y' byte
            field_0 = buf[self._pos - 1]

            # Now read the v (variant) of struct (yv)
            signature_len = buf[self._pos]  # byte
            o = self._pos + 1
            self._pos += signature_len + 2  # one for the byte, one for the '\0'
            type_ = get_signature_tree(buf[o : o + signature_len].decode()).types[0]
            headers[HEADER_MESSAGE_ARG_NAME[field_0]] = readers[type_.token](
                self, type_
            )
        return headers

    def _read_header(self) -> None:
        """Read the header of the message."""
        # Signature is of the header is
        # BYTE, BYTE, BYTE, BYTE, UINT32, UINT32, ARRAY of STRUCT of (BYTE,VARIANT)
        self.read_to_pos(HEADER_SIGNATURE_SIZE)
        buffer = self._buf
        endian = buffer[0]
        self._message_type = buffer[1]
        self._flag = buffer[2]
        protocol_version = buffer[3]

        if endian != LITTLE_ENDIAN and endian != BIG_ENDIAN:
            raise InvalidMessageError(
                f"Expecting endianness as the first byte, got {endian} from {buffer}"
            )
        if protocol_version != PROTOCOL_VERSION:
            raise InvalidMessageError(
                f"got unknown protocol version: {protocol_version}"
            )

        self._body_len, self._serial, self._header_len = UNPACK_LENGTHS[
            endian
        ].unpack_from(buffer, 4)
        self._msg_len = (
            self._header_len + (-self._header_len & 7) + self._body_len
        )  # align 8
        can_cast = bool(
            (IS_LITTLE_ENDIAN and endian == LITTLE_ENDIAN)
            or (IS_BIG_ENDIAN and endian == BIG_ENDIAN)
        )
        self._readers = self._readers_by_type[(endian, can_cast)]
        if not can_cast:
            self._uint32_unpack = UINT32_UNPACK_BY_ENDIAN[endian]

    def _read_body(self):
        """Read the body of the message."""
        self.read_to_pos(HEADER_SIGNATURE_SIZE + self._msg_len)
        self._view = memoryview(self._buf)
        self._pos = HEADER_ARRAY_OF_STRUCT_SIGNATURE_POSITION
        header_fields = self.header_fields(self._header_len)
        self._pos += -self._pos & 7  # align 8
        header_fields.pop("unix_fds", None)  # defined by self._unix_fds
        tree = get_signature_tree(header_fields.pop("signature", ""))
        self._message = Message(
            **header_fields,
            message_type=MESSAGE_TYPE_MAP[self._message_type],
            flags=MESSAGE_FLAG_MAP[self._flag],
            unix_fds=self._unix_fds,
            signature=tree,
            body=[self._readers[t.token](self, t) for t in tree.types]
            if self._body_len
            else [],
            serial=self._serial,
            # The D-Bus implementation already validates the message,
            # so we don't need to do it again.
            validate=False,
        )

    def unmarshall(self) -> Optional[Message]:
        """Unmarshall the message.

        The underlying read function will raise MarshallerStreamEndError
        if there are not enough bytes in the buffer. This allows unmarshall
        to be resumed when more data comes in over the wire.
        """
        try:
            if not self._msg_len:
                self._read_header()
            self._read_body()
        except MarshallerStreamEndError:
            return None
        return self._message

    _complex_parsers_unpack: Dict[
        str, Callable[["Unmarshaller", SignatureType], Any]
    ] = {
        "b": read_boolean,
        "o": read_string_unpack,
        "s": read_string_unpack,
        "g": read_signature,
        "a": read_array,
        "(": read_struct,
        "{": read_dict_entry,
        "v": read_variant,
    }

    _complex_parsers_cast: Dict[str, Callable[["Unmarshaller", SignatureType], Any]] = {
        "b": read_boolean,
        "o": read_string_cast,
        "s": read_string_cast,
        "g": read_signature,
        "a": read_array,
        "(": read_struct,
        "{": read_dict_entry,
        "v": read_variant,
        "h": read_uint32_cast,
        UINT32_DBUS_TYPE: read_uint32_cast,
        INT16_DBUS_TYPE: read_int16_cast,
    }

    _ctype_by_endian: Dict[
        Tuple[int, bool], Dict[str, Tuple[None, str, int, Callable]]
    ] = {
        endian_can_cast: build_simple_parsers(*endian_can_cast)
        for endian_can_cast in [
            (LITTLE_ENDIAN, True),
            (LITTLE_ENDIAN, False),
            (BIG_ENDIAN, True),
            (BIG_ENDIAN, False),
        ]
    }

    _readers_by_type: Dict[Tuple[int, bool], READER_TYPE] = {
        (LITTLE_ENDIAN, True): {
            **_ctype_by_endian[(LITTLE_ENDIAN, True)],
            **_complex_parsers_cast,
        },
        (LITTLE_ENDIAN, False): {
            **_ctype_by_endian[(LITTLE_ENDIAN, False)],
            **_complex_parsers_unpack,
        },
        (BIG_ENDIAN, True): {
            **_ctype_by_endian[(BIG_ENDIAN, True)],
            **_complex_parsers_cast,
        },
        (BIG_ENDIAN, False): {
            **_ctype_by_endian[(BIG_ENDIAN, False)],
            **_complex_parsers_unpack,
        },
    }
