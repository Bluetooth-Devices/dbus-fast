import sys

import pytest

from dbus_fast import DBusError, Message, aio, glib
from dbus_fast.service import PropertyAccess, ServiceInterface, dbus_property
from dbus_fast.signature import Variant
from tests.util import check_gi_repository, skip_reason_no_gi

has_gi = check_gi_repository()


class ExampleInterface(ServiceInterface):
    def __init__(self):
        super().__init__("test.interface")
        self._some_property = "foo"
        self.error_name = "test.error"
        self.error_text = "i am bad"
        self._int64_property = -10000

    @dbus_property()
    def SomeProperty(self) -> "s":
        return self._some_property

    @SomeProperty.setter
    def SomeProperty(self, val: "s"):
        self._some_property = val

    @dbus_property(access=PropertyAccess.READ)
    def Int64Property(self) -> "x":
        return self._int64_property

    @dbus_property(access=PropertyAccess.READ)
    def ComplexProperty(self) -> "a{sv}":
        """Return complex output."""
        return {"hello": Variant("s", "world")}

    @dbus_property()
    def ErrorThrowingProperty(self) -> "s":
        raise DBusError(self.error_name, self.error_text)

    @ErrorThrowingProperty.setter
    def ErrorThrowingProperty(self, val: "s"):
        raise DBusError(self.error_name, self.error_text)


@pytest.mark.asyncio
async def test_aio_properties():
    service_bus = await aio.MessageBus().connect()
    service_interface = ExampleInterface()
    service_bus.export("/test/path", service_interface)

    bus = await aio.MessageBus().connect()
    obj = bus.get_proxy_object(
        service_bus.unique_name,
        "/test/path",
        service_bus._introspect_export_path("/test/path"),
    )
    interface = obj.get_interface(service_interface.name)

    prop = await interface.get_some_property()
    assert prop == service_interface._some_property

    prop = await interface.get_int64_property()
    assert prop == service_interface._int64_property

    await interface.set_some_property("different")
    assert service_interface._some_property == "different"

    prop = await interface.get_complex_property()
    assert prop == {"hello": Variant("s", "world")}

    prop = await interface.get_complex_property(unpack_variants=True)
    assert prop == {"hello": "world"}

    with pytest.raises(DBusError):
        try:
            prop = await interface.get_error_throwing_property()
            assert False, prop
        except DBusError as e:
            assert e.type == service_interface.error_name
            assert e.text == service_interface.error_text
            assert type(e.reply) is Message
            raise e

    with pytest.raises(DBusError):
        try:
            await interface.set_error_throwing_property("different")
        except DBusError as e:
            assert e.type == service_interface.error_name
            assert e.text == service_interface.error_text
            assert type(e.reply) is Message
            raise e

    service_bus.disconnect()
    bus.disconnect()


@pytest.mark.skipif(
    sys.version_info[:3][1] in (10, 11, 12), reason="segfaults on py3.10,py3.11,py3.12"
)
@pytest.mark.skipif(not has_gi, reason=skip_reason_no_gi)
def test_glib_properties():
    service_bus = glib.MessageBus().connect_sync()
    service_interface = ExampleInterface()
    service_bus.export("/test/path", service_interface)

    bus = glib.MessageBus().connect_sync()
    obj = bus.get_proxy_object(
        service_bus.unique_name,
        "/test/path",
        service_bus._introspect_export_path("/test/path"),
    )
    interface = obj.get_interface(service_interface.name)

    prop = interface.get_some_property_sync()
    assert prop == service_interface._some_property

    interface.set_some_property_sync("different")
    assert service_interface._some_property == "different"

    prop = interface.get_complex_property_sync()
    assert prop == {"hello": Variant("s", "world")}

    prop = interface.get_complex_property_sync(unpack_variants=True)
    assert prop == {"hello": "world"}

    with pytest.raises(DBusError):
        try:
            prop = interface.get_error_throwing_property_sync()
            assert False, prop
        except DBusError as e:
            assert e.type == service_interface.error_name
            assert e.text == service_interface.error_text
            assert type(e.reply) is Message
            raise e

    with pytest.raises(DBusError):
        try:
            interface.set_error_throwing_property_sync("different2")
        except DBusError as e:
            assert e.type == service_interface.error_name
            assert e.text == service_interface.error_text
            assert type(e.reply) is Message
            raise e

    service_bus.disconnect()
    bus.disconnect()
