"""Unit tests for the high/low-level fd body conversion in ``_private.util``."""

import copy

from dbus_fast._private.util import replace_fds_with_idx, replace_idx_with_fds
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
