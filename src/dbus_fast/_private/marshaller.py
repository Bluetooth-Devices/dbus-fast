from struct import Struct, error
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from ..signature import SignatureType, Variant, get_signature_tree

PACK_UINT32 = Struct("<I").pack


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
        written += 1
        return written

    def write_variant(self, variant: Variant, _=None) -> int:
        written = self.write_signature(variant.signature)
        written += self.write_single(variant.type, variant.value)
        return written

    def write_array(self, array: Iterable[Any], type_: SignatureType) -> int:
        # TODO max array size is 64MiB (67108864 bytes)
        written = self._align(4)
        # length placeholder
        offset = len(self._buf)
        written += self._align(4) + 4
        self._buf.extend(PACK_UINT32(0))
        child_type = type_.children[0]

        if child_type.token in "xtd{(":
            # the first alignment is not included in array size
            written += self._align(8)

        array_len = 0
        if child_type.token == "{":
            for key, value in array.items():
                array_len += self.write_dict_entry([key, value], child_type)
        elif child_type.token == "y":
            array_len = len(array)
            self._buf.extend(array)
        elif child_type.token in self._writers:
            writer, packer, size = self._writers[child_type.token]
            if not writer:
                for value in array:
                    array_len += self._align(size) + size
                    self._buf.extend(packer(value))
            else:
                for value in array:
                    array_len += writer(self, value, child_type)
        else:
            raise NotImplementedError(
                f'type is not implemented yet: "{child_type.token}"'
            )

        array_len_packed = PACK_UINT32(array_len)
        for i in range(offset, offset + 4):
            self._buf[i] = array_len_packed[i - offset]

        return written + array_len

    def write_struct(self, array: List[Any], type_: SignatureType) -> int:
        written = self._align(8)
        for i, value in enumerate(array):
            written += self.write_single(type_.children[i], value)
        return written

    def write_dict_entry(self, dict_entry: List[Any], type_: SignatureType) -> int:
        written = self._align(8)
        written += self.write_single(type_.children[0], dict_entry[0])
        written += self.write_single(type_.children[1], dict_entry[1])
        return written

    def write_single(self, type_: SignatureType, body: Any) -> int:
        t = type_.token

        if t not in self._writers:
            raise NotImplementedError(f'type is not implemented yet: "{t}"')

        writer, packer, size = self._writers[t]
        if not writer:
            written = self._align(size)
            self._buf.extend(packer(body))
            return written + size
        return writer(self, body, type_)

    def marshall(self):
        """Marshalls the body into a byte array"""
        try:
            self._construct_buffer()
        except error:
            self.signature_tree.verify(self.body)
        return self._buf

    def _construct_buffer(self):
        self._buf.clear()
        writers = self._writers
        body = self.body
        buf = self._buf
        for i, type_ in enumerate(self.signature_tree.types):
            t = type_.token
            if t not in writers:
                raise NotImplementedError(f'type is not implemented yet: "{t}"')

            writer, packer, size = writers[t]
            if not writer:
                if size != 1:
                    self._align(size)
                buf.extend(packer(body[i]))
            else:
                writer(self, body[i], type_)

    _writers: Dict[
        str,
        Tuple[
            Optional[Callable[[Any, Any], int]],
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
