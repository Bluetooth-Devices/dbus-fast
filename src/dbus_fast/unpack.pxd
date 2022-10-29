"""cdefs for unpack.py"""

import cython


cdef object Variant

cpdef unpack_variants(object data)

cdef _unpack_variants(object data)
