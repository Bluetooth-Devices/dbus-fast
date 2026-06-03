import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from dbus_fast import (
    ArgDirection,
    InvalidIntrospectionError,
    InvalidMemberNameError,
    PropertyAccess,
    SignatureType,
)
from dbus_fast import introspection as intr
from dbus_fast.signature import get_signature_tree

_DATA_DIR = Path(__file__).parent / "data"

with (_DATA_DIR / "strict-introspection.xml").open() as f:
    strict_data = f.read()

with (_DATA_DIR / "sloppy-introspection.xml").open() as f:
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


def test_introspection_rejects_billion_laughs() -> None:
    """Nested-entity expansion in an Introspect reply is rejected."""
    payload = (
        '<?xml version="1.0"?>'
        "<!DOCTYPE node ["
        '<!ENTITY a "AAAAAAAAAA">'
        '<!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;">'
        '<!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;">'
        "]>"
        "<node>&c;</node>"
    )
    with pytest.raises(InvalidIntrospectionError, match="internal DTD"):
        intr.Node.parse(payload)


def test_introspection_rejects_quadratic_blowup() -> None:
    """A single large entity referenced many times is rejected."""
    payload = (
        '<?xml version="1.0"?>'
        "<!DOCTYPE node ["
        '<!ENTITY pad "' + ("A" * 1024) + '">'
        "]>"
        "<node>" + ("&pad;" * 64) + "</node>"
    )
    with pytest.raises(InvalidIntrospectionError, match="internal DTD"):
        intr.Node.parse(payload)


def test_introspection_rejects_xxe_external_entity() -> None:
    """External-entity declarations are rejected even without expansion."""
    payload = (
        '<?xml version="1.0"?>'
        "<!DOCTYPE node ["
        '<!ENTITY xxe SYSTEM "file:///etc/passwd">'
        "]>"
        "<node>&xxe;</node>"
    )
    with pytest.raises(InvalidIntrospectionError, match="internal DTD"):
        intr.Node.parse(payload)


def test_introspection_rejects_attlist_amplification() -> None:
    """ATTLIST default-value declarations are rejected (amplification vector)."""
    payload = (
        '<?xml version="1.0"?>'
        "<!DOCTYPE node ["
        '<!ATTLIST node bogus CDATA "' + ("A" * 1024) + '">'
        "]>"
        "<node/>"
    )
    with pytest.raises(InvalidIntrospectionError, match="internal DTD"):
        intr.Node.parse(payload)


def test_introspection_accepts_standard_doctype() -> None:
    """The standard D-Bus introspection DOCTYPE (no internal subset) parses."""
    payload = (
        '<?xml version="1.0"?>\n'
        '<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"\n'
        '"http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">\n'
        '<node><interface name="org.example.Iface"/></node>'
    )
    node = intr.Node.parse(payload)
    assert len(node.interfaces) == 1
    assert node.interfaces[0].name == "org.example.Iface"


def test_introspection_malformed_xml_raises_parse_error() -> None:
    """Malformed XML still raises ET.ParseError, not a silent failure."""
    with pytest.raises(ET.ParseError):
        intr.Node.parse("<node><unclosed")


def test_introspection_parse_error_preserves_code_and_position() -> None:
    """ET.ParseError still carries the expat code and position metadata."""
    with pytest.raises(ET.ParseError) as excinfo:
        intr.Node.parse("<bad")
    assert excinfo.value.code  # non-zero expat error code
    assert isinstance(excinfo.value.position, tuple)
    assert len(excinfo.value.position) == 2


def test_introspection_rejects_default_namespaced_root() -> None:
    """A namespaced <node> root is still rejected by the root-tag check."""
    payload = '<node xmlns="urn:example"><interface name="a"/></node>'
    with pytest.raises(InvalidIntrospectionError, match="node"):
        intr.Node.parse(payload)


def test_introspection_rejects_deeply_nested_nodes() -> None:
    """Deeply nested <node> elements are bounded to avoid stack exhaustion."""
    depth = intr._MAX_NODE_DEPTH + 8
    payload = "<node>" + ('<node name="x">' * depth) + ("</node>" * depth) + "</node>"
    with pytest.raises(InvalidIntrospectionError, match="nesting"):
        intr.Node.parse(payload)


def test_introspection_accepts_nesting_up_to_cap() -> None:
    """Nesting up to the cap parses without raising."""
    depth = intr._MAX_NODE_DEPTH
    payload = "<node>" + ('<node name="x">' * depth) + ("</node>" * depth) + "</node>"
    node = intr.Node.parse(payload)
    cursor = node
    for _ in range(depth):
        assert len(cursor.nodes) == 1
        cursor = cursor.nodes[0]
    assert cursor.nodes == []


