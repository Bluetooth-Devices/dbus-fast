"""cdefs for unmarshaller.py"""

import cython

from ..signature import SignatureType


cdef unsigned int UINT32_SIZE
cdef unsigned int HEADER_ARRAY_OF_STRUCT_SIGNATURE_POSITION
cdef unsigned int HEADER_SIGNATURE_SIZE
cdef unsigned int LITTLE_ENDIAN
cdef unsigned int BIG_ENDIAN
cdef str UINT32_CAST
cdef object UINT32_SIGNATURE

cdef class Unmarshaller:

    cdef object _unix_fds
    cdef bytearray _buf
    cdef object _view
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

    cpdef reset(self)

    @cython.locals(
        start_len=cython.ulong,
        missing_bytes=cython.ulong
    )
    cpdef read_to_pos(self, unsigned long pos)

    cpdef read_uint32_cast(self, object type_)

    @cython.locals(
        buf_bytes=cython.bytearray,
    )
    cpdef read_string_cast(self, type_ = *)

    @cython.locals(
        beginning_pos=cython.ulong,
        array_length=cython.uint,
    )
    cpdef read_array(self, object type_)

    @cython.locals(
        o=cython.ulong,
        signature_len=cython.uint,
    )
    cpdef read_signature(self, type_ = *)

    @cython.locals(
        endian=cython.uint,
        protocol_version=cython.uint,
        can_cast=cython.bint
    )
    cpdef _read_header(self)

    cpdef _read_body(self)

    cpdef unmarshall(self)

    @cython.locals(
        beginning_pos=cython.ulong,
        o=cython.ulong,
        signature_len=cython.uint,
    )
    cpdef header_fields(self, unsigned int header_length)
