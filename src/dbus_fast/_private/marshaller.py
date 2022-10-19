from struct import Struct, error
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

from ..signature import SignatureType, Variant, get_signature_tree

PACK_UINT32 = Struct("<I").pack
PACKED_UINT32_ZERO = PACK_UINT32(0)


class Marshaller:
    """Marshall data for Dbus."""

    __slots__ = ("signature_tree", "_buf", "body")

    def __init__(self, signature: str, body: List[Any]) -> None:
        """Marshaller constructor."""
        self.signature_tree = get_signature_tree(signature)
        self._buf = bytearray()
        self.body = body

    @property
    def buffer(self) -> bytearray:
        return self._buf

    def align(self, n):
        return self._align(n)

    def _align(self, n):
        offset = n - len(self._buf) % n
        if offset == 0 or offset == n:
            return 0
        self._buf.extend(bytes(offset))
        return offset

    def write_boolean(self, boolean: bool, type_: SignatureType) -> int:
        written = self._align(4)
        self._buf.extend(PACK_UINT32(int(boolean)))
        return written + 4

    def write_signature(self, signature: str, type_: SignatureType) -> int:
        return self._write_signature(signature.encode())

    def _write_signature(self, signature_bytes) -> int:
        signature_len = len(signature_bytes)
        buf = self._buf
        buf.append(signature_len)
        buf.extend(signature_bytes)
        buf.append(0)
        return signature_len + 2

    def write_string(self, value, type_: SignatureType) -> int:
        value_bytes = value.encode()
        value_len = len(value)
        written = self._align(4) + 4
        buf = self._buf
        buf.extend(PACK_UINT32(value_len))
        buf.extend(value_bytes)
        written += value_len
        buf.append(0)
        written += 1
        return written

    def write_variant(self, variant: Variant, type_: SignatureType) -> int:
        written = self._write_signature(variant.signature.encode())
        written += self._write_single(variant.type, variant.value)
        return written

    def write_array(
        self, array: Union[List[Any], Dict[Any, Any]], type_: SignatureType
    ) -> int:
        return self._write_array(array, type_)

    def _write_array(
        self, array: Union[List[Any], Dict[Any, Any]], type_: SignatureType
    ) -> int:
        # TODO max array size is 64MiB (67108864 bytes)
        written = self._align(4)
        # length placeholder
        buf = self._buf
        offset = len(buf)
        written += self._align(4) + 4
        buf.extend(PACKED_UINT32_ZERO)
        child_type = type_.children[0]
        token = child_type.token

        if token in "xtd{(":
            # the first alignment is not included in array size
            written += self._align(8)

        array_len = 0
        if token == "{":
            for key, value in array.items():  # type: ignore[union-attr]
                array_len += self.write_dict_entry([key, value], child_type)
        elif token == "y":
            array_len = len(array)
            buf.extend(array)
        elif token == "(":
            for value in array:
                array_len += self._write_struct(value, child_type)
        else:
            writer, packer, size = self._writers[token]
            if not writer:
                for value in array:
                    array_len += self._align(size) + size
                    buf.extend(packer(value))  # type: ignore[misc]
            else:
                for value in array:
                    array_len += writer(self, value, child_type)

        array_len_packed = PACK_UINT32(array_len)
        for i in range(offset, offset + 4):
            buf[i] = array_len_packed[i - offset]

        return written + array_len

    def write_struct(self, array: List[Any], type_: SignatureType) -> int:
        return self._write_struct(array, type_)

    def _write_struct(self, array: List[Any], type_: SignatureType) -> int:
        written = self._align(8)
        for i, value in enumerate(array):
            written += self._write_single(type_.children[i], value)
        return written

    def write_dict_entry(self, dict_entry: List[Any], type_: SignatureType) -> int:
        written = self._align(8)
        written += self._write_single(type_.children[0], dict_entry[0])
        written += self._write_single(type_.children[1], dict_entry[1])
        return written

    def _write_single(self, type_: SignatureType, body: Any) -> int:
        t = type_.token
        writer, packer, size = self._writers[t]
        if not writer:
            written = self._align(size)
            self._buf.extend(packer(body))  # type: ignore[misc]
            return written + size
        return writer(self, body, type_)

    def marshall(self) -> bytearray:
        """Marshalls the body into a byte array"""
        try:
            self._construct_buffer()
        except KeyError as ex:
            raise NotImplementedError(f'type is not implemented yet: "{ex.args}"')
        except error:
            self.signature_tree.verify(self.body)
        return self._buf

    def _construct_buffer(self) -> None:
        self._buf.clear()
        writers = self._writers
        body = self.body
        buf = self._buf
        for i, type_ in enumerate(self.signature_tree.types):
            t = type_.token
            if t == "y":
                buf.append(body[i])
            elif t == "u":
                self._align(4)
                buf.extend(PACK_UINT32(body[i]))
            elif t == "a":
                self._write_array(body[i], type_)
            else:
                writer, packer, size = writers[t]
                if not writer:
                    if size != 1:
                        self._align(size)
                    buf.extend(packer(body[i]))  # type: ignore[misc]
                else:
                    writer(self, body[i], type_)

    _writers: Dict[
        str,
        Tuple[
            Optional[Callable[[Any, Any, SignatureType], int]],
            Optional[Callable[[Any], bytes]],
            int,
        ],
    ] = {
        "y": (None, Struct("<B").pack, 1),
        "b": (write_boolean, None, 0),
        "n": (None, Struct("<h").pack, 2),
        "q": (None, Struct("<H").pack, 2),
        "i": (None, Struct("<i").pack, 4),
        "u": (None, PACK_UINT32, 4),
        "x": (None, Struct("<q").pack, 8),
        "t": (None, Struct("<Q").pack, 8),
        "d": (None, Struct("<d").pack, 8),
        "h": (None, Struct("<I").pack, 4),
        "o": (write_string, None, 0),
        "s": (write_string, None, 0),
        "g": (write_signature, None, 0),
        "a": (write_array, None, 0),
        "(": (write_struct, None, 0),
        "{": (write_dict_entry, None, 0),
        "v": (write_variant, None, 0),
    }
