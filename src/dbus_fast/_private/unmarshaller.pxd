"""cdefs for unmarshaller.py"""

import cython

from ..signature import SignatureType


cdef unsigned int UINT32_SIZE
cdef unsigned int HEADER_ARRAY_OF_STRUCT_SIGNATURE_POSITION
cdef unsigned int HEADER_SIGNATURE_SIZE

cdef class Unmarshaller:

    cdef object unix_fds
    cdef object buf
    cdef object view
    cdef unsigned int pos
    cdef object stream
    cdef object sock
    cdef object _message
    cdef object readers
    cdef unsigned int body_len
    cdef unsigned int serial
    cdef unsigned int header_len
    cdef object message_type
    cdef object flag
    cdef unsigned int msg_len
    cdef object _uint32_unpack


    @cython.locals(
        start_len=cython.ulong,
        missing_bytes=cython.ulong,
    )
    cpdef read_to_pos(self, unsigned long pos)

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
    )
    cpdef _read_header(self)

    @cython.locals(
        beginning_pos=cython.ulong,
        o=cython.ulong,
        signature_len=cython.uint,
    )
    cpdef header_fields(self, unsigned int header_length)
