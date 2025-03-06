"""cdefs for signature.py"""

import cython


cdef class SignatureType:

    cdef public str token
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

    cdef _init(self, SignatureTree signature_Tree, object value)


cdef SignatureTree _SIGNATURE_TREE_EMPTY
cdef SignatureTree _SIGNATURE_TREE_B
cdef SignatureTree _SIGNATURE_TREE_N
cdef SignatureTree _SIGNATURE_TREE_O
cdef SignatureTree _SIGNATURE_TREE_S
cdef SignatureTree _SIGNATURE_TREE_U
cdef SignatureTree _SIGNATURE_TREE_Y
cdef SignatureTree _SIGNATURE_TREE_G

cdef SignatureTree _SIGNATURE_TREE_AS
cdef SignatureType _SIGNATURE_TREE_AS_TYPES_0
cdef SignatureTree _SIGNATURE_TREE_AO
cdef SignatureType _SIGNATURE_TREE_AO_TYPES_0
cdef SignatureTree _SIGNATURE_TREE_A_SV
cdef SignatureType _SIGNATURE_TREE_A_SV_TYPES_0
cdef SignatureTree _SIGNATURE_TREE_SA_SV_AS
cdef SignatureType _SIGNATURE_TREE_SA_SV_AS_TYPES_1
cdef SignatureType _SIGNATURE_TREE_SA_SV_AS_TYPES_2
cdef SignatureTree _SIGNATURE_TREE_OAS
cdef SignatureType _SIGNATURE_TREE_OAS_TYPES_1
cdef SignatureTree _SIGNATURE_TREE_OA_SA_SV
cdef SignatureType _SIGNATURE_TREE_OA_SA_SV_TYPES_1
cdef SignatureTree _SIGNATURE_TREE_AY
cdef SignatureType _SIGNATURE_TREE_AY_TYPES_0
cdef SignatureTree _SIGNATURE_TREE_A_QV
cdef SignatureType _SIGNATURE_TREE_A_QV_TYPES_0
cdef SignatureTree _SIGNATURE_TREE_A_OA_SA_SV
cdef SignatureType _SIGNATURE_TREE_A_OA_SA_SV_TYPES_0
