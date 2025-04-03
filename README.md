# dbus-fast

<p align="center">
  <a href="https://github.com/bluetooth-devices/dbus-fast/actions?query=workflow%3ACI">
    <img src="https://img.shields.io/github/workflow/status/bluetooth-devices/dbus-fast/CI/main?label=CI&logo=github&style=flat-square" alt="CI Status" >
  </a>
  <a href="https://dbus-fast.readthedocs.io">
    <img src="https://img.shields.io/readthedocs/dbus-fast.svg?logo=read-the-docs&logoColor=fff&style=flat-square" alt="Documentation Status">
  </a>
  <a href="https://codecov.io/gh/bluetooth-devices/dbus-fast">
    <img src="https://img.shields.io/codecov/c/github/bluetooth-devices/dbus-fast.svg?logo=codecov&logoColor=fff&style=flat-square" alt="Test coverage percentage">
  </a>
</p>
<p align="center">
  <a href="https://python-poetry.org/">
    <img src="https://img.shields.io/badge/packaging-poetry-299bd7?style=flat-square&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAASCAYAAABrXO8xAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAJJSURBVHgBfZLPa1NBEMe/s7tNXoxW1KJQKaUHkXhQvHgW6UHQQ09CBS/6V3hKc/AP8CqCrUcpmop3Cx48eDB4yEECjVQrlZb80CRN8t6OM/teagVxYZi38+Yz853dJbzoMV3MM8cJUcLMSUKIE8AzQ2PieZzFxEJOHMOgMQQ+dUgSAckNXhapU/NMhDSWLs1B24A8sO1xrN4NECkcAC9ASkiIJc6k5TRiUDPhnyMMdhKc+Zx19l6SgyeW76BEONY9exVQMzKExGKwwPsCzza7KGSSWRWEQhyEaDXp6ZHEr416ygbiKYOd7TEWvvcQIeusHYMJGhTwF9y7sGnSwaWyFAiyoxzqW0PM/RjghPxF2pWReAowTEXnDh0xgcLs8l2YQmOrj3N7ByiqEoH0cARs4u78WgAVkoEDIDoOi3AkcLOHU60RIg5wC4ZuTC7FaHKQm8Hq1fQuSOBvX/sodmNJSB5geaF5CPIkUeecdMxieoRO5jz9bheL6/tXjrwCyX/UYBUcjCaWHljx1xiX6z9xEjkYAzbGVnB8pvLmyXm9ep+W8CmsSHQQY77Zx1zboxAV0w7ybMhQmfqdmmw3nEp1I0Z+FGO6M8LZdoyZnuzzBdjISicKRnpxzI9fPb+0oYXsNdyi+d3h9bm9MWYHFtPeIZfLwzmFDKy1ai3p+PDls1Llz4yyFpferxjnyjJDSEy9CaCx5m2cJPerq6Xm34eTrZt3PqxYO1XOwDYZrFlH1fWnpU38Y9HRze3lj0vOujZcXKuuXm3jP+s3KbZVra7y2EAAAAAASUVORK5CYII=" alt="Poetry">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff">
  </a>
  <a href="https://github.com/pre-commit/pre-commit">
    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat-square" alt="pre-commit">
  </a>
  <a href="https://codspeed.io/Bluetooth-Devices/dbus-fast"><img src="https://img.shields.io/endpoint?url=https://codspeed.io/badge.json" alt="CodSpeed Badge"/></a>
</p>
<p align="center">
  <a href="https://pypi.org/project/dbus-fast/">
    <img src="https://img.shields.io/pypi/v/dbus-fast.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPI Version">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/dbus-fast.svg?style=flat-square&logo=python&amp;logoColor=fff" alt="Supported Python versions">
  <img src="https://img.shields.io/pypi/l/dbus-fast.svg?style=flat-square" alt="License">
</p>

