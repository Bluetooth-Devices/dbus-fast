import pytest

from dbus_fast import SignatureBodyMismatchError, SignatureTree, Variant
from dbus_fast._private.unmarshaller import is_compiled
from dbus_fast._private.util import signature_contains_type
from dbus_fast.errors import InternalError, InvalidSignatureError
from dbus_fast.signature import SignatureType, get_signature_tree


def assert_simple_type(signature, type_):
    assert type_.token == signature
    assert type_.signature == signature
    assert len(type_.children) == 0


def test_simple():
    tree = SignatureTree("s")
    assert len(tree.types) == 1
    assert_simple_type("s", tree.types[0])


def test_multiple_simple():
    tree = SignatureTree("sss")
    assert len(tree.types) == 3
    for i in range(3):
        assert_simple_type("s", tree.types[i])


def test_children():
    tree = SignatureTree("ss")
    assert len(tree.types) == 2
    parent = tree.types[0]
    assert parent.token == "s"
    assert parent.signature == "s"
    assert len(parent.children) == 0


def test_array():
    tree = SignatureTree("as")
    assert len(tree.types) == 1
    child = tree.types[0]
    assert child.signature == "as"
    assert child.token == "a"
    assert len(child.children) == 1
    assert_simple_type("s", child.children[0])
    assert child.children[0].token == "s"
    assert child._child_0.signature == "s"
    assert child._child_1 is None
    with pytest.raises(AttributeError):
        _ = child._child_1.signature


def test_array_multiple():
    tree = SignatureTree("asasass")
    assert len(tree.types) == 4
    assert_simple_type("s", tree.types[3])
    for i in range(3):
        array_child = tree.types[i]
        assert array_child.token == "a"
        assert array_child.signature == "as"
        assert len(array_child.children) == 1
        assert_simple_type("s", array_child.children[0])


def test_array_nested():
    tree = SignatureTree("aas")
    assert len(tree.types) == 1
    child = tree.types[0]
    assert child.token == "a"
    assert child.signature == "aas"
    assert len(child.children) == 1
    nested_child = child.children[0]
    assert nested_child.token == "a"
    assert nested_child.signature == "as"
    assert len(nested_child.children) == 1
    assert_simple_type("s", nested_child.children[0])


def test_simple_struct():
    tree = SignatureTree("(sss)")
    assert len(tree.types) == 1
    child = tree.types[0]
    assert child.signature == "(sss)"
    assert len(child.children) == 3
    for i in range(3):
        assert_simple_type("s", child.children[i])
    assert child._child_0.signature == "s"
    assert child._child_1.signature == "s"


def test_nested_struct():
    tree = SignatureTree("(s(s(s)))")
    assert len(tree.types) == 1
    child = tree.types[0]
    assert child.signature == "(s(s(s)))"
    assert child.token == "("
    assert len(child.children) == 2
    assert_simple_type("s", child.children[0])
    first_nested = child.children[1]
    assert first_nested.token == "("
    assert first_nested.signature == "(s(s))"
    assert len(first_nested.children) == 2
    assert_simple_type("s", first_nested.children[0])
    second_nested = first_nested.children[1]
    assert second_nested.token == "("
    assert second_nested.signature == "(s)"
    assert len(second_nested.children) == 1
    assert_simple_type("s", second_nested.children[0])


def test_struct_multiple():
    tree = SignatureTree("(s)(s)(s)")
    assert len(tree.types) == 3
    for i in range(3):
        child = tree.types[0]
        assert child.token == "("
        assert child.signature == "(s)"
        assert len(child.children) == 1
        assert_simple_type("s", child.children[0])


def test_array_of_structs():
    tree = SignatureTree("a(ss)")
    assert len(tree.types) == 1
    child = tree.types[0]
    assert child.token == "a"
    assert child.signature == "a(ss)"
    assert len(child.children) == 1
    struct_child = child.children[0]
    assert struct_child.token == "("
    assert struct_child.signature == "(ss)"
    assert len(struct_child.children) == 2
    for i in range(2):
        assert_simple_type("s", struct_child.children[i])


def test_dict_simple():
    tree = SignatureTree("a{ss}")
    assert len(tree.types) == 1
    child = tree.types[0]
    assert child.signature == "a{ss}"
    assert child.token == "a"
    assert len(child.children) == 1
    dict_child = child.children[0]
    assert dict_child.token == "{"
    assert dict_child.signature == "{ss}"
    assert len(dict_child.children) == 2
    assert_simple_type("s", dict_child.children[0])
    assert_simple_type("s", dict_child.children[1])


