from struct import Struct, error, pack
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from ..signature import SignatureTree, SignatureType, Variant

PACK_UINT32 = Struct("<I").pack


class Marshaller:
    def __init__(self, signature: str, body: Any) -> None:
        self.signature_tree = SignatureTree._get(signature)
        self.buffer = bytearray()
        self.body = body

    def align(self, n) -> int:
        offset = n - len(self.buffer) % n
        if offset == 0 or offset == n:
            return 0
        self.buffer.extend(bytes(offset))
        return offset

    def write_boolean(self, boolean: bool, _=None) -> int:
        written = self.align(4)
        self.buffer.extend(PACK_UINT32(int(boolean)))
        return written + 4

    def write_signature(self, signature: str, _=None) -> int:
        signature = signature.encode()
        signature_len = len(signature)
        self.buffer.append(signature_len)
        self.buffer.extend(signature)
        self.buffer.append(0)
        return signature_len + 2

    def write_string(self, value: str, _=None) -> int:
        value = value.encode()
        value_len = len(value)
        written = self.align(4) + 4
        self.buffer.extend(PACK_UINT32(value_len))
        self.buffer.extend(value)
        written += value_len
        self.buffer.append(0)
        written += 1
        return written

    def write_variant(self, variant: Variant, _=None) -> int:
        written = self.write_signature(variant.signature)
        written += self.write_single(variant.type, variant.value)
        return written

    def write_array(self, array: Iterable[Any], type_: SignatureType) -> int:
        # TODO max array size is 64MiB (67108864 bytes)
        written = self.align(4)
        # length placeholder
        offset = len(self.buffer)
        written += self.align(4) + 4
        self.buffer.extend(PACK_UINT32(0))
        child_type = type_.children[0]

        if child_type.token in "xtd{(":
            # the first alignment is not included in array size
            written += self.align(8)

        array_len = 0
        if child_type.token == "{":
            for key, value in array.items():
                array_len += self.write_dict_entry([key, value], child_type)
        elif child_type.token == "y":
            array_len = len(array)
            self.buffer.extend(array)
        elif child_type.token in self._writers:
            writer, packer, size = self._writers[child_type.token]
            if not writer:
                for value in array:
                    array_len += self.align(size) + size
                    self.buffer.extend(packer(value))
            else:
                for value in array:
                    array_len += writer(self, value, child_type)
        else:
            raise NotImplementedError(
                f'type is not implemented yet: "{child_type.token}"'
            )

        array_len_packed = PACK_UINT32(array_len)
        for i in range(offset, offset + 4):
            self.buffer[i] = array_len_packed[i - offset]

        return written + array_len

    def write_struct(self, array: List[Any], type_: SignatureType) -> int:
        written = self.align(8)
        for i, value in enumerate(array):
            written += self.write_single(type_.children[i], value)
        return written

    def write_dict_entry(self, dict_entry: List[Any], type_: SignatureType) -> int:
        written = self.align(8)
        written += self.write_single(type_.children[0], dict_entry[0])
        written += self.write_single(type_.children[1], dict_entry[1])
        return written

    def write_single(self, type_: SignatureType, body: Any) -> int:
        t = type_.token

        if t not in self._writers:
            raise NotImplementedError(f'type is not implemented yet: "{t}"')

        writer, packer, size = self._writers[t]
        if not writer:
            written = self.align(size)
            self.buffer.extend(packer(body))
            return written + size
        return writer(self, body, type_)

    def marshall(self):
        """Marshalls the body into a byte array"""
        try:
            self._construct_buffer()
        except error:
            self.signature_tree.verify(self.body)
        return self.buffer

    def _construct_buffer(self):
        self.buffer.clear()
        for i, type_ in enumerate(self.signature_tree.types):
            t = type_.token
            if t not in self._writers:
                raise NotImplementedError(f'type is not implemented yet: "{t}"')

            writer, packer, size = self._writers[t]
            if not writer:

                # In-line align
                offset = size - len(self.buffer) % size
                if offset != 0 and offset != size:
                    self.buffer.extend(bytes(offset))

                self.buffer.extend(packer(self.body[i]))
            else:
                writer(self, self.body[i], type_)

    _writers: Dict[
        str,
        Tuple[
            Optional[Callable[[Any, Any], int]],
            Optional[Callable[[Any], bytes]],
            Optional[int],
        ],
    ] = {
        "y": (None, Struct("<B").pack, 1),
        "b": (write_boolean, None, None),
        "n": (None, Struct("<h").pack, 2),
        "q": (None, Struct("<H").pack, 2),
        "i": (None, Struct("<i").pack, 4),
        "u": (None, PACK_UINT32, 4),
        "x": (None, Struct("<q").pack, 8),
        "t": (None, Struct("<Q").pack, 8),
        "d": (None, Struct("<d").pack, 8),
        "h": (None, Struct("<I").pack, 4),
        "o": (write_string, None, None),
        "s": (write_string, None, None),
        "g": (write_signature, None, None),
        "a": (write_array, None, None),
        "(": (write_struct, None, None),
        "{": (write_dict_entry, None, None),
        "v": (write_variant, None, None),
    }
