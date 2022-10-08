"""cdefs for marshaller.py"""

import cython


cdef class Marshaller:

    cdef object signature_tree
    cdef bytearray _buf
    cdef object body

    cpdef int align(self, unsigned int n)

    @cython.locals(
        offset=cython.ulong,
    )
    cdef int _align(self, unsigned int n)

    @cython.locals(
        value_len=cython.uint,
        signature_len=cython.uint,
        written=cython.uint,
    )
    cpdef write_string(self, object value, _ = *)

    @cython.locals(
        signature_bytes=cython.bytes,
        signature_len=cython.uint,
    )
    cdef _write_signature(self, str signature)

    @cython.locals(
        array_len=cython.uint,
        written=cython.uint,
        array_len_packed=cython.bytes,
        i=cython.uint,
    )
    cpdef write_array(self, object array, object type)

    @cython.locals(
        written=cython.uint,
        i=cython.uint,
    )
    cpdef write_struct(self, object array, object type)

    @cython.locals(
        written=cython.uint,
    )
    cdef _write_single(self, object type_, object body)

    @cython.locals(
        written=cython.uint,
    )
    cpdef write_dict_entry(self, object type_, object body)

    cpdef marshall(self)

    @cython.locals(
        offset=cython.ulong,
        size=cython.int
    )
    cdef _construct_buffer(self)
