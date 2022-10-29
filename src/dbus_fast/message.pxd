"""cdefs for message.py"""

import cython


cdef object ErrorType
cdef object SignatureTree
cdef object SignatureType
cdef object MessageType
cdef object Variant
cdef object Marshaller


cdef object HEADER_PATH
cdef object HEADER_INTERFACE
cdef object HEADER_MEMBER
cdef object HEADER_ERROR_NAME
cdef object HEADER_REPLY_SERIAL
cdef object HEADER_DESTINATION
cdef object HEADER_SENDER
cdef object HEADER_SIGNATURE
cdef object HEADER_UNIX_FDS


cdef object LITTLE_ENDIAN
cdef object PROTOCOL_VERSION

cdef get_signature_tree

cdef class Message:

    cdef public object destination
    cdef public object path
    cdef public object interface
    cdef public object member
    cdef public object message_type
    cdef public object flags
    cdef public object error_name
    cdef public unsigned int reply_serial
    cdef public object sender
    cdef public object unix_fds
    cdef public object signature
    cdef public object signature_tree
    cdef public object body
    cdef public unsigned int serial

    cpdef _marshall(self, bint negotiate_unix_fd)
