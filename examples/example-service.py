#!/usr/bin/env python3
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

import asyncio
from typing import Annotated

from dbus_fast import Variant
from dbus_fast.aio.message_bus import MessageBus
from dbus_fast.annotations import DBusDict, DBusStr
from dbus_fast.service import ServiceInterface, dbus_method, dbus_property, dbus_signal


class ExampleInterface(ServiceInterface):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._string_prop = "kevin"

    @dbus_method()
    def Echo(self, what: DBusStr) -> DBusStr:
        return what

    @dbus_method()
    def EchoMultiple(
        self, what1: DBusStr, what2: DBusStr
    ) -> Annotated[tuple[DBusStr, DBusStr], "ss"]:
        return what1, what2

    @dbus_method()
    def GetVariantDict(self) -> DBusDict:
        return {
            "foo": Variant("s", "bar"),
            "bat": Variant("x", -55),
            "a_list": Variant("as", ["hello", "world"]),
        }

    @dbus_property(name="StringProp")
    def string_prop(self) -> DBusStr:
        return self._string_prop

    @string_prop.setter
    def string_prop_setter(self, val: DBusStr) -> None:
        self._string_prop = val

    @dbus_signal()
    def signal_simple(self) -> DBusStr:
        return "hello"

    @dbus_signal()
    def signal_multiple(self) -> Annotated[tuple[DBusStr, DBusStr], "ss"]:
        return "hello", "world"


async def main() -> None:
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
