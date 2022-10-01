"""cdefs for marshaller.py"""

import cython


cdef class Marshaller:

    cdef object signature_tree
    cdef object _buf
    cdef object body
