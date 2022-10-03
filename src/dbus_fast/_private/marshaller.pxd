"""cdefs for marshaller.py"""

import cython


cdef class Marshaller:

    cdef object signature_tree
    cdef bytearray _buf
    cdef object body

    @cython.locals(
        offset=cython.ulong,
    )
    cpdef int align(self, unsigned long n)

    @cython.locals(
        signature_len=cython.uint,
        written=cython.uint,
    )
    cpdef write_string(self, object value, _ = *)

    @cython.locals(
        array_len=cython.uint,
        written=cython.uint,
        array_len_packed=cython.bytes,
    )
    cpdef write_array(self, object array, object type)

    @cython.locals(
        written=cython.uint,
    )
    cpdef write_struct(self, object array, object type)

    @cython.locals(
        written=cython.uint,
    )
    cpdef write_single(self, object type_, object body)

    cpdef marshall(self)

    @cython.locals(
        offset=cython.ulong,
    )
    cpdef _construct_buffer(self)
