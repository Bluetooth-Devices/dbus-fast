The High Level Service
======================

.. toctree::
   :maxdepth: 2

   service-interface

The high level service interface provides everything you need to export interfaces on the bus. When you export an interface on your :class:`MessageBus <dbus_fast.message_bus.BaseMessageBus>`, clients can send you messages to call methods, get and set properties, and listen to your signals.

If you're exposing a service for general use, you can request a well-known name for your connection with :func:`MessageBus.request_name() <dbus_fast.message_bus.BaseMessageBus.request_name>` so users have a predictable name to use to send messages your client.

Services are defined by subclassing :class:`ServiceInterface <dbus_fast.service.ServiceInterface>` and definining members as methods on the class with the decorator methods :func:`@dbus_method() <dbus_fast.service.dbus_method>`, :func:`@dbus_property() <dbus_fast.service.dbus_property>`, and :func:`@dbus_signal() <dbus_fast.service.dbus_signal>`. The parameters of the decorated class methods must be annotated with DBus type strings to indicate the types of values they expect. See the documentation on `the type system </type-system/index.html>`_ for more information on how DBus types are mapped to Python values with signature strings. The decorator methods themselves take arguments that affect how the member is exported on the bus, such as the name of the member or the access permissions of a property.

A class method decorated with ``@dbus_method()`` will be called when a client calls the method over DBus. The parameters given to the class method will be provided by the calling client and will conform to the parameter type annotations. The value returned by the class method will be returned to the client and must conform to the return type annotation specified by the user. If the return annotation specifies more than one type, the values must be returned in a ``tuple``. When :class:`aio.MessageBus` is used, methods can be coroutines.

A class method decorated with ``@dbus_property()`` will be exposed as a DBus property getter. This decoration works the same as a standard Python ``@property``. The getter will be called when a client gets the property through the standard properties interface with ``org.freedesktop.DBus.Properties.Get``. Define a property setter with ``@<method_name>.setter`` taking the new value as a parameter. The setter will be called when the client sets the property through ``org.freedesktop.DBus.Properties.Set``. When :class:`aio.MessageBus` is used, property getters and setters can be coroutines, although this will cause some functionality of the Python ``@property`` annotation to be lost.

A class method decorated with ``@dbus_signal()`` will be exposed as a DBus signal. The value returned by the class method will be emitted as a signal and broadcast to clients who are listening to the signal. The returned value must conform to the return annotation of the class method as a DBus signature string. If the signal has more than one argument, they must be returned within a ``tuple``.

A class method decorated with ``@dbus_method()`` or ``@dbus_property()`` may throw a :class:`DBusError <dbus_fast.DBusError>` to return a detailed error to the client if something goes wrong.

After the service interface is defined, call :func:`MessageBus.export() <dbus_fast.message_bus.BaseMessageBus.export>` on a connected message bus and the service will be made available on the given object path.

If any file descriptors are sent or received (DBus type ``h``), the variable refers to the file descriptor itself. You are responsible for closing any file descriptors sent or received by the bus. You must set the ``negotiate_unix_fd`` flag to ``True`` in the ``MessageBus`` constructor to use unix file descriptors.

:example:

.. code-block:: python3

    from dbus_fast.aio import MessageBus
    from dbus_fast.service import (ServiceInterface,
                                   dbus_method, dbus_property, dbus_signal)
    from dbus_fast import Variant, DBusError

    import asyncio

    class ExampleInterface(ServiceInterface):
        def __init__(self):
            super().__init__('com.example.SampleInterface0')
            self._bar = 105

        @dbus_method()
        def Frobate(self, foo: 'i', bar: 's') -> 'a{us}':
            print(f'called Frobate with foo={foo} and bar={bar}')

            return {
                1: 'one',
                2: 'two'
            }

        @dbus_method()
        async def Bazify(self, bar: '(iiu)') -> 'vv':
            print(f'called Bazify with bar={bar}')

            return Variant('s', 'example'), Variant('s', 'bazify')

        @dbus_method()
        def Mogrify(self, bar: '(iiav)'):
            raise DBusError('com.example.error.CannotMogrify',
                            'it is not possible to mogrify')

        @dbus_signal()
        def Changed(self) -> 'b':
            return True

        @dbus_property()
        def Bar(self) -> 'y':
            return self._bar

        @Bar.setter
        def Bar(self, val: 'y'):
            if self._bar == val:
                return

            self._bar = val

            self.emit_properties_changed({'Bar': self._bar})

    async def main():
        bus = await MessageBus().connect()
        interface = ExampleInterface()
        bus.export('/com/example/sample0', interface)
        await bus.request_name('com.example.name')

        # emit the changed signal after two seconds.
        await asyncio.sleep(2)

        interface.changed()

        await bus.wait_for_disconnect()

    asyncio.run(main())
