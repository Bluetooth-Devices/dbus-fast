"""cdefs for signature.py"""

import cython


cdef class SignatureType:

    cdef public str token
    cdef public unsigned int token_as_int
    cdef public list children
    cdef str _signature


cdef class SignatureTree:

    cdef public str signature
    cdef public list types
    cdef public SignatureType root_type


cdef class Variant:

    cdef public SignatureType type
    cdef public str signature
    cdef public object value

    @cython.locals(self=Variant)
    @staticmethod
    cdef Variant _factory(SignatureTree signature_tree, object value)
