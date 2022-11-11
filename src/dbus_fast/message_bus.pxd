import cython

from .message cimport Message


cdef object MessageType
cdef object DBusError
cdef object MessageFlag

cdef object MESSAGE_TYPE_CALL
cdef object MESSAGE_TYPE_SIGNAL

cdef class BaseMessageBus:

    cdef public object unique_name
    cdef public object _disconnected
    cdef public object _user_disconnect
    cdef public object _method_return_handlers
    cdef public object _serial
    cdef public cython.list _user_message_handlers
    cdef public object _name_owners
    cdef public object _bus_address
    cdef public object _name_owner_match_rule
    cdef public object _match_rules
    cdef public object _high_level_client_initialized
    cdef public object _ProxyObject
    cdef public object _machine_id

    cpdef _process_message(self, Message msg)
