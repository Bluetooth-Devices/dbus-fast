from struct import Struct, error
from typing import Any, Callable, Dict, Iterable, List, Tuple

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
    def buffer(self):
        return self._buf

    def align(self, n) -> int:
        return self._align(n)

    def _align(self, n) -> int:
        offset = n - len(self._buf) % n
        if offset == 0 or offset == n:
            return 0
        self._buf.extend(bytes(offset))
        return offset

    def write_boolean(self, boolean: bool, _=None) -> int:
        written = self._align(4)
        self._buf.extend(PACK_UINT32(int(boolean)))
        return written + 4

    def write_signature(self, signature: str, _=None) -> int:
        return self._write_signature(signature)

    def _write_signature(self, signature) -> int:
        signature_bytes = signature.encode()
        signature_len = len(signature)
        self._buf.append(signature_len)
        self._buf.extend(signature_bytes)
        self._buf.append(0)
        return signature_len + 2

    def write_string(self, value, _=None) -> int:
        value_bytes = value.encode()
        value_len = len(value)
        written = self._align(4) + 4
        self._buf.extend(PACK_UINT32(value_len))
        self._buf.extend(value_bytes)
        written += value_len
        self._buf.append(0)
        return written + 1

    def write_variant(self, variant: Variant, _=None) -> int:
        written = self._write_signature(variant.signature)
        written += self._write_single(variant.type, variant.value)
        return written

    def write_array(self, array: Iterable[Any], type_: SignatureType) -> int:
        # TODO max array size is 64MiB (67108864 bytes)
        written = self._align(4)
        buf = self._buf
        # length placeholder
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
            for key, value in array.items():
                array_len += self.write_dict_entry([key, value], child_type)
        elif token == "y":
            array_len = len(array)
            buf.extend(array)
        else:
            writer_size = self._writers.get(token)
            if not writer_size:
                raise NotImplementedError(f'type is not implemented yet: "{token}"')
            writer, size = writer_size
            if size:
                for value in array:
                    array_len += self._align(size) + size
                    buf.extend(writer(value))
            else:
                for value in array:
                    array_len += writer(self, value, child_type)

        array_len_packed = PACK_UINT32(array_len)
        for i in range(offset, offset + 4):
            buf[i] = array_len_packed[i - offset]

        return written + array_len

    def write_struct(self, array: List[Any], type_: SignatureType) -> int:
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
        writer_size = self._writers.get(type_.token)
        if not writer_size:
            raise NotImplementedError(f'type is not implemented yet: "{type_.token}"')

        writer, size = writer_size
        if size:
            written = 0 if size == 1 else self._align(size)
            self._buf.extend(writer(body))
            return written + size
        return writer(self, body, type_)

    def marshall(self):
        """Marshalls the body into a byte array"""
        self._buf.clear()
        body = self.body
        try:
            for type_ in self.signature_tree.types:
                self._write_single(type_, body)
        except error:
            self.signature_tree.verify(self.body)
        return self._buf

    _writers: Dict[str, Tuple[Callable, int],] = {
        "y": (Struct("<B").pack, 1),
        "b": (write_boolean, 0),
        "n": (Struct("<h").pack, 2),
        "q": (Struct("<H").pack, 2),
        "i": (Struct("<i").pack, 4),
        "u": (PACK_UINT32, 4),
        "x": (Struct("<q").pack, 8),
        "t": (Struct("<Q").pack, 8),
        "d": (Struct("<d").pack, 8),
        "h": (Struct("<I").pack, 4),
        "o": (write_string, 0),
        "s": (write_string, 0),
        "g": (write_signature, 0),
        "a": (write_array, 0),
        "(": (write_struct, 0),
        "{": (write_dict_entry, 0),
        "v": (write_variant, 0),
    }
