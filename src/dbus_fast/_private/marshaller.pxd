"""cdefs for marshaller.py"""

import cython


cdef bytes PACKED_UINT32_ZERO
cdef object PACK_UINT32

cdef class Marshaller:

    cdef object signature_tree
    cdef bytearray _buf
    cdef object body

    cpdef unsigned int align(self, unsigned int n)

    @cython.locals(
        offset=cython.ulong,
    )
    cdef unsigned int _align(self, unsigned int n)

    @cython.locals(
        value_len=cython.uint,
        signature_len=cython.uint,
        written=cython.uint,
    )
    cpdef write_string(self, object value, object _type)

    @cython.locals(
        signature_len=cython.uint,
    )
    cdef unsigned int _write_signature(self, bytes signature_bytes)

    cpdef write_array(self, object array, object type)

    @cython.locals(
        array_len=cython.uint,
        buf=cython.bytearray,
        written=cython.uint,
        token=cython.str,
        array_len_packed=cython.bytes,
        size=cython.uint,
        writer=cython.object,
        packer=cython.object,
        i=cython.uint,
    )
    cdef unsigned int _write_array(self, object array, object type)

    cpdef write_struct(self, object array, object type)

    @cython.locals(
        written=cython.uint,
        i=cython.uint,
    )
    cdef unsigned int _write_struct(self, object array, object type)

    @cython.locals(
        written=cython.uint,
    )
    cpdef write_variant(self, object variant, object type)

    @cython.locals(
        written=cython.uint,
        size=cython.uint,
    )
    cdef unsigned int _write_single(self, object type_, object body)

    @cython.locals(
        written=cython.uint,
        t=cython.str,
    )
    cpdef write_dict_entry(self, object type_, object body)

    cpdef marshall(self)

    @cython.locals(
        offset=cython.ulong,
        t=cython.str,
        size=cython.uint,
        writer=cython.object,
        packer=cython.object,
    )
    cdef _construct_buffer(self)
