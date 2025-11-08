import asyncio

import pytest

from dbus_fast import Message
from dbus_fast.aio import MessageBus
from dbus_fast.constants import RequestNameReply
from dbus_fast.introspection import Node
from dbus_fast.service import ServiceInterface, dbus_signal
from dbus_fast.signature import Variant


class ExampleInterface(ServiceInterface):
    def __init__(self):
        super().__init__("test.interface")

    @dbus_signal()
    def SomeSignal(self) -> "s":
        return "hello"

    @dbus_signal()
    def SignalMultiple(self) -> "ss":
        return ["hello", "world"]

    @dbus_signal()
    def SignalComplex(self) -> "a{sv}":  # noqa: F722
        """Broadcast a complex signal."""
        return {"hello": Variant("s", "world")}


@pytest.mark.asyncio
async def test_signals():
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    bus_intr = await bus1.introspect("org.freedesktop.DBus", "/org/freedesktop/DBus")
    bus_obj = bus1.get_proxy_object(
        "org.freedesktop.DBus", "/org/freedesktop/DBus", bus_intr
    )
    stats = bus_obj.get_interface("org.freedesktop.DBus.Debug.Stats")

    await bus1.request_name("test.signals.name")
    service_interface = ExampleInterface()
    bus1.export("/test/path", service_interface)

    obj = bus2.get_proxy_object(
        "test.signals.name", "/test/path", bus1._introspect_export_path("/test/path")
    )
    interface = obj.get_interface(service_interface.name)

    async def ping():
        await bus2.call(
            Message(
                destination=bus1.unique_name,
                interface="org.freedesktop.DBus.Peer",
                path="/test/path",
                member="Ping",
            )
        )

    err = None

    single_counter = 0

    def single_handler(value):
        try:
            nonlocal single_counter
            nonlocal err
            assert value == "hello"
            single_counter += 1
        except Exception as e:
            err = e

    multiple_counter = 0

    def multiple_handler(value1, value2):
        nonlocal multiple_counter
        nonlocal err
        try:
            assert value1 == "hello"
            assert value2 == "world"
            multiple_counter += 1
        except Exception as e:
            err = e

    await ping()
    match_rules = await stats.call_get_all_match_rules()
    assert bus2.unique_name in match_rules
    bus_match_rules = match_rules[bus2.unique_name]
    # the bus connection itself takes a rule on NameOwnerChange after the high
    # level client is initialized
    assert len(bus_match_rules) == 1
    assert len(bus2._user_message_handlers) == 0

    interface.on_some_signal(single_handler)
    interface.on_signal_multiple(multiple_handler)

    # Interlude: adding a signal handler with `on_[signal]` should add a match rule and
    # message handler. Removing a signal handler with `off_[signal]` should
    # remove the match rule and message handler to avoid memory leaks.
    await ping()
    match_rules = await stats.call_get_all_match_rules()
    assert bus2.unique_name in match_rules
    bus_match_rules = match_rules[bus2.unique_name]
    # test the match rule and user handler has been added
    assert len(bus_match_rules) == 2
    assert (
        "type='signal',interface='test.interface',path='/test/path',sender='test.signals.name'"
        in bus_match_rules
    )
    assert len(bus2._user_message_handlers) == 1

    service_interface.SomeSignal()
    await ping()
    assert err is None
    assert single_counter == 1

    service_interface.SignalMultiple()
    await ping()
    assert err is None
    assert multiple_counter == 1

    # special case: another bus with the same path and interface but on a
    # different name and connection will trigger the match rule of the first
    # (happens with mpris)
    bus3 = await MessageBus().connect()
    await bus3.request_name("test.signals.name2")
    service_interface2 = ExampleInterface()
    bus3.export("/test/path", service_interface2)

    obj = bus2.get_proxy_object(
        "test.signals.name2", "/test/path", bus3._introspect_export_path("/test/path")
    )
    # we have to add a dummy handler to add the match rule
    iface2 = obj.get_interface(service_interface2.name)

    def dummy_signal_handler(what):
        pass

    iface2.on_some_signal(dummy_signal_handler)
    await ping()

    service_interface2.SomeSignal()
    await ping()
    # single_counter is not incremented for signals of the second interface
    assert single_counter == 1

    interface.off_some_signal(single_handler)
    interface.off_signal_multiple(multiple_handler)
    iface2.off_some_signal(dummy_signal_handler)

    # After `off_[signal]`, the match rule and user handler should be removed
    await ping()
    match_rules = await stats.call_get_all_match_rules()
    assert bus2.unique_name in match_rules
    bus_match_rules = match_rules[bus2.unique_name]
    assert len(bus_match_rules) == 1
    assert (
        "type='signal',interface='test.interface',path='/test/path',sender='test.signals.name'"
        not in bus_match_rules
    )
    assert len(bus2._user_message_handlers) == 0

    bus1.disconnect()
    bus2.disconnect()
    bus3.disconnect()


