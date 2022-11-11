import cython

from .message cimport Message


cdef object MessageType
cdef object DBusError
cdef object MessageFlag


cdef class BaseMessageBus:

    cdef public object unique_name
    cdef object _disconnected
    cdef object _user_disconnect
    cdef object _method_return_handlers
    cdef object _serial
    cdef object _user_message_handlers
    cdef object _name_owners
    cdef object _bus_address
    cdef object _name_owner_match_rule
    cdef object _match_rules
    cdef object _high_level_client_initialized
    cdef object _ProxyObject
    cdef object _machine_id

    cpdef _process_message(self, msg: Message)
