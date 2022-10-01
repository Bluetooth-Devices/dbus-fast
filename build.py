"""Build optional cython modules."""

import contextlib
import os
from distutils.command.build_ext import build_ext


class BuildExt(build_ext):
    def build_extensions(self):
        try:
            super().build_extensions()
        except Exception:
            pass


def build(setup_kwargs):
    if os.environ.get("SKIP_CYTHON", False):
        return
    with contextlib.suppress(Exception):
        from Cython.Build import cythonize

        setup_kwargs.update(
            dict(
                ext_modules=cythonize(
                    [
                        "src/dbus_fast/_private/marshaller.py",
                        "src/dbus_fast/_private/unmarshaller.py",
                    ]
                ),
                cmdclass=dict(build_ext=BuildExt),
            )
        )
