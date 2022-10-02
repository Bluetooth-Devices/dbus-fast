import array
import io
import socket
import sys
from struct import Struct
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..constants import MESSAGE_FLAG_MAP, MESSAGE_TYPE_MAP, MessageFlag, MessageType
from ..errors import InvalidMessageError
from ..message import Message
from ..signature import SignatureTree, SignatureType, Variant
from .constants import (
    BIG_ENDIAN,
    HEADER_NAME_MAP,
    LITTLE_ENDIAN,
    PROTOCOL_VERSION,
    HeaderField,
)

IS_LITTLE_ENDIAN = sys.byteorder == "little"
IS_BIG_ENDIAN = sys.byteorder == "big"

MAX_UNIX_FDS = 16

UNPACK_SYMBOL = {LITTLE_ENDIAN: "<", BIG_ENDIAN: ">"}
UNPACK_LENGTHS = {BIG_ENDIAN: Struct(">III"), LITTLE_ENDIAN: Struct("<III")}

UINT32_CAST = "I"
UINT32_SIZE = 4
UINT32_DBUS_TYPE = "u"
UINT32_SIGNATURE = SignatureTree._get(UINT32_DBUS_TYPE).types[0]

DBUS_TO_CTYPE = {
    "y": ("B", 1),  # byte
    "n": ("h", 2),  # int16
    "q": ("H", 2),  # uint16
    "i": ("i", 4),  # int32
    UINT32_DBUS_TYPE: (UINT32_CAST, UINT32_SIZE),  # uint32
    "x": ("q", 8),  # int64
    "t": ("Q", 8),  # uint64
    "d": ("d", 8),  # double
    "h": ("I", 4),  # uint32
}

UINT32_UNPACK_BY_ENDIAN = {
    LITTLE_ENDIAN: Struct("<I").unpack_from,
    BIG_ENDIAN: Struct(">I").unpack_from,
}

HEADER_SIGNATURE_SIZE = 16
HEADER_ARRAY_OF_STRUCT_SIGNATURE_POSITION = 12

HEADER_DESTINATION = HeaderField.DESTINATION.name
HEADER_PATH = HeaderField.PATH.name
HEADER_INTERFACE = HeaderField.INTERFACE.name
HEADER_MEMBER = HeaderField.MEMBER.name
HEADER_ERROR_NAME = HeaderField.ERROR_NAME.name
HEADER_REPLY_SERIAL = HeaderField.REPLY_SERIAL.name
HEADER_SENDER = HeaderField.SENDER.name

READER_TYPE = Callable[["Unmarshaller", SignatureType], Any]


def cast_parser_factory(ctype: str, size: int) -> READER_TYPE:
    """Build a parser that casts the bytes to the given ctype."""

    def _cast_parser(self: "Unmarshaller", signature: SignatureType) -> Any:
        self.pos += size + (-self.pos & (size - 1))  # align
        return self.view[self.pos - size : self.pos].cast(ctype)[0]

    return _cast_parser


