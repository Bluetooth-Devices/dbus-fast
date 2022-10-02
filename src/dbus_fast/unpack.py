from typing import Any

from .signature import Variant


def unpack_variants(data: Any) -> Any:
    """Unpack variants and remove signature info."""
    if isinstance(data, Variant):
        return unpack_variants(data.value)
    if isinstance(data, dict):
        return {k: unpack_variants(v) for k, v in data.items()}
    if isinstance(data, list):
        return [unpack_variants(item) for item in data]
    return data
