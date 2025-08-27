from __future__ import annotations

import os
import xml.etree.ElementTree as ET

from dbus_fast import (
    ArgDirection,
    InvalidMemberNameError,
    PropertyAccess,
    SignatureType,
)
from dbus_fast import introspection as intr
from dbus_fast.constants import ErrorType
from dbus_fast.errors import DBusError
from dbus_fast.message_bus import BaseMessageBus
from dbus_fast.proxy_object import BaseProxyInterface, BaseProxyObject

with open(f"{os.path.dirname(__file__)}/data/strict-introspection.xml") as f:
    strict_data = f.read()

with open(f"{os.path.dirname(__file__)}/data/sloppy-introspection.xml") as f:
    sloppy_data = f.read()


def test_introspection_from_xml_sloppy():
    intr.Node.parse(sloppy_data, validate_property_names=False)


def test_introspection_from_xml_strict():
    try:
        node = intr.Node.parse(sloppy_data)
    except InvalidMemberNameError:
        pass
    else:
        assert False, "Expected an AssertionError"

    node = intr.Node.parse(strict_data)

    assert len(node.interfaces) == 1
    interface = node.interfaces[0]

    assert len(node.nodes) == 2
    assert len(interface.methods) == 3
    assert len(interface.signals) == 2
    assert len(interface.properties) == 1

    assert type(node.nodes[0]) is intr.Node
    assert node.nodes[0].name == "child_of_sample_object"
    assert type(node.nodes[1]) is intr.Node
    assert node.nodes[1].name == "another_child_of_sample_object"

    assert interface.name == "com.example.SampleInterface0"

    frobate = interface.methods[0]
    assert type(frobate) is intr.Method
    assert frobate.name == "Frobate"
    assert len(frobate.in_args) == 1
    assert len(frobate.out_args) == 2

    foo = frobate.in_args[0]
    assert type(foo) is intr.Arg
    assert foo.name == "foo"
    assert foo.direction == ArgDirection.IN
    assert foo.signature == "i"
    assert type(foo.type) is SignatureType
    assert foo.type.token == "i"

    bar = frobate.out_args[0]
    assert type(bar) is intr.Arg
    assert bar.name == "bar"
    assert bar.direction == ArgDirection.OUT
    assert bar.signature == "s"
    assert type(bar.type) is SignatureType
    assert bar.type.token == "s"

    prop = interface.properties[0]
    assert type(prop) is intr.Property
    assert prop.name == "Bar"
    assert prop.signature == "y"
    assert type(prop.type) is SignatureType
    assert prop.type.token == "y"
    assert prop.access == PropertyAccess.WRITE

    changed = interface.signals[0]
    assert type(changed) is intr.Signal
    assert changed.name == "Changed"
    assert len(changed.args) == 1
    new_value = changed.args[0]
    assert type(new_value) is intr.Arg
    assert new_value.name == "0-new_value"
    assert new_value.signature == "b"


def test_example_introspection_to_xml():
    node = intr.Node.parse(strict_data)
    tree = node.to_xml()
    assert tree.tag == "node"
    assert tree.attrib.get("name") == "/com/example/sample_object0"
    assert len(tree) == 3
    interface = tree[0]
    assert interface.tag == "interface"
    assert interface.get("name") == "com.example.SampleInterface0"
    assert len(interface) == 6
    method = interface[0]
    assert method.tag == "method"
    assert method.get("name") == "Frobate"
    assert len(method) == 4

    arg = method[0]
    assert arg.tag == "arg"
    assert arg.attrib.get("name") == "foo"
    assert arg.attrib.get("type") == "i"
    assert arg.attrib.get("direction") == "in"

    annotation = method[3]
    assert annotation.tag == "annotation"
    assert annotation.attrib.get("name") == "org.freedesktop.DBus.Deprecated"
    assert annotation.attrib.get("value") == "true"

    signal = interface[3]
    assert signal.tag == "signal"
    assert signal.attrib.get("name") == "Changed"
    assert len(signal) == 1

    arg = signal[0]
    assert arg.tag == "arg"
    assert arg.attrib.get("name") == "0-new_value"
    assert arg.attrib.get("type") == "b"

    signal = interface[4]
    assert signal.tag == "signal"
    assert signal.attrib.get("name") == "ChangedMulti"
    assert len(signal) == 2

    arg = signal[0]
    assert arg.tag == "arg"
    assert arg.attrib.get("name") == "new_value1"
    assert arg.attrib.get("type") == "b"

    arg = signal[1]
    assert arg.tag == "arg"
    assert arg.attrib.get("name") == "0-new_value2"
    assert arg.attrib.get("type") == "y"

    prop = interface[5]
    assert prop.attrib.get("name") == "Bar"
    assert prop.attrib.get("type") == "y"
    assert prop.attrib.get("access") == "write"


