"""cdefs for message.py"""

import cython

from ._private.marshaller cimport Marshaller
from .signature cimport SignatureTree

cdef object ErrorType
cdef object MessageType

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

cdef Py_ssize_t _MAX_MESSAGE_SIZE
cdef Py_ssize_t _MAX_ARRAY_LENGTH

cdef object MESSAGE_FLAG
cdef object MESSAGE_FLAG_NONE
cdef object MESSAGE_TYPE_METHOD_CALL

cdef bytes HEADER_FIELD_PATH
cdef bytes HEADER_FIELD_INTERFACE
cdef bytes HEADER_FIELD_MEMBER
cdef bytes HEADER_FIELD_ERROR_NAME
cdef bytes HEADER_FIELD_REPLY_SERIAL
cdef bytes HEADER_FIELD_DESTINATION
cdef bytes HEADER_FIELD_SIGNATURE
cdef bytes HEADER_FIELD_UNIX_FDS

cdef Py_ssize_t HEADER_FIELDS_OFFSET
cdef object PACK_HEADER_START
cdef object PACK_UINT32
cdef object PACK_UINT32_INTO
cdef tuple ZERO_PADDING

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
    cdef public list unix_fds
    cdef public str signature
    cdef public SignatureTree signature_tree
    cdef public object body
    cdef public unsigned int serial

    @cython.locals(
        body_buffer=bytearray,
        header_buffer=bytearray,
        signature_bytes=bytes,
        fields_len=Py_ssize_t,
    )
    cpdef _marshall(self, bint negotiate_unix_fd)

    cdef _fast_init(
        self,
        object destination,
        object path,
        object interface,
        object member,
        object message_type,
        object flags,
        object error_name,
        unsigned int reply_serial,
        object sender,
        list unix_fds,
        SignatureTree signature_tree,
        object body,
        unsigned int serial,
        bint validate
    )


cdef _align8(bytearray buf)

cdef _write_header_uint32(bytearray buf, bytes field, unsigned int value)

@cython.locals(value_bytes=bytes)
cdef _write_header_string(bytearray buf, bytes field, object value)