def test_dict_of_structs():
    tree = SignatureTree("a{s(ss)}")
    assert len(tree.types) == 1
    child = tree.types[0]
    assert child.token == "a"
    assert child.signature == "a{s(ss)}"
    assert len(child.children) == 1
    dict_child = child.children[0]
    assert dict_child.token == "{"
    assert dict_child.signature == "{s(ss)}"
    assert len(dict_child.children) == 2
    assert_simple_type("s", dict_child.children[0])
    struct_child = dict_child.children[1]
    assert struct_child.token == "("
    assert struct_child.signature == "(ss)"
    assert len(struct_child.children) == 2
    for i in range(2):
        assert_simple_type("s", struct_child.children[i])


def test_contains_type():
    tree = SignatureTree("h")
    assert signature_contains_type(tree, [0], "h")
    assert not signature_contains_type(tree, [0], "u")

    tree = SignatureTree("ah")
    assert signature_contains_type(tree, [[0]], "h")
    assert signature_contains_type(tree, [[0]], "a")
    assert not signature_contains_type(tree, [[0]], "u")

    tree = SignatureTree("av")
    body = [
        [
            Variant("u", 0),
            Variant("i", 0),
            Variant("x", 0),
            Variant("v", Variant("s", "hi")),
        ]
    ]
    assert signature_contains_type(tree, body, "u")
    assert signature_contains_type(tree, body, "x")
    assert signature_contains_type(tree, body, "v")
    assert signature_contains_type(tree, body, "s")
    assert not signature_contains_type(tree, body, "o")

    tree = SignatureTree("a{sv}")
    body = {
        "foo": Variant("h", 0),
        "bar": Variant("i", 0),
        "bat": Variant("x", 0),
        "baz": Variant("v", Variant("o", "/hi")),
    }
    for expected in "hixvso":
        assert signature_contains_type(tree, [body], expected)
    assert not signature_contains_type(tree, [body], "b")


def test_invalid_variants():
    tree = SignatureTree("a{sa{sv}}")
    s_con = {
        "type": "802-11-wireless",
        "uuid": "1234",
        "id": "SSID",
    }

    s_wifi = {
        "ssid": "SSID",
        "mode": "infrastructure",
        "hidden": True,
    }

    s_wsec = {
        "key-mgmt": "wpa-psk",
        "auth-alg": "open",
        "psk": "PASSWORD",
    }

    s_ip4 = {"method": "auto"}
    s_ip6 = {"method": "auto"}

    con = {
        "connection": s_con,
        "802-11-wireless": s_wifi,
        "802-11-wireless-security": s_wsec,
        "ipv4": s_ip4,
        "ipv6": s_ip6,
    }

    with pytest.raises(SignatureBodyMismatchError):
        tree.verify([con])


def test_variant_signature_type():
    tree = SignatureTree("as")
    var = Variant(tree.types[0], ["foo", "bar"])
    assert var.type == tree.types[0]
    assert var.value == ["foo", "bar"]
    assert var.signature == "as"

    with pytest.raises(SignatureBodyMismatchError):
        Variant(tree.types[0], "wrong")


def test_struct_accepts_tuples_or_lists():
    tree = SignatureTree("(s)")
    tree.verify([("ok",)])
    tree.verify([["ok"]])


# --- Parse-error paths in SignatureType._parse_next / SignatureTree ---


def test_parse_empty_signature_inside_container_raises():
    with pytest.raises(InvalidSignatureError, match="empty signature"):
        SignatureTree("a")


def test_parse_unknown_token_raises():
    with pytest.raises(InvalidSignatureError, match="unexpected token"):
        SignatureTree("z")


def test_parse_array_missing_child_raises():
    # SignatureType._parse_next is called recursively; a lone "a" hits the
    # "empty signature" branch first. Force the "missing type for array"
    # branch by feeding an unterminated struct after the array.
    with pytest.raises(InvalidSignatureError):
        SignatureTree("a(")


def test_parse_struct_missing_close_raises():
    with pytest.raises(InvalidSignatureError, match='missing closing "\\)"'):
        SignatureTree("(ss")


def test_parse_dict_entry_key_not_simple_raises():
    # Key must be a basic type, not a container
    with pytest.raises(InvalidSignatureError, match="simple type for dict entry key"):
        SignatureTree("a{(s)s}")


def test_parse_dict_entry_missing_close_raises():
    with pytest.raises(InvalidSignatureError, match='missing closing "}"'):
        SignatureTree("a{ss")


def test_signature_too_long_raises():
    long_sig = "s" * 256
    with pytest.raises(InvalidSignatureError, match="less than 256 characters"):
        SignatureTree(long_sig)


# --- SignatureType.__eq__ ---


def test_signature_type_eq_with_string_falls_back_to_super():
    t = SignatureTree("s").types[0]
    # Comparison against a non-SignatureType returns NotImplemented from the
    # default object __eq__, which Python interprets as False.
    assert (t == "s") is False
    assert t != 42