def test_default_interfaces():
    # just make sure it doesn't throw
    default = intr.Node.default()
    assert type(default) is intr.Node


class MockMessageBus(BaseMessageBus):
    def __init__(self, nodes: dict[str, dict[str, intr.Node]]) -> None:
        super().__init__(ProxyObject=MockProxyObject)
        self.nodes = nodes
        self.introspect_count = 0

        # disable bus name tracking for testing purposes
        class MockNameOwners(dict):
            def get(self, key, default):
                return dict.get(self, key, default if default else ":")

        self._name_owners = MockNameOwners()

    def introspect_sync(self, bus_name: str, path: str) -> intr.Node:
        self.introspect_count = self.introspect_count + 1
        service = self.nodes.get(bus_name)
        if service is None:
            raise DBusError(ErrorType.NAME_HAS_NO_OWNER, f"unknown service: {bus_name}")
        node = service.get(path)
        if node is None:
            raise DBusError(ErrorType.UNKNOWN_OBJECT, f"unknown object: {path}")
        return node

    def _setup_socket(self) -> None:
        pass

    def _init_high_level_client(self) -> None:
        pass


class MockProxyInterface(BaseProxyInterface):
    def _add_method(self, intr_method: intr.Method) -> None:
        pass

    def _add_property(self, intr_property: intr.Property) -> None:
        pass


class MockProxyObject(BaseProxyObject):
    def __init__(
        self,
        bus_name: str,
        path: str,
        introspection: intr.Node | str | ET.Element | None,
        bus: BaseMessageBus,
    ) -> None:
        super().__init__(bus_name, path, introspection, bus, MockProxyInterface)


def test_inline_child():
    bus = MockMessageBus(
        {
            "com.example": {
                "/com/example/parent_object": intr.Node.parse(
                    """<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
    "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">
<node name="/com/example/parent_object">
    <interface name="com.example.ParentInterface">
        <method name="ParentMethod"/>
    </interface>
    <node name="child_object">
        <interface name="com.example.ChildInterface">
            <property name="ChildProperty" type="i"/>
        </interface>
    </node>
</node>"""
                )
            }
        }
    )
    introspection = bus.introspect_sync("com.example", "/com/example/parent_object")
    assert bus.introspect_count == 1

    parent = bus.get_proxy_object(
        "com.example", "/com/example/parent_object", introspection
    )
    assert parent.bus_name == "com.example"
    assert parent.path == "/com/example/parent_object"
    assert parent.child_paths == ["/com/example/parent_object/child_object"]
    interface = parent.get_interface("com.example.ParentInterface")
    assert interface.bus_name == "com.example"
    assert interface.path == "/com/example/parent_object"
    assert [method.name for method in interface.introspection.methods] == [
        "ParentMethod"
    ]

    child = next(iter(parent.get_children()))
    assert child.bus_name == "com.example"
    assert child.path == "/com/example/parent_object/child_object"
    interface = child.get_interface("com.example.ChildInterface")
    assert [prop.name for prop in interface.introspection.properties] == [
        "ChildProperty"
    ]

    # getting the inline child should not have required another introspection
    assert bus.introspect_count == 1


def test_noninline_child():
    obj0_node = intr.Node.parse(strict_data)
    bus = MockMessageBus(
        {
            "com.example": {
                obj0_node.name: obj0_node,
                f"{obj0_node.name}/child_of_sample_object": intr.Node.parse(
                    f"""<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
    "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">
<node name="{obj0_node.name}/child_of_sample_object">
    <interface name="com.example.ChildInterface">
        <property name="ChildProperty" type="i"/>
    </interface>
</node>"""
                ),
            }
        }
    )
    introspection = bus.introspect_sync("com.example", "/com/example/sample_object0")
    assert bus.introspect_count == 1
    parent = bus.get_proxy_object(
        "com.example", "/com/example/sample_object0", introspection
    )

    assert parent.path == "/com/example/sample_object0"
    assert parent.child_paths == [
        "/com/example/sample_object0/child_of_sample_object",
        "/com/example/sample_object0/another_child_of_sample_object",
    ]
    children = parent.get_children()
    assert [child.path for child in children] == parent.child_paths

    # merely listing the children should not have required another introspection
    assert bus.introspect_count == 1

    child = next(
        child
        for child in children
        if child.path == "/com/example/sample_object0/child_of_sample_object"
    )
    interface = child.get_interface("com.example.ChildInterface")

    # obtaining the child interface should have required a second introspection
    assert bus.introspect_count == 2

    assert [prop.name for prop in interface.introspection.properties] == [
        "ChildProperty"
    ]
