"""
The :mod:`dbus_fast.annotations` module contains type aliases that can be used in
place of D-Bus signature strings in order to get proper Python type hints. This
applies to methods decorated with :meth:`dbus_property <dbus_fast.service.dbus_property>`,
:meth:`dbus_method <dbus_fast.service.dbus_method>` or :meth:`dbus_signal
<dbus_fast.service.dbus_signal>`.

This module only includes common types. You can construct your own annotated
types like this::

    from typing import Annotated

    MyDBusStruct = Annotated[tuple[int, str], "(is)"]

Or you can use ``Annotated[...]`` directly without creating an alias.

.. versionadded:: v3.2.0
    Prior to this version, annotations had to be specified as D-Bus signature
    strings.
"""

from typing import Annotated

from dbus_fast.signature import Variant

__all__ = [
    "DBusBool",
    "DBusByte",
    "DBusDict",
    "DBusDouble",
    "DBusInt16",
    "DBusInt32",
    "DBusInt64",
    "DBusObjectPath",
    "DBusSignature",
    "DBusStr",
    "DBusUInt16",
    "DBusUInt32",
    "DBusUInt64",
    "DBusVariant",
]

DBusBool = Annotated[bool, "b"]
"""
D-Bus BOOLEAN type ("b").
"""
DBusByte = Annotated[int, "y"]
"""
D-Bus BYTE type ("y").
"""
DBusInt16 = Annotated[int, "n"]
"""
D-Bus INT16 type ("n").
"""
DBusUInt16 = Annotated[int, "q"]
"""
D-Bus UINT16 type ("q").
"""
DBusInt32 = Annotated[int, "i"]
"""
D-Bus INT32 type ("i").
"""
DBusUInt32 = Annotated[int, "u"]
"""
D-Bus UINT32 type ("u").
"""
DBusInt64 = Annotated[int, "x"]
"""
D-Bus INT64 type ("x").
"""
DBusUInt64 = Annotated[int, "t"]
"""
D-Bus UINT64 type ("t").
"""
DBusDouble = Annotated[float, "d"]
"""
D-Bus DOUBLE type ("d").
"""
DBusStr = Annotated[str, "s"]
"""
D-Bus STRING type ("s").
"""
DBusObjectPath = Annotated[str, "o"]
"""
D-Bus OBJECT_PATH type ("o").
"""
DBusSignature = Annotated[str, "g"]
"""
D-Bus SIGNATURE type ("g").
"""
DBusVariant = Annotated[Variant, "v"]
"""
D-Bus VARIANT type ("v").
"""
DBusDict = Annotated[dict[str, Variant], "a{sv}"]
"""
D-Bus ARRAY of DICT_ENTRY type with STRING keys and VARIANT values ("a{sv}").
"""
DBusUnixFd = Annotated[int, "h"]
"""
D-Bus UNIX_FD type ("h").
"""
DBusBytes = Annotated[bytes, "ay"]
"""
D-Bus ARRAY of BYTE type ("ay").
"""
