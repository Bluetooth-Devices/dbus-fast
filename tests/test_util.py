"""Unit tests for the helpers in ``_private.util``."""

import copy
import inspect
import types
from typing import Annotated

import pytest

from dbus_fast._private.util import (
    parse_annotation,
    replace_fds_with_idx,
    replace_idx_with_fds,
    signature_contains_type,
)
from dbus_fast.annotations import DBusInt32, DBusSignature, DBusStr
from dbus_fast.signature import Variant, get_signature_tree


def _roundtrip(signature, high_body):
    """Convert high->low->high and return (low_body, fds, restored_high).

    Both conversions mutate nested containers in place, so each direction
    runs against an independent deep copy and the low body is snapshotted
    before the restore step rewrites it.
    """
    low_body, fds = replace_fds_with_idx(signature, copy.deepcopy(high_body))
    low_snapshot = copy.deepcopy(low_body)
    restored = replace_idx_with_fds(signature, low_body, fds)
    return low_snapshot, fds, restored


def test_bare_fd_roundtrip():
    low, fds, high = _roundtrip("h", [42])
    assert low == [0]
    assert fds == [42]
    assert high == [42]


def test_array_of_fds_roundtrip():
    low, fds, high = _roundtrip("ah", [[7, 8, 9]])
    assert low == [[0, 1, 2]]
    assert fds == [7, 8, 9]
    assert high == [[7, 8, 9]]


def test_struct_of_fds_roundtrip():
    low, fds, high = _roundtrip("(hh)", [[7, 9]])
    assert low == [[0, 1]]
    assert fds == [7, 9]
    assert high == [[7, 9]]


def test_dict_fd_value_roundtrip():
    low, fds, high = _roundtrip("a{sh}", [{"a": 7, "b": 8}])
    assert low == [{"a": 0, "b": 1}]
    assert fds == [7, 8]
    assert high == [{"a": 7, "b": 8}]


def test_dict_fd_key_roundtrip():
    low, fds, high = _roundtrip("a{hs}", [{7: "x", 8: "y"}])
    assert low == [{0: "x", 1: "y"}]
    assert fds == [7, 8]
    assert high == [{7: "x", 8: "y"}]


def test_dict_nested_fd_in_value_roundtrip():
    low, fds, high = _roundtrip("a{s(h)}", [{"a": [7]}])
    assert low == [{"a": [0]}]
    assert fds == [7]
    assert high == [{"a": [7]}]


def test_variant_carrying_bare_fd_roundtrip():
    low, fds = replace_fds_with_idx("v", [Variant("h", 7)])
    assert low[0].value == 0
    assert fds == [7]
    high = replace_idx_with_fds("v", low, fds)
    assert high[0].value == 7


def test_variant_carrying_array_of_fds_roundtrip():
    low, fds = replace_fds_with_idx("v", [Variant("ah", [7, 8])])
    assert low[0].value == [0, 1]
    assert fds == [7, 8]
    high = replace_idx_with_fds("v", low, fds)
    assert high[0].value == [7, 8]


def test_duplicate_fd_collapses_to_single_index():
    low, fds = replace_fds_with_idx("(hh)", [[7, 7]])
    assert low == [[0, 0]]
    assert fds == [7]


def test_replace_fds_with_idx_no_fd_in_signature_is_noop():
    body = ["hello", 1]
    low, fds = replace_fds_with_idx("si", list(body))
    assert low == body
    assert fds == []


def test_replace_idx_with_fds_empty_unix_fds_returns_body():
    body = [3]
    assert replace_idx_with_fds("h", body, []) is body


def test_replace_idx_with_fds_no_fd_in_signature_is_noop():
    body = ["hello"]
    assert replace_idx_with_fds("s", body, [42]) == ["hello"]


def test_replace_idx_with_fds_out_of_range_index_yields_none():
    # A malformed message can declare an fd index that exceeds the unix_fds
    # array; the missing slot resolves to None rather than raising.
    assert replace_idx_with_fds("h", [5], [42]) == [None]


def test_string_signature_and_tree_signature_agree():
    tree = get_signature_tree("ah")
    low_str, fds_str = replace_fds_with_idx("ah", [[7, 8]])
    low_tree, fds_tree = replace_fds_with_idx(tree, [[7, 8]])
    assert low_str == low_tree
    assert fds_str == fds_tree


def test_signature_contains_type_token_in_tree():
    assert signature_contains_type("h", [], "h") is True
    assert signature_contains_type("(sih)", [], "h") is True


def test_signature_contains_type_token_absent_without_variants():
    # No variant in the signature means the body is never inspected.
    assert signature_contains_type("ai", [1, 2, 3], "h") is False


def test_signature_contains_type_descends_into_variant_body():
    # 'h' is not in the static signature 'v', so the body must be walked to
    # discover the fd hidden inside the variant.
    assert signature_contains_type("v", [Variant("h", 5)], "h") is True


def test_signature_contains_type_descends_into_list_of_variants():
    assert signature_contains_type("av", [[Variant("h", 5)]], "h") is True


def test_signature_contains_type_descends_into_dict_of_variants():
    assert signature_contains_type("a{sv}", [{"k": Variant("h", 5)}], "h") is True


def test_signature_contains_type_variant_without_token_is_false():
    assert signature_contains_type("v", [Variant("s", "x")], "h") is False


def test_signature_contains_type_accepts_signature_tree():
    tree = get_signature_tree("v")
    assert signature_contains_type(tree, [Variant("h", 5)], "h") is True


def _module_with(**names):
    mod = types.ModuleType("fake_annotations_module")
    for key, value in names.items():
        setattr(mod, key, value)
    return mod


def test_parse_annotation_empty_inputs_return_empty_string():
    mod = _module_with()
    assert parse_annotation(None, mod) == ""
    assert parse_annotation(inspect.Signature.empty, mod) == ""


@pytest.mark.parametrize("sig", ["s", "i", "a{sv}", "(ii)", "ah"])
def test_parse_annotation_dbus_signature_string_returned_directly(sig):
    assert parse_annotation(sig, _module_with()) == sig


def test_parse_annotation_quoted_string_literal_is_stripped():
    # ast.literal_eval turns the quoted forward-ref form into the bare code.
    assert parse_annotation("'s'", _module_with()) == "s"


def test_parse_annotation_forward_reference_is_evaluated():
    mod = _module_with(DBusInt32=DBusInt32)
    assert parse_annotation("DBusInt32", mod) == "i"


def test_parse_annotation_annotated_alias_returns_signature():
    mod = _module_with()
    assert parse_annotation(DBusInt32, mod) == "i"
    assert parse_annotation(DBusStr, mod) == "s"


def test_parse_annotation_annotated_without_signature_raises():
    with pytest.raises(ValueError, match="must include a DBusSignature"):
        parse_annotation(Annotated[int, "not a signature"], _module_with())


def test_parse_annotation_unsupported_type_raises():
    with pytest.raises(ValueError, match="must be a string constant"):
        parse_annotation(int, _module_with())


def test_parse_annotation_runtime_signature_annotated_form():
    mod = _module_with()
    assert parse_annotation(Annotated[int, DBusSignature("u")], mod) == "u"