@pytest.mark.asyncio
async def test_complex_signals():
    """Test complex signals with and without signature removal."""
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    await bus1.request_name("test.signals.name")
    service_interface = ExampleInterface()
    bus1.export("/test/path", service_interface)

    obj = bus2.get_proxy_object(
        "test.signals.name", "/test/path", bus1._introspect_export_path("/test/path")
    )
    interface = obj.get_interface(service_interface.name)

    async def ping():
        await bus2.call(
            Message(
                destination=bus1.unique_name,
                interface="org.freedesktop.DBus.Peer",
                path="/test/path",
                member="Ping",
            )
        )

    sig_handler_counter = 0
    sig_handler_err = None
    no_sig_handler_counter = 0
    no_sig_handler_err = None

    def complex_handler_with_sig(value):
        nonlocal sig_handler_counter
        nonlocal sig_handler_err
        try:
            assert value == {"hello": Variant("s", "world")}
            sig_handler_counter += 1
        except AssertionError as ex:
            sig_handler_err = ex

    def complex_handler_no_sig(value):
        nonlocal no_sig_handler_counter
        nonlocal no_sig_handler_err
        try:
            assert value == {"hello": "world"}
            no_sig_handler_counter += 1
        except AssertionError as ex:
            no_sig_handler_err = ex

    interface.on_signal_complex(complex_handler_with_sig)
    interface.on_signal_complex(complex_handler_no_sig, unpack_variants=True)
    await ping()

    service_interface.SignalComplex()
    await ping()
    assert sig_handler_err is None
    assert sig_handler_counter == 1
    assert no_sig_handler_err is None
    assert no_sig_handler_counter == 1

    bus1.disconnect()
    bus2.disconnect()


@pytest.mark.asyncio
async def test_varargs_callback():
    """Test varargs callback for signal."""
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    await bus1.request_name("test.signals.name")
    service_interface = ExampleInterface()
    bus1.export("/test/path", service_interface)

    obj = bus2.get_proxy_object(
        "test.signals.name", "/test/path", bus1._introspect_export_path("/test/path")
    )
    interface = obj.get_interface(service_interface.name)

    async def ping():
        await bus2.call(
            Message(
                destination=bus1.unique_name,
                interface="org.freedesktop.DBus.Peer",
                path="/test/path",
                member="Ping",
            )
        )

    varargs_handler_counter = 0
    varargs_handler_err = None
    varargs_plus_handler_counter = 0
    varargs_plus_handler_err = None

    def varargs_handler(*args):
        nonlocal varargs_handler_counter
        nonlocal varargs_handler_err
        try:
            assert args[0] == "hello"
            varargs_handler_counter += 1
        except AssertionError as ex:
            varargs_handler_err = ex

    def varargs_plus_handler(value, *_):
        nonlocal varargs_plus_handler_counter
        nonlocal varargs_plus_handler_err
        try:
            assert value == "hello"
            varargs_plus_handler_counter += 1
        except AssertionError as ex:
            varargs_plus_handler_err = ex

    interface.on_some_signal(varargs_handler)
    interface.on_some_signal(varargs_plus_handler)
    await ping()

    service_interface.SomeSignal()
    await ping()
    assert varargs_handler_err is None
    assert varargs_handler_counter == 1
    assert varargs_plus_handler_err is None
    assert varargs_plus_handler_counter == 1

    bus1.disconnect()
    bus2.disconnect()


@pytest.mark.asyncio
async def test_kwargs_callback():
    """Test callback for signal with kwargs."""
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    await bus1.request_name("test.signals.name")
    service_interface = ExampleInterface()
    bus1.export("/test/path", service_interface)

    obj = bus2.get_proxy_object(
        "test.signals.name", "/test/path", bus1._introspect_export_path("/test/path")
    )
    interface = obj.get_interface(service_interface.name)

    async def ping():
        await bus2.call(
            Message(
                destination=bus1.unique_name,
                interface="org.freedesktop.DBus.Peer",
                path="/test/path",
                member="Ping",
            )
        )

    kwargs_handler_counter = 0
    kwargs_handler_err = None
    kwarg_default_handler_counter = 0
    kwarg_default_handler_err = None

    def kwargs_handler(value, **_):
        nonlocal kwargs_handler_counter
        nonlocal kwargs_handler_err
        try:
            assert value == "hello"
            kwargs_handler_counter += 1
        except AssertionError as ex:
            kwargs_handler_err = ex

    def kwarg_default_handler(value, *, _=True):
        nonlocal kwarg_default_handler_counter
        nonlocal kwarg_default_handler_err
        try:
            assert value == "hello"
            kwarg_default_handler_counter += 1
        except AssertionError as ex:
            kwarg_default_handler_err = ex

    interface.on_some_signal(kwargs_handler)
    interface.on_some_signal(kwarg_default_handler)
    await ping()

    service_interface.SomeSignal()
    await ping()
    assert kwargs_handler_err is None
    assert kwargs_handler_counter == 1
    assert kwarg_default_handler_err is None
    assert kwarg_default_handler_counter == 1

    def kwarg_bad_handler(value, *, bad_kwarg):
        pass

    with pytest.raises(TypeError):
        interface.on_some_signal(kwarg_bad_handler)

    bus1.disconnect()
    bus2.disconnect()