def test_signature_type_eq_with_other_signature_type():
    a = SignatureTree("as").types[0]
    b = SignatureTree("as").types[0]
    c = SignatureTree("ai").types[0]
    assert a == b
    assert a != c


# --- _verify_* error paths ---


def _expect_mismatch(signature, value, match=None):
    tree = SignatureTree(signature)
    with pytest.raises(SignatureBodyMismatchError, match=match):
        tree.verify([value])


def test_verify_byte_wrong_type():
    _expect_mismatch("y", "not an int", match="BYTE")


def test_verify_byte_out_of_range_low():
    _expect_mismatch("y", -1, match="between")


def test_verify_byte_out_of_range_high():
    _expect_mismatch("y", 0x100, match="between")


def test_verify_boolean_wrong_type():
    _expect_mismatch("b", 1, match="BOOLEAN")


def test_verify_int16_wrong_type():
    _expect_mismatch("n", "x", match="INT16")


def test_verify_int16_out_of_range():
    _expect_mismatch("n", 0x8000, match="between")
    _expect_mismatch("n", -0x8001, match="between")


def test_verify_uint16_wrong_type():
    _expect_mismatch("q", "x", match="UINT16")


def test_verify_uint16_out_of_range():
    _expect_mismatch("q", -1, match="between")
    _expect_mismatch("q", 0x10000, match="between")


@pytest.mark.skipif(
    is_compiled(),
    reason="_verify_int32 has a strict int annotation; Cython enforces it before the isinstance check",
)
def test_verify_int32_wrong_type():
    _expect_mismatch("i", "x", match="INT32")


def test_verify_int32_out_of_range():
    _expect_mismatch("i", 0x80000000, match="between")
    _expect_mismatch("i", -0x80000001, match="between")


def test_verify_uint32_wrong_type():
    _expect_mismatch("u", "x", match="UINT32")


def test_verify_uint32_out_of_range():
    _expect_mismatch("u", -1, match="between")
    _expect_mismatch("u", 0x100000000, match="between")


def test_verify_int64_wrong_type():
    _expect_mismatch("x", "x", match="INT64")


def test_verify_int64_out_of_range():
    _expect_mismatch("x", 1 << 63, match="between")
    _expect_mismatch("x", -(1 << 63) - 1, match="between")


def test_verify_uint64_wrong_type():
    _expect_mismatch("t", "x", match="UINT64")


def test_verify_uint64_out_of_range():
    _expect_mismatch("t", -1, match="between")
    _expect_mismatch("t", 1 << 64, match="between")


def test_verify_double_wrong_type():
    _expect_mismatch("d", "x", match="DOUBLE")


def test_verify_double_accepts_int_and_float():
    SignatureTree("d").verify([1])
    SignatureTree("d").verify([1.5])


def test_verify_unix_fd_wraps_uint32_error():
    _expect_mismatch("h", -1, match="UNIX_FD")
    _expect_mismatch("h", "x", match="UNIX_FD")


def test_verify_unix_fd_accepts_valid_uint32():
    SignatureTree("h").verify([0])
    SignatureTree("h").verify([0xFFFFFFFF])


def test_verify_object_path_invalid():
    _expect_mismatch("o", "not a path", match="OBJECT_PATH")
    _expect_mismatch("o", "missing/leading/slash", match="OBJECT_PATH")
    _expect_mismatch("o", "", match="OBJECT_PATH")


def test_verify_object_path_wrong_type():
    _expect_mismatch("o", 5, match="OBJECT_PATH")
    _expect_mismatch("o", [], match="OBJECT_PATH")
    _expect_mismatch("o", {}, match="OBJECT_PATH")


def test_verify_object_path_accepts_valid():
    SignatureTree("o").verify(["/"])
    SignatureTree("o").verify(["/com/example/Object"])


def test_verify_string_wrong_type():
    _expect_mismatch("s", 5, match="STRING")


def test_verify_signature_wrong_type():
    _expect_mismatch("g", 5, match="SIGNATURE")


def test_verify_signature_too_long():
    _expect_mismatch("g", "s" * 256, match="less than 256 bytes")


def test_verify_array_dict_wrong_container():
    _expect_mismatch("a{ss}", ["not a dict"], match="DICT_ENTRY")


def test_verify_array_bytes_wrong_type():
    _expect_mismatch("ay", [1, 2, 3], match="BYTE")


def test_verify_array_bytes_accepts_bytes_and_bytearray():
    SignatureTree("ay").verify([b"hello"])
    SignatureTree("ay").verify([bytearray(b"hello")])


