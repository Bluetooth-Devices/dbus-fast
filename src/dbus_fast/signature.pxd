"""cdefs for signature.py"""

import cython


cdef class SignatureType:

    cdef public str token
    cdef public list children
    cdef str _signature

    @cython.locals(
        child=SignatureType,
        signature=cython.list
    )
    cdef _collapse(self)


cdef class SignatureTree:

    cdef public str signature
    cdef public list types


cdef class Variant:

    cdef public SignatureType type
    cdef public object signature
    cdef public object value

    @cython.locals(
        signature_tree=SignatureTree
    )
    cdef void _init_signature(self, object signature, object value, bint verify)