@pytest.mark.asyncio
async def test_coro_callback():
    """Test callback for signal with a coroutine."""
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    await bus1.request_name("test.signals.name")
    service_interface = ExampleInterface()
    bus1.export("/test/path", service_interface)

    obj = bus2.get_proxy_object(
        "test.signals.name", "/test/path", bus1._introspect_export_path("/test/path")
    )
    interface = obj.get_interface(service_interface.name)

    async def ping():
        await bus2.call(
            Message(
                destination=bus1.unique_name,
                interface="org.freedesktop.DBus.Peer",
                path="/test/path",
                member="Ping",
            )
        )

    kwargs_handler_counter = 0
    kwargs_handler_err = None
    kwarg_default_handler_counter = 0
    kwarg_default_handler_err = None

    async def kwargs_handler(value, **_):
        nonlocal kwargs_handler_counter
        nonlocal kwargs_handler_err
        try:
            assert value == "hello"
            kwargs_handler_counter += 1
        except AssertionError as ex:
            kwargs_handler_err = ex

    async def kwarg_default_handler(value, *, _=True):
        nonlocal kwarg_default_handler_counter
        nonlocal kwarg_default_handler_err
        try:
            assert value == "hello"
            kwarg_default_handler_counter += 1
        except AssertionError as ex:
            kwarg_default_handler_err = ex

    interface.on_some_signal(kwargs_handler)
    interface.on_some_signal(kwarg_default_handler)
    await ping()

    service_interface.SomeSignal()
    await ping()
    await asyncio.sleep(0)
    assert kwargs_handler_err is None
    assert kwargs_handler_counter == 1
    assert kwarg_default_handler_err is None
    assert kwarg_default_handler_counter == 1

    def kwarg_bad_handler(value, *, bad_kwarg):
        pass

    with pytest.raises(TypeError):
        interface.on_some_signal(kwarg_bad_handler)

    bus1.disconnect()
    bus2.disconnect()


@pytest.mark.asyncio
async def test_on_signal_type_error():
    """Test on callback raises type errors for invalid callbacks."""
    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()

    await bus1.request_name("test.signals.name")
    service_interface = ExampleInterface()
    bus1.export("/test/path", service_interface)

    obj = bus2.get_proxy_object(
        "test.signals.name", "/test/path", bus1._introspect_export_path("/test/path")
    )
    interface = obj.get_interface(service_interface.name)

    with pytest.raises(TypeError):
        interface.on_some_signal("not_a_callable")

    with pytest.raises(TypeError):
        interface.on_some_signal(lambda a, b: "Too many parameters")

    with pytest.raises(TypeError):
        interface.on_some_signal(lambda: "Too few parameters")

    with pytest.raises(TypeError):
        interface.on_some_signal(lambda a, b, *args: "Too many before varargs")

    bus1.disconnect()
    bus2.disconnect()


@pytest.mark.asyncio
async def test_signals_with_changing_owners():
    well_known_name = "test.signals.changing.name"

    bus1 = await MessageBus().connect()
    bus2 = await MessageBus().connect()
    bus3 = await MessageBus().connect()

    async def ping():
        await bus1.call(
            Message(
                destination=bus1.unique_name,
                interface="org.freedesktop.DBus.Peer",
                path="/test/path",
                member="Ping",
            )
        )

    service_interface = ExampleInterface()
    introspection = Node.default()
    introspection.interfaces.append(service_interface.introspect())

    # get the interface before export
    obj = bus1.get_proxy_object(well_known_name, "/test/path", introspection)
    iface = obj.get_interface("test.interface")
    counter = 0

    def handler(what):
        nonlocal counter
        counter += 1

    iface.on_some_signal(handler)
    await ping()

    # now export and get the name
    bus2.export("/test/path", service_interface)
    result = await bus2.request_name(well_known_name)
    assert result is RequestNameReply.PRIMARY_OWNER

    # the signal should work
    service_interface.SomeSignal()
    await ping()
    assert counter == 1
    counter = 0

    # now queue up a transfer of the name
    service_interface2 = ExampleInterface()
    bus3.export("/test/path", service_interface2)
    result = await bus3.request_name(well_known_name)
    assert result is RequestNameReply.IN_QUEUE

    # if it doesn't own the name, the signal shouldn't work here
    service_interface2.SomeSignal()
    await ping()
    assert counter == 0

    # now transfer over the name and it should work
    bus2.disconnect()
    await ping()

    service_interface2.SomeSignal()
    await ping()
    assert counter == 1
    counter = 0

    bus1.disconnect()
    bus2.disconnect()
    bus3.disconnect()
