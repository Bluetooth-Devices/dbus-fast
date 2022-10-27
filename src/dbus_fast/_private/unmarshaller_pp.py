from struct import Struct

UNPACK_HEADER_LITTLE_ENDIAN = Struct("<III").unpack_from
UINT32_UNPACK_LITTLE_ENDIAN = Struct("<I").unpack_from
INT16_UNPACK_LITTLE_ENDIAN = Struct("<h").unpack_from

UNPACK_HEADER_BIG_ENDIAN = Struct(">III").unpack_from
UINT32_UNPACK_BIG_ENDIAN = Struct(">I").unpack_from
INT16_UNPACK_BIG_ENDIAN = Struct(">h").unpack_from


def _unpack_uint32_le(payload) -> int:
    return UINT32_UNPACK_LITTLE_ENDIAN(payload)[0]


def _unpack_int16_le(payload) -> int:
    return INT16_UNPACK_LITTLE_ENDIAN(payload)[0]
