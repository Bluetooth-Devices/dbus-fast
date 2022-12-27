from ..message cimport Message
from ..message_bus cimport BaseMessageBus
from ..service cimport ServiceInterface, _Method

import cython


cdef object deque
cdef object memoryview
cdef object copy
cdef object NO_REPLY_EXPECTED_VALUE
cdef object MESSAGE_TYPE_CALL

cdef _future_set_exception(object fut, object exc)

cdef _future_set_result(object fut, object result)





cdef class MessageBus(BaseMessageBus):

    cdef object _loop
    cdef object _auth
    cdef _MessageWriter _writer
    cdef object _disconnect_future

    cpdef send(self, Message msg)


cdef class _MessageWriter:

    cdef object messages
    cdef object negotiate_unix_fd
    cdef MessageBus bus
    cdef object sock
    cdef object loop
    cdef object buf
    cdef object fd
    cdef object offset
    cdef object unix_fds
    cdef object fut

    cdef _buffer_message(self, Message msg, object future)
