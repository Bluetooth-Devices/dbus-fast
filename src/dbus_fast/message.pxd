"""cdefs for message.py"""

import cython


cdef unsigned int LITTLE_ENDIAN
cdef unsigned int BIG_ENDIAN
cdef unsigned int PROTOCOL_VERSION

cdef class Message:

    cdef str destination
    cdef str path
    cdef str interface
    cdef str member
    cdef object message_type
    cdef object flags
    cdef str error_name
    cdef object reply_serial
    cdef str sender
    cdef list unix_fds
    cdef str signature
    cdef object signature_tree
    cdef list body
    cdef unsigned int _serial

    @cython.locals(
        fields=cython.list,
        header_body=cython.list,
    )
    cpdef _marshall(self, negotiate_unix_fd = *)

    cpdef _matches(self, dict matcher)
