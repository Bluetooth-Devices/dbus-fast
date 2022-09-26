#!/usr/bin/env python3
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

import asyncio

from dbus_fast import Variant
from dbus_fast.aio.message_bus import MessageBus
from dbus_fast.service import ServiceInterface, dbus_property, method, signal


class ExampleInterface(ServiceInterface):
    def __init__(self, name):
        super().__init__(name)
        self._string_prop = "kevin"

    @method()
    def Echo(self, what: "s") -> "s":
        return what

    @method()
    def EchoMultiple(self, what1: "s", what2: "s") -> "ss":
        return [what1, what2]

    @method()
    def GetVariantDict(self) -> "a{sv}":
        return {
            "foo": Variant("s", "bar"),
            "bat": Variant("x", -55),
            "a_list": Variant("as", ["hello", "world"]),
        }

    @dbus_property(name="StringProp")
    def string_prop(self) -> "s":
        return self._string_prop

    @string_prop.setter
    def string_prop_setter(self, val: "s"):
        self._string_prop = val

    @signal()
    def signal_simple(self) -> "s":
        return "hello"

    @signal()
    def signal_multiple(self) -> "ss":
        return ["hello", "world"]


async def main():
    name = "dbus.next.example.service"
    path = "/example/path"
    interface_name = "example.interface"

    bus = await MessageBus().connect()
    interface = ExampleInterface(interface_name)
    bus.export("/example/path", interface)
    await bus.request_name(name)
    print(
        f'service up on name: "{name}", path: "{path}", interface: "{interface_name}"'
    )
    await bus.wait_for_disconnect()


asyncio.run(main())