A faster version of dbus-next originally from the [great DBus next library](https://github.com/altdesktop/python-dbus-next) ❤️

## Installation

Install this via pip (or your favourite package manager):

`pip install dbus-fast`

[Documentation](https://dbus-fast.readthedocs.io/en/latest/)

dbus-fast is a Python library for DBus that aims to be a performant fully featured high level library primarily geared towards integration of applications into Linux desktop and mobile environments.

Desktop application developers can use this library for integrating their applications into desktop environments by implementing common DBus standard interfaces or creating custom plugin interfaces.

Desktop users can use this library to create their own scripts and utilities to interact with those interfaces for customization of their desktop environment.

dbus-fast plans to improve over other DBus libraries for Python in the following ways:

- Zero dependencies and pure Python 3
- An optional cython extension is available to speed up (un)marshalling
- Focus on performance
- Support for multiple IO backends including asyncio and the GLib main loop.
- Nonblocking IO suitable for GUI development.
- Target the latest language features of Python for beautiful services and clients.
- Complete implementation of the DBus type system without ever guessing types.
- Integration tests for all features of the library.
- Completely documented public API.

## Installing

This library is available on PyPi as [dbus-fast](https://pypi.org/project/dbus-fast/).

```
pip3 install dbus-fast
```

## The Client Interface

To use a service on the bus, the library constructs a proxy object you can use to call methods, get and set properties, and listen to signals.

For more information, see the [overview for the high-level client](https://dbus-fast.readthedocs.io/en/latest/high-level-client/index.html).

This example connects to a media player and controls it with the [MPRIS](https://specifications.freedesktop.org/mpris-spec/latest/) DBus interface.

```python
from dbus_fast.aio import MessageBus

import asyncio


async def main():
    bus = await MessageBus().connect()
    # the introspection xml would normally be included in your project, but
    # this is convenient for development
    introspection = await bus.introspect('org.mpris.MediaPlayer2.vlc', '/org/mpris/MediaPlayer2')

    obj = bus.get_proxy_object('org.mpris.MediaPlayer2.vlc', '/org/mpris/MediaPlayer2', introspection)
    player = obj.get_interface('org.mpris.MediaPlayer2.Player')
    properties = obj.get_interface('org.freedesktop.DBus.Properties')

    # call methods on the interface (this causes the media player to play)
    await player.call_play()

    volume = await player.get_volume()
    print(f'current volume: {volume}, setting to 0.5')

    await player.set_volume(0.5)

    # listen to signals
    def on_properties_changed(interface_name, changed_properties, invalidated_properties):
        for changed, variant in changed_properties.items():
            print(f'property changed: {changed} - {variant.value}')

    properties.on_properties_changed(on_properties_changed)

    await asyncio.Event().wait()

asyncio.run(main())
```

## The Service Interface

To define a service on the bus, use the `ServiceInterface` class and decorate class methods to specify DBus methods, properties, and signals with their type signatures.

For more information, see the [overview for the high-level service](https://dbus-fast.readthedocs.io/en/latest/high-level-service/index.html).

```python
from dbus_fast.service import ServiceInterface, method, dbus_property, signal, Variant
from dbus_fast.aio MessageBus

import asyncio

class ExampleInterface(ServiceInterface):
    def __init__(self, name):
        super().__init__(name)
        self._string_prop = 'kevin'

    @method()
    def Echo(self, what: 's') -> 's':
        return what

    @method()
    def GetVariantDict() -> 'a{sv}':
        return {
            'foo': Variant('s', 'bar'),
            'bat': Variant('x', -55),
            'a_list': Variant('as', ['hello', 'world'])
        }

    @dbus_property()
    def string_prop(self) -> 's':
        return self._string_prop

    @string_prop.setter
    def string_prop_setter(self, val: 's'):
        self._string_prop = val

    @signal()
    def signal_simple(self) -> 's':
        return 'hello'

async def main():
    bus = await MessageBus().connect()
    interface = ExampleInterface('test.interface')
    bus.export('/test/path', interface)
    # now that we are ready to handle requests, we can request name from D-Bus
    await bus.request_name('test.name')
    # wait indefinitely
    await asyncio.Event().wait()

asyncio.run(main())
```

## The Low-Level Interface

The low-level interface works with DBus messages directly.

For more information, see the [overview for the low-level interface](https://dbus-fast.readthedocs.io/en/latest/low-level-interface/index.html).

```python
from dbus_fast.message import Message, MessageType
from dbus_fast.aio import MessageBus

import asyncio
import json


async def main():
    bus = await MessageBus().connect()

    reply = await bus.call(
        Message(destination='org.freedesktop.DBus',
                path='/org/freedesktop/DBus',
                interface='org.freedesktop.DBus',
                member='ListNames'))

    if reply.message_type == MessageType.ERROR:
        raise Exception(reply.body[0])

    print(json.dumps(reply.body[0], indent=2))


asyncio.run(main())
```

## Projects that use python-dbus-fast

- [Bluetooth Adapters](https://github.com/bluetooth-devices/bluetooth-adapters)

## Contributing

Contributions are welcome. Development happens on [Github](https://github.com/Bluetooth-Devices/dbus-fast).

Before you commit, run `pre-commit run --all-files` to run the linter, code formatter, and the test suite.

## Copyright

You can use this code under an MIT license (see LICENSE).

- © 2019, Tony Crisci
- © 2022, Bluetooth Devices authors

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- prettier-ignore-start -->
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- markdownlint-disable -->
<!-- markdownlint-enable -->
<!-- ALL-CONTRIBUTORS-LIST:END -->
<!-- prettier-ignore-end -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

## Credits

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[browniebroke/cookiecutter-pypackage](https://github.com/browniebroke/cookiecutter-pypackage)
project template.
