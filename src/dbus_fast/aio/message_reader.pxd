"""cdefs for message_reader.py"""

import cython


@cython.locals(
    message=cython.object,
)
cpdef message_reader(object unmarshaller, object process, object finalize)
