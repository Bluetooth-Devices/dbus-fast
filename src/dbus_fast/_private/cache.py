def bounded_put(cache: dict, key: object, value: object, maximum: int) -> None:
    """Insert into a FIFO cache bounded at ``maximum``, evicting the oldest entry."""
    # Other threads may evict or insert concurrently: a lost race must not
    # raise, and evicting until below the bound keeps the size from drifting.
    while len(cache) >= maximum:
        try:
            cache.pop(next(iter(cache)), None)
        except (RuntimeError, StopIteration):
            break
    cache[key] = value
