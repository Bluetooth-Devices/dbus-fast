from typing import Any

from .signature import Variant


def unpack_variants(data: Any) -> Any:
    """Unpack variants and remove signature info."""
    return _unpack_variants(data)


def _unpack_variants(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: _unpack_variants(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_unpack_variants(item) for item in data]
    if isinstance(data, Variant):
        return _unpack_variants(data.value)
    return data
