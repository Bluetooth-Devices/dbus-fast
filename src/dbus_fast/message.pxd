"""cdefs for message.py"""

import cython


cdef class Message:

    cdef public str destination
    cdef public str path
    cdef public str interface
    cdef public str member
    cdef public object message_type
    cdef public object flags
    cdef public str error_name
    cdef public unsigned int reply_serial
    cdef public str sender
    cdef public list unix_fds
    cdef public str signature
    cdef public object signature_tree
    cdef public list body
    cdef public unsigned int serial

    cpdef _marshall(self, bint negotiate_unix_fd)
