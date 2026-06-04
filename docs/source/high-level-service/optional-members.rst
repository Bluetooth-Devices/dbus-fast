Optional members
=================

The decorators :func:`@dbus_method() <dbus_fast.service.dbus_method>`,
:func:`@dbus_property() <dbus_fast.service.dbus_property>`, and
:func:`@dbus_signal() <dbus_fast.service.dbus_signal>` are collected from
the class when an interface is constructed, so the set of members is
normally fixed when you write the class. A common need, though, is to
write the interface once with all of its members and then expose only
some of them depending on runtime configuration.

The ``disabled`` argument accepted by each decorator is evaluated when
the class is built, so wrapping the ``class`` body in a factory function
lets you produce variants of an interface with different optional members
enabled. Passing the set of members to enable — rather than to disable —
keeps any members added later opt-in:

.. code-block:: python3

    from dbus_fast.annotations import DBusStr, DBusUInt16
    from dbus_fast.service import ServiceInterface, dbus_property, PropertyAccess


    def make_advertisement(enabled_properties=("Appearance", "LocalName")):
        class Advertisement(ServiceInterface):
            def __init__(self, name="org.example.Advertisement"):
                super().__init__(name)
                self._appearance = 0
                self._local_name = ""

            @dbus_property(
                PropertyAccess.READ,
                disabled="Appearance" not in enabled_properties,
            )
            def Appearance(self) -> DBusUInt16:
                return self._appearance

            @dbus_property(
                PropertyAccess.READ,
                disabled="LocalName" not in enabled_properties,
            )
            def LocalName(self) -> DBusStr:
                return self._local_name

        return Advertisement


    # All properties enabled.
    Advertisement = make_advertisement()
    # A variant that exposes only LocalName.
    MinimalAdvertisement = make_advertisement(enabled_properties=["LocalName"])

Build the class once and reuse it for every instance — there is no need
to rebuild it per object.