def test_verify_array_wrong_container():
    _expect_mismatch("as", "not a list", match='must be Python type "list"')


def test_verify_struct_wrong_type():
    _expect_mismatch("(ss)", "not a tuple", match="STRUCT")


def test_verify_struct_wrong_length():
    _expect_mismatch(
        "(ss)", ["only one"], match="members equal to the number of struct"
    )


def test_verify_variant_wrong_type():
    _expect_mismatch("v", "not a variant", match="VARIANT")


def test_verify_none_raises():
    with pytest.raises(SignatureBodyMismatchError, match='Python type "None"'):
        SignatureType("s").verify(None)


def test_verify_token_with_no_validator_raises():
    # SignatureType built directly with a token outside the validators dict
    # (e.g. the closing-paren marker used during parsing) hits the fallback.
    t = SignatureType(")")
    with pytest.raises(Exception, match="cannot verify type with token"):
        t.verify("anything")


# --- SignatureTree.verify error paths ---


@pytest.mark.skipif(
    is_compiled(),
    reason="SignatureTree.verify has a strict list[Any] annotation; Cython enforces it before the isinstance check",
)
def test_tree_verify_body_not_list():
    tree = SignatureTree("s")
    with pytest.raises(SignatureBodyMismatchError, match="must be a list"):
        tree.verify("not a list")


def test_tree_verify_wrong_body_length():
    tree = SignatureTree("ss")
    with pytest.raises(SignatureBodyMismatchError, match="wrong number of types"):
        tree.verify(["only one"])


def test_tree_eq():
    assert SignatureTree("as") == SignatureTree("as")
    assert SignatureTree("as") != SignatureTree("ai")
    assert (SignatureTree("s") == "s") is False


# --- Variant constructor paths ---


def test_variant_from_signature_tree():
    tree = SignatureTree("s")
    v = Variant(tree, "hi")
    assert v.signature == "s"
    assert v.type is tree.types[0]
    assert v.value == "hi"


def test_variant_from_signature_string():
    v = Variant("s", "hi")
    assert v.signature == "s"
    assert v.value == "hi"


def test_variant_invalid_signature_type_raises_typeerror():
    with pytest.raises(TypeError, match="signature must be"):
        Variant(123, "hi")


def test_variant_signature_tree_with_multiple_types_raises():
    tree = SignatureTree("ss")
    with pytest.raises(ValueError, match="single complete type"):
        Variant(tree, "hi")


@pytest.mark.skipif(
    is_compiled(), reason="Variant._factory is a cdef staticmethod when Cython-compiled"
)
def test_variant_factory_skips_verification():
    tree = SignatureTree("s")
    # _factory is the internal fast path used by the unmarshaller; it bypasses
    # verification and is the only way to build a Variant with a mismatched
    # value, so we exercise that explicitly.
    v = Variant._factory(tree, "hi")
    assert v.signature == "s"
    assert v.type is tree.root_type
    assert v.value == "hi"


def test_variant_eq():
    assert Variant("s", "hi") == Variant("s", "hi")
    assert Variant("s", "hi") != Variant("s", "bye")
    assert Variant("s", "hi") != Variant("o", "/hi")
    assert (Variant("s", "hi") == "hi") is False


def test_variant_repr():
    v = Variant("s", "hi")
    text = repr(v)
    assert "Variant" in text
    assert "'s'" in text
    assert "hi" in text


def test_variant_skip_verify_flag():
    # verify=False lets the caller construct an invalid Variant without raising;
    # used as a perf escape hatch by trusted producers.
    v = Variant("s", 123, verify=False)
    assert v.value == 123


def test_verify_raises_internal_error_when_validator_missing(monkeypatch):
    sig_type = SignatureType("i")
    monkeypatch.delitem(SignatureType.validators, "i")
    with pytest.raises(InternalError):
        sig_type.verify(123)


def test_get_signature_tree_cache_is_bounded() -> None:
    """The lru_cache on get_signature_tree must declare a finite maxsize."""
    info = get_signature_tree.cache_info()
    assert info.maxsize is not None
    assert info.maxsize <= 8192


def test_get_signature_tree_cache_evicts_under_unique_stream() -> None:
    """Streaming more unique signatures than maxsize must not grow the cache."""
    info = get_signature_tree.cache_info()
    maxsize = info.maxsize
    assert maxsize is not None

    # Encode the index in 14 bits across two DBus type chars (y, i) so each
    # signature is unique, short, and well under the 255-char signature
    # length cap.
    overflow = maxsize * 2
    width = overflow.bit_length()
    for n in range(overflow):
        sig = f"{n:b}".zfill(width).translate(str.maketrans("01", "yi"))
        get_signature_tree(sig)

    assert get_signature_tree.cache_info().currsize <= maxsize
