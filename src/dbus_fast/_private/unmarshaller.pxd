"""cdefs for unmarshaller.py"""

import cython

from ..signature import SignatureType


cdef unsigned int UINT32_SIZE
cdef unsigned int INT16_SIZE
cdef unsigned int HEADER_ARRAY_OF_STRUCT_SIGNATURE_POSITION
cdef unsigned int HEADER_SIGNATURE_SIZE
cdef unsigned int LITTLE_ENDIAN
cdef unsigned int BIG_ENDIAN
cdef unsigned int PROTOCOL_VERSION
cdef str UINT32_CAST
cdef str INT16_CAST

cdef object UNPACK_LENGTHS_LITTLE_ENDIAN
cdef object UNPACK_LENGTHS_BIG_ENDIAN
cdef object UINT32_UNPACK_LITTLE_ENDIAN
cdef object UINT32_UNPACK_BIG_ENDIAN
cdef object INT16_UNPACK_LITTLE_ENDIAN
cdef object INT16_UNPACK_BIG_ENDIAN

cdef object UINT32_SIGNATURE


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
    cdef object _uint32_unpack
    cdef object _int16_unpack

    cpdef reset(self)

    cdef read_sock(self, unsigned long length)

    @cython.locals(
        start_len=cython.ulong,
        missing_bytes=cython.ulong
    )
    cdef void read_to_pos(self, unsigned long pos)

    cpdef read_uint32_unpack(self, object type_)

    cdef unsigned int _read_uint32_unpack(self)

    cpdef read_int16_unpack(self, object type_)

    cdef int _read_int16_unpack(self)

    cpdef read_string_unpack(self, object type_)

    cdef _read_string_unpack(self)

    @cython.locals(
        buf_bytes=cython.bytearray,
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
    cdef void _read_header(self)

    @cython.locals(
        body=cython.list,
    )
    cdef void _read_body(self)

    cpdef unmarshall(self)

    @cython.locals(
        beginning_pos=cython.ulong,
        o=cython.ulong,
        field_0=cython.uint,
        signature_len=cython.uint,
    )
    cdef header_fields(self, unsigned int header_length)