# Each wrapper routes the embedded annotation through a distinct
# _fetch_annotations call site: interface, method, signal, property, arg.
_ANNOTATION_CONTAINERS = [
    '<node><interface name="a.b">{ann}</interface></node>',
    '<node><interface name="a.b"><method name="M">{ann}</method></interface></node>',
    '<node><interface name="a.b"><signal name="S">{ann}</signal></interface></node>',
    '<node><interface name="a.b"><property name="P" type="s">{ann}</property></interface></node>',
    '<node><interface name="a.b"><method name="M"><arg type="s">{ann}</arg></method></interface></node>',
]


@pytest.mark.parametrize("container", _ANNOTATION_CONTAINERS)
@pytest.mark.parametrize(
    "annotation",
    [
        "<annotation/>",
        '<annotation value="x"/>',
        '<annotation name=""/>',
    ],
)
def test_introspection_rejects_annotation_missing_name(
    container: str, annotation: str
) -> None:
    """A name-less annotation raises at every _fetch_annotations call site."""
    with pytest.raises(
        InvalidIntrospectionError, match='annotations must have a "name"'
    ):
        intr.Node.parse(container.format(ann=annotation))


@pytest.mark.parametrize("container", _ANNOTATION_CONTAINERS)
def test_introspection_rejects_annotation_missing_value(container: str) -> None:
    """A value-less annotation raises at every _fetch_annotations call site."""
    with pytest.raises(
        InvalidIntrospectionError, match='annotations must have a "value"'
    ):
        intr.Node.parse(container.format(ann='<annotation name="x"/>'))


def test_introspection_accepts_annotation_empty_value() -> None:
    """An empty string value is valid and preserved (only a missing value raises)."""
    payload = (
        '<node><interface name="a.b"><annotation name="x" value=""/></interface></node>'
    )
    node = intr.Node.parse(payload)
    assert node.interfaces[0].annotations == {"x": ""}


@pytest.mark.parametrize(
    ("payload", "match"),
    [
        ("<node><interface/></node>", 'interfaces must have a "name"'),
        (
            '<node><interface name="a.b"><method/></interface></node>',
            'methods must have a "name"',
        ),
        (
            '<node><interface name="a.b"><signal/></interface></node>',
            'signals must have a "name"',
        ),
        (
            '<node><interface name="a.b"><property type="s"/></interface></node>',
            'properties must have a "name"',
        ),
        (
            '<node><interface name="a.b"><property name="P"/></interface></node>',
            'properties must have a "type"',
        ),
        (
            '<node><interface name="a.b"><property name="P" type="ss"/></interface></node>',
            "properties must have a single complete type",
        ),
        (
            '<node><interface name="a.b"><method name="M"><arg/></method></interface></node>',
            'a method argument must have a "type"',
        ),
        (
            '<node><interface name="a.b"><method name="M"><arg type="ss"/></method></interface></node>',
            "an argument must have a single complete type",
        ),
        ("<node><node/></node>", 'child nodes must have a "name"'),
    ],
)
def test_introspection_rejects_element_missing_required_attribute(
    payload: str, match: str
) -> None:
    """Each introspection element rejects malformed/missing required attributes."""
    with pytest.raises(InvalidIntrospectionError, match=match):
        intr.Node.parse(payload)


def test_introspection_tostring_round_trips() -> None:
    """tostring() emits the DOCTYPE header and re-parses to an equal tree."""
    node = intr.Node.parse(strict_data)
    xml = node.tostring()
    assert xml.startswith("<!DOCTYPE node PUBLIC")
    assert intr.Node.parse(xml).interfaces[0].name == node.interfaces[0].name


def test_introspection_arg_to_xml_omits_unset_name_and_direction() -> None:
    """An Arg without a name or direction serialises with just a type."""
    assert intr.Arg("s").to_xml().attrib == {"type": "s"}


def test_introspection_arg_accepts_signature_type() -> None:
    """Arg accepts a parsed SignatureType in place of a signature string."""
    sig_type = get_signature_tree("s").types[0]
    arg = intr.Arg(sig_type)
    assert arg.signature == "s"
    assert arg.type is sig_type


def test_introspection_signal_allows_none_name() -> None:
    """Signal(None) skips member-name validation."""
    assert intr.Signal(None).name is None


def test_introspection_node_to_xml_omits_unset_name() -> None:
    """A nameless Node serialises without a name attribute."""
    assert "name" not in intr.Node().to_xml().attrib


def test_introspection_ignores_unknown_node_children() -> None:
    """Unknown child elements under <node> are skipped, not rejected."""
    node = intr.Node.parse("<node><foo/></node>")
    assert node.interfaces == []
    assert node.nodes == []
