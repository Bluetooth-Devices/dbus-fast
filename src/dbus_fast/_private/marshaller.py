# cython: freethreading_compatible = True

from __future__ import annotations

from collections.abc import Callable
from struct import Struct, error
from typing import Any

from ..errors import InternalError, InvalidMessageError
from ..signature import SignatureType, Variant, get_signature_tree

PACK_LITTLE_ENDIAN = "<"

PACK_UINT32 = Struct(f"{PACK_LITTLE_ENDIAN}I").pack
PACKED_UINT32_ZERO = PACK_UINT32(0)
PACKED_BOOL_FALSE = PACK_UINT32(0)
PACKED_BOOL_TRUE = PACK_UINT32(1)

# D-Bus spec sec 4.4 caps a single marshalled array at 64 MiB. A larger array
# yields a frame the bus rejects by disconnecting, so fail fast with a clear
# error instead of emitting an invalid message.
#
# MAX_ARRAY_LENGTH is the Python-importable form (used by tests);
# _MAX_ARRAY_LENGTH is the cdef unsigned int form used internally per .pxd.
MAX_ARRAY_LENGTH = 67_108_864
_MAX_ARRAY_LENGTH = MAX_ARRAY_LENGTH

_int = int
_bytes = bytes
_str = str


class Marshaller:
    """Marshall data for Dbus."""

    __slots__ = ("_buf", "body", "signature_tree")

    def __init__(self, signature: str, body: list[Any]) -> None:
        """Marshaller constructor."""
        self.signature_tree = get_signature_tree(signature)
        self._buf = bytearray()
        self.body = body

    def _buffer(self) -> bytearray:
        return self._buf

    def _align(self, n: _int) -> _int:
        offset = n - len(self._buf) % n
        if offset == 0 or offset == n:
            return 0
        for _ in range(offset):
            self._buf.append(0)
        return offset

    def write_boolean(self, boolean: bool, type_: SignatureType) -> int:
        return self._write_boolean(boolean)

    def _write_boolean(self, boolean: bool) -> int:
        written = self._align(4)
        self._buf += PACKED_BOOL_TRUE if boolean else PACKED_BOOL_FALSE
        return written + 4

    def write_signature(self, signature: str, type_: SignatureType) -> int:
        return self._write_signature(signature.encode())

    def _write_signature(self, signature_bytes: _bytes) -> int:
        signature_len = len(signature_bytes)
        buf = self._buf
        buf.append(signature_len)
        buf += signature_bytes
        buf.append(0)
        return signature_len + 2

    def write_string(self, value: _str, type_: SignatureType) -> int:
        return self._write_string(value)

    def _write_string(self, value: _str) -> int:
        value_bytes = value.encode()
        value_len = len(value_bytes)
        written = self._align(4) + 4
        buf = self._buf
        buf += PACK_UINT32(value_len)
        buf += value_bytes
        written += value_len
        buf.append(0)
        written += 1
        return written

    def write_variant(self, variant: Variant, type_: SignatureType) -> int:
        return self._write_variant(variant, type_)

    def _write_variant(self, variant: Variant, type_: SignatureType) -> int:
        signature = variant.signature
        signature_bytes = signature.encode()
        written = self._write_signature(signature_bytes)
        written += self._write_single(variant.type, variant.value)
        return written

    def write_array(
        self, array: bytes | list[Any] | dict[Any, Any], type_: SignatureType
    ) -> int:
        return self._write_array(array, type_)

    def _write_array(
        self, array: bytes | list[Any] | dict[Any, Any], type_: SignatureType
    ) -> int:
        written = self._align(4)
        # length placeholder
        buf: bytearray = self._buf
        offset = len(buf)
        written += self._align(4) + 4
        buf += PACKED_UINT32_ZERO
        child_type = type_.children[0]
        token = child_type.token

        if token in "xtd{(":
            # the first alignment is not included in array size
            written += self._align(8)

        array_len = 0
        if token == "{":
            for key, value in array.items():  # type: ignore[union-attr]
                array_len += self._write_dict_entry_kv(key, value, child_type)
        elif token == "y":
            array_len = len(array)
        elif token == "(":
            for value in array:
                array_len += self._write_struct(value, child_type)
        else:
            writer, packer, size = self._writers[token]
            if not writer:
                for value in array:
                    array_len += self._align(size) + size
                    buf += packer(value)  # type: ignore[misc]
            else:
                for value in array:
                    array_len += writer(self, value, child_type)

        if array_len > _MAX_ARRAY_LENGTH:
            raise InvalidMessageError(
                f"array size {array_len} exceeds maximum {_MAX_ARRAY_LENGTH}"
            )

        # Byte arrays copy in bulk; defer it until the size guard has passed so
        # an oversized payload is rejected without first being copied.
        if token == "y":
            buf += array  # type: ignore[arg-type]

        array_len_packed = PACK_UINT32(array_len)
        for i in range(offset, offset + 4):
            buf[i] = array_len_packed[i - offset]

        return written + array_len

    def write_struct(self, array: tuple[Any] | list[Any], type_: SignatureType) -> int:
        return self._write_struct(array, type_)

    def _write_struct(self, array: tuple[Any] | list[Any], type_: SignatureType) -> int:
        written = self._align(8)
        for i, value in enumerate(array):
            written += self._write_single(type_.children[i], value)
        return written

    def write_dict_entry(self, dict_entry: list[Any], type_: SignatureType) -> int:
        return self._write_dict_entry_kv(dict_entry[0], dict_entry[1], type_)

    def _write_dict_entry_kv(self, key: Any, value: Any, type_: SignatureType) -> int:
        written = self._align(8)
        written += self._write_single(type_.children[0], key)
        written += self._write_single(type_.children[1], value)
        return written

    def _write_single(self, type_: SignatureType, body: Any) -> int:
        t = type_.token
        if t == "y":
            self._buf.append(body)
            return 1
        if t == "u":
            written = self._align(4)
            self._buf += PACK_UINT32(body)
            return written + 4
        if t == "a":
            return self._write_array(body, type_)
        if t == "s" or t == "o":
            return self._write_string(body)
        if t == "v":
            return self._write_variant(body, type_)
        if t == "b":
            return self._write_boolean(body)
        writer, packer, size = self._writers[t]
        if not writer:
            written = self._align(size)
            self._buf += packer(body)  # type: ignore[misc]
            return written + size
        return writer(self, body, type_)

    def marshall(self) -> bytearray:
        """Marshalls the body into a byte array"""
        return self._marshall()

    def _marshall(self) -> bytearray:
        """Marshalls the body into a byte array"""
        try:
            return self._construct_buffer()
        except KeyError as ex:
            raise NotImplementedError(
                f'type is not implemented yet: "{ex.args}"'
            ) from ex
        except error:
            self.signature_tree.verify(self.body)
        raise InternalError("should not reach here")  # pragma: no cover

    def _construct_buffer(self) -> bytearray:
        self._buf.clear()
        body = self.body
        for i, type_ in enumerate(self.signature_tree.types):
            self._write_single(type_, body[i])
        return self._buf

    _writers: dict[
        str,
        tuple[
            Callable[[Any, Any, SignatureType], int] | None,
            Callable[[Any], bytes] | None,
            int,
        ],
    ] = {
        "y": (None, Struct(f"{PACK_LITTLE_ENDIAN}B").pack, 1),
        "b": (write_boolean, None, 0),
        "n": (None, Struct(f"{PACK_LITTLE_ENDIAN}h").pack, 2),
        "q": (None, Struct(f"{PACK_LITTLE_ENDIAN}H").pack, 2),
        "i": (None, Struct(f"{PACK_LITTLE_ENDIAN}i").pack, 4),
        "u": (None, PACK_UINT32, 4),
        "x": (None, Struct(f"{PACK_LITTLE_ENDIAN}q").pack, 8),
        "t": (None, Struct(f"{PACK_LITTLE_ENDIAN}Q").pack, 8),
        "d": (None, Struct(f"{PACK_LITTLE_ENDIAN}d").pack, 8),
        "h": (None, Struct(f"{PACK_LITTLE_ENDIAN}I").pack, 4),
        "o": (write_string, None, 0),
        "s": (write_string, None, 0),
        "g": (write_signature, None, 0),
        "a": (write_array, None, 0),
        "(": (write_struct, None, 0),
        "{": (write_dict_entry, None, 0),
        "v": (write_variant, None, 0),
    }
