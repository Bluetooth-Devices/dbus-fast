# Installation

The package is published on [PyPI](https://pypi.org/project/dbus-fast/) and can be installed with `pip` (or any equivalent):

```bash
pip install dbus-fast
```

## Installing without the Cython extension

`dbus-fast` ships an optional Cython extension that accelerates the
marshalling/unmarshalling hot paths. The wheels on PyPI bundle the compiled
extension, which adds a few MB to the installed footprint of an application.

If you don't need the extra performance — for example, when bundling
`dbus-fast` into a size-sensitive application — you can install the pure-Python
version by setting `SKIP_CYTHON=1` when building from a source distribution:

```bash
SKIP_CYTHON=1 pip install --no-binary dbus-fast dbus-fast
```

The `--no-binary dbus-fast` flag forces `pip` to build from the source
distribution (skipping the prebuilt wheel), and `SKIP_CYTHON=1` tells the build
to skip the Cython extension entirely. The result is the same library, only
slower on the marshalling hot paths.

Conversely, set `REQUIRE_CYTHON=1` to make the build fail loudly if the Cython
extension cannot be produced — useful when packaging wheels in CI.