def unpack_parser_factory(unpack_from: Callable, size: int) -> READER_TYPE:
    """Build a parser that unpacks the bytes using the given unpack_from function."""

    def _unpack_from_parser(self: "Unmarshaller", signature: SignatureType) -> Any:
        self.pos += size + (-self.pos & (size - 1))  # align
        return unpack_from(self.view, self.pos - size)[0]

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
        "unix_fds",
        "buf",
        "view",
        "pos",
        "stream",
        "sock",
        "_message",
        "readers",
        "body_len",
        "serial",
        "header_len",
        "message_type",
        "flag",
        "msg_len",
        "_uint32_unpack",
    )

    def __init__(self, stream: io.BufferedRWPair, sock=None):
        self.unix_fds: List[int] = []
        self.buf = bytearray()  # Actual buffer
        self.view = None  # Memory view of the buffer
        self.pos = 0
        self.stream = stream
        self.sock = sock
        self._message: Message | None = None
        self.readers: Dict[str, READER_TYPE] = {}
        self.body_len = 0
        self.serial = 0
        self.header_len = 0
        self.message_type: MessageType | None = None
        self.flag: MessageFlag | None = None
        self.msg_len = 0
        # Only set if we cannot cast
        self._uint32_unpack: Callable | None = None

    @property
    def message(self) -> Message:
        """Return the message that has been unmarshalled."""
        return self._message

    def read_sock(self, length: int) -> bytes:
        """reads from the socket, storing any fds sent and handling errors
        from the read itself"""
        unix_fd_list = array.array("i")

        try:
            msg, ancdata, *_ = self.sock.recvmsg(
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
            self.unix_fds.extend(list(unix_fd_list))

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
        start_len = len(self.buf)
        missing_bytes = pos - (start_len - self.pos)
        if self.sock is None:
            data = self.stream.read(missing_bytes)
        else:
            data = self.read_sock(missing_bytes)
        if data == b"":
            raise EOFError()
        if data is None:
            raise MarshallerStreamEndError()
        self.buf.extend(data)
        if len(data) + start_len != pos:
            raise MarshallerStreamEndError()

    def read_boolean(self, type_=None) -> bool:
        return bool(self.readers[UINT32_SIGNATURE.token](self, UINT32_SIGNATURE))

    def read_string_cast(self, type_=None) -> str:
        """Read a string using cast."""
        self.pos += UINT32_SIZE + (-self.pos & (UINT32_SIZE - 1))  # align
        str_start = self.pos
        # read terminating '\0' byte as well (str_length + 1)
        start_pos = self.pos - UINT32_SIZE
        self.pos += self.view[start_pos : self.pos].cast(UINT32_CAST)[0] + 1
        end_pos = self.pos - 1
        return self.buf[str_start:end_pos].decode()

    def read_string_unpack(self, type_=None) -> str:
        """Read a string using unpack."""
        self.pos += UINT32_SIZE + (-self.pos & (UINT32_SIZE - 1))  # align
        str_start = self.pos
        # read terminating '\0' byte as well (str_length + 1)
        self.pos += self._uint32_unpack(self.view, str_start - UINT32_SIZE)[0] + 1
        return self.buf[str_start : self.pos - 1].decode()

    def read_signature(self, type_=None) -> str:
        signature_len = self.view[self.pos]  # byte
        o = self.pos + 1
        # read terminating '\0' byte as well (str_length + 1)
        self.pos = o + signature_len + 1
        return self.buf[o : o + signature_len].decode()

    def read_variant(self, type_=None) -> Variant:
        tree = SignatureTree._get(self.read_signature())
        # verify in Variant is only useful on construction not unmarshalling
        return Variant(
            tree, self.readers[tree.types[0].token](self, tree.types[0]), verify=False
        )

    def read_struct(self, type_=None) -> List[Any]:
        self.pos += -self.pos & 7  # align 8
        readers = self.readers
        return [
            readers[child_type.token](self, child_type) for child_type in type_.children
        ]

    def read_dict_entry(self, type_: SignatureType) -> Dict[Any, Any]:
        self.pos += -self.pos & 7  # align 8
        return self.readers[type_.children[0].token](
            self, type_.children[0]
        ), self.readers[type_.children[1].token](self, type_.children[1])

    def read_array(self, type_: SignatureType) -> List[Any]:
        self.pos += -self.pos & 3  # align 4 for the array
        self.pos += (
            -self.pos & (UINT32_SIZE - 1)
        ) + UINT32_SIZE  # align for the uint32
        if self._uint32_unpack:
            array_length = self._uint32_unpack(self.view, self.pos - UINT32_SIZE)[0]
        else:
            array_length = self.view[self.pos - UINT32_SIZE : self.pos].cast(
                UINT32_CAST
            )[0]

        child_type = type_.children[0]
        if child_type.token in "xtd{(":
            # the first alignment is not included in the array size
            self.pos += -self.pos & 7  # align 8

        if child_type.token == "y":
            self.pos += array_length
            return self.buf[self.pos - array_length : self.pos]

        beginning_pos = self.pos
        readers = self.readers

        if child_type.token == "{":
            result_dict = {}
            while self.pos - beginning_pos < array_length:
                self.pos += -self.pos & 7  # align 8
                key = readers[child_type.children[0].token](
                    self, child_type.children[0]
                )
                result_dict[key] = readers[child_type.children[1].token](
                    self, child_type.children[1]
                )
            return result_dict

        result_list = []
        while self.pos - beginning_pos < array_length:
            result_list.append(readers[child_type.token](self, child_type))
        return result_list

    def header_fields(self, header_length) -> Dict[str, Any]:
        """Header fields are always a(yv)."""
        beginning_pos = self.pos
        headers = {}
        while self.pos - beginning_pos < header_length:
            # Now read the y (byte) of struct (yv)
            self.pos += (-self.pos & 7) + 1  # align 8 + 1 for 'y' byte
            field_0 = self.view[self.pos - 1]

            # Now read the v (variant) of struct (yv)
            signature_len = self.view[self.pos]  # byte
            o = self.pos + 1
            self.pos += signature_len + 2  # one for the byte, one for the '\0'
            tree = SignatureTree._get(self.buf[o : o + signature_len].decode())
            headers[HEADER_NAME_MAP[field_0]] = self.readers[tree.types[0].token](
                self, tree.types[0]
            )
        return headers

    def _read_header(self) -> None:
        """Read the header of the message."""
        # Signature is of the header is
        # BYTE, BYTE, BYTE, BYTE, UINT32, UINT32, ARRAY of STRUCT of (BYTE,VARIANT)
        self.read_to_pos(HEADER_SIGNATURE_SIZE)
        buffer = self.buf
        endian = buffer[0]
        self.message_type = MESSAGE_TYPE_MAP[buffer[1]]
        self.flag = MESSAGE_FLAG_MAP[buffer[2]]
        protocol_version = buffer[3]

        if endian != LITTLE_ENDIAN and endian != BIG_ENDIAN:
            raise InvalidMessageError(
                f"Expecting endianness as the first byte, got {endian} from {buffer}"
            )
        if protocol_version != PROTOCOL_VERSION:
            raise InvalidMessageError(
                f"got unknown protocol version: {protocol_version}"
            )

        self.body_len, self.serial, self.header_len = UNPACK_LENGTHS[
            endian
        ].unpack_from(buffer, 4)
        self.msg_len = (
            self.header_len + (-self.header_len & 7) + self.body_len
        )  # align 8
        can_cast = bool(
            (IS_LITTLE_ENDIAN and endian == LITTLE_ENDIAN)
            or (IS_BIG_ENDIAN and endian == BIG_ENDIAN)
        )
        self.readers = self._readers_by_type[(endian, can_cast)]
        if not can_cast:
            self._uint32_unpack = UINT32_UNPACK_BY_ENDIAN[endian]

    def _read_body(self):
        """Read the body of the message."""
        self.read_to_pos(HEADER_SIGNATURE_SIZE + self.msg_len)
        self.view = memoryview(self.buf)
        self.pos = HEADER_ARRAY_OF_STRUCT_SIGNATURE_POSITION
        header_fields = self.header_fields(self.header_len)
        self.pos += -self.pos & 7  # align 8
        tree = SignatureTree._get(header_fields.get(HeaderField.SIGNATURE.name, ""))
        self._message = Message(
            destination=header_fields.get(HEADER_DESTINATION),
            path=header_fields.get(HEADER_PATH),
            interface=header_fields.get(HEADER_INTERFACE),
            member=header_fields.get(HEADER_MEMBER),
            message_type=self.message_type,
            flags=self.flag,
            error_name=header_fields.get(HEADER_ERROR_NAME),
            reply_serial=header_fields.get(HEADER_REPLY_SERIAL),
            sender=header_fields.get(HEADER_SENDER),
            unix_fds=self.unix_fds,
            signature=tree.signature,
            body=[self.readers[t.token](self, t) for t in tree.types]
            if self.body_len
            else [],
            serial=self.serial,
            # The D-Bus implementation already validates the message,
            # so we don't need to do it again.
            validate=False,
        )

    def unmarshall(self):
        """Unmarshall the message.

        The underlying read function will raise MarshallerStreamEndError
        if there are not enough bytes in the buffer. This allows unmarshall
        to be resumed when more data comes in over the wire.
        """
        try:
            if not self.message_type:
                self._read_header()
            self._read_body()
        except MarshallerStreamEndError:
            return None
        return self.message

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
