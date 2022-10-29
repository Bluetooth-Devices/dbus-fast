"""cdefs for unmarshaller.py"""

import cython

from ..signature import SignatureType


cdef unsigned int UINT32_SIZE
cdef unsigned int INT16_SIZE
cdef unsigned int UINT16_SIZE

cdef unsigned int HEADER_ARRAY_OF_STRUCT_SIGNATURE_POSITION
cdef unsigned int HEADER_SIGNATURE_SIZE
cdef unsigned int LITTLE_ENDIAN
cdef unsigned int BIG_ENDIAN
cdef unsigned int PROTOCOL_VERSION

cdef str UINT32_CAST
cdef str INT16_CAST
cdef str UINT16_CAST

cdef bint SYS_IS_LITTLE_ENDIAN
cdef bint SYS_IS_BIG_ENDIAN

cdef object UNPACK_HEADER_LITTLE_ENDIAN
cdef object UNPACK_HEADER_BIG_ENDIAN

cdef object UINT32_UNPACK_LITTLE_ENDIAN
cdef object UINT32_UNPACK_BIG_ENDIAN

cdef object INT16_UNPACK_LITTLE_ENDIAN
cdef object INT16_UNPACK_BIG_ENDIAN

cdef object UINT16_UNPACK_LITTLE_ENDIAN
cdef object UINT16_UNPACK_BIG_ENDIAN

cdef object Variant
cdef object Message
cdef object MESSAGE_TYPE_MAP
cdef object MESSAGE_FLAG_MAP
cdef object HEADER_MESSAGE_ARG_NAME

cdef object SIGNATURE_TREE_EMPTY
cdef object SIGNATURE_TREE_B
cdef object SIGNATURE_TREE_N
cdef object SIGNATURE_TREE_O
cdef object SIGNATURE_TREE_S
cdef object SIGNATURE_TREE_AS
cdef object SIGNATURE_TREE_AS_TYPES_0
cdef object SIGNATURE_TREE_A_SV
cdef object SIGNATURE_TREE_A_SV_TYPES_0
cdef object SIGNATURE_TREE_SA_SV_AS
cdef object SIGNATURE_TREE_SA_SV_AS_TYPES_1
cdef object SIGNATURE_TREE_SA_SV_AS_TYPES_2
cdef object SIGNATURE_TREE_OAS
cdef object SIGNATURE_TREE_OAS_TYPES_1
cdef object SIGNATURE_TREE_OA_SA_SV
cdef object SIGNATURE_TREE_OA_SA_SV_TYPES_1
cdef object SIGNATURE_TREE_AY
cdef object SIGNATURE_TREE_AY_TYPES_0
cdef object SIGNATURE_TREE_A_QV
cdef object SIGNATURE_TREE_A_QV_TYPES_0

cdef unsigned int TOKEN_O_AS_INT
cdef unsigned int TOKEN_S_AS_INT
cdef unsigned int TOKEN_G_AS_INT


cpdef get_signature_tree

cdef inline unsigned long _cast_uint32_native(const char * payload, unsigned int offset):
    cdef unsigned long *u32p = <unsigned long *> &payload[offset]
    return u32p[0]

cdef inline short _cast_int16_native(const char *  payload, unsigned int offset):
    cdef short *s16p = <short *> &payload[offset]
    return s16p[0]

cdef inline unsigned short _cast_uint16_native(const char *  payload, unsigned int offset):
    cdef unsigned short *u16p = <unsigned short *> &payload[offset]
    return u16p[0]


cdef class MarshallerStreamEndError(Exception):
    pass

cdef class Unmarshaller:

    cdef object _unix_fds
    cdef bytearray _buf
    cdef unsigned int _pos
    cdef object _stream
    cdef object _sock
    cdef object _message
    cdef object _readers
    cdef unsigned int _body_len
    cdef unsigned int _serial
    cdef unsigned int _header_len
    cdef unsigned int _message_type
    cdef unsigned int _flag
    cdef unsigned int _msg_len
    cdef unsigned int _is_native
    cdef object _uint32_unpack
    cdef object _int16_unpack
    cdef object _uint16_unpack

    cpdef reset(self)

    cdef bytes _read_sock(self, unsigned long length)

    @cython.locals(
        start_len=cython.ulong,
        missing_bytes=cython.ulong,
        data=cython.bytes
    )
    cdef _read_to_pos(self, unsigned long pos)

    cpdef read_boolean(self, object type_)

    cdef _read_boolean(self)

    cpdef read_uint32_unpack(self, object type_)

    cdef unsigned int _read_uint32_unpack(self)

    cpdef read_int16_unpack(self, object type_)

    cdef int _read_int16_unpack(self)

    cpdef read_uint16_unpack(self, object type_)

    cdef unsigned int _read_uint16_unpack(self)

    cpdef read_string_unpack(self, object type_)

    @cython.locals(
        str_start=cython.uint,
    )
    cdef _read_string_unpack(self)

    cdef _read_variant(self)

    cpdef read_array(self, object type_)

    @cython.locals(
        beginning_pos=cython.ulong,
        array_length=cython.uint,
    )
    cdef _read_array(self, object type_)

    cpdef read_signature(self, object type_)

    @cython.locals(
        o=cython.ulong,
        signature_len=cython.uint,
    )
    cdef _read_signature(self)

    @cython.locals(
        endian=cython.uint,
        protocol_version=cython.uint,
        key=cython.str
    )
    cdef _read_header(self)

    @cython.locals(
        body=cython.list
    )
    cdef _read_body(self)

    cpdef unmarshall(self)

    @cython.locals(
        beginning_pos=cython.ulong,
        o=cython.ulong,
        field_0=cython.uint,
        token_as_int=cython.uint,
        signature_len=cython.uint,
    )
    cdef header_fields(self, unsigned int header_length)
