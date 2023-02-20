"""Build optional cython modules."""

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
    try:
        from Cython.Build import cythonize

        setup_kwargs.update(
            dict(
                ext_modules=cythonize(
                    [
                        "src/dbus_fast/aio/message_reader.py",
                        "src/dbus_fast/message.py",
                        "src/dbus_fast/message_bus.py",
                        "src/dbus_fast/service.py",
                        "src/dbus_fast/signature.py",
                        "src/dbus_fast/unpack.py",
                        "src/dbus_fast/_private/marshaller.py",
                        "src/dbus_fast/_private/unmarshaller.py",
                    ],
                    compiler_directives={"language_level": "3"},  # Python 3
                ),
                cmdclass=dict(build_ext=BuildExt),
            )
        )
    except Exception:
        if os.environ.get("REQUIRE_CYTHON"):
            raise
        pass
