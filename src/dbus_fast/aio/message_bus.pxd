"""cdefs for message_bus.py"""

import cython


cdef _future_set_result(object fut, object result)


cdef class _MessageWriter:

    cdef object messages
    cdef bint negotiate_unix_fd
    cdef object bus
    cdef object sock
    cdef object loop
    cdef object buf
    cdef unsigned int fd
    cdef unsigned int offset
    cdef list unix_fds
    cdef object fut
