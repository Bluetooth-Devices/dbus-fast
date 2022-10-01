"""cdefs for unmarshaller.py"""

import cython

from ..signature import SignatureType


cdef unsigned int UINT32_SIZE
#cdef const char* UINT32_CAST

#cpdef cast_parser_factory(int ctype, int size)

cdef class Unmarshaller:

    cdef object unix_fds
    cdef object buf
    cdef object view
    cdef unsigned int pos
    cdef object stream
    cdef object sock
    cdef object message
    cdef object readers
    cdef unsigned int body_len
    cdef unsigned int serial
    cdef unsigned int header_len
    cdef object message_type
    cdef object flag
    cdef unsigned int msg_len
    cdef object _uint32_unpack

    cpdef read_string_cast(self, type_ = *)

    cpdef read_array(self, object type_)
