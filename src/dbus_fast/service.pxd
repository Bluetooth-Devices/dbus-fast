"""cdefs for service.py"""

import cython

from .signature cimport SignatureTree


cdef class _Method:

    cdef public str name
    cdef public object fn
    cdef public object disabled
    cdef public object introspection
    cdef public str in_signature
    cdef public str out_signature
    cdef public SignatureTree in_signature_tree
    cdef public SignatureTree out_signature_tree

cdef class ServiceInterface:

    cdef public str name
    cdef list __methods
    cdef list __properties
    cdef list __signals
    cdef set __buses
    cdef dict __handlers
