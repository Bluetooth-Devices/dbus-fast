"""Spawn a temporary dbus-daemon for the test session.

On Linux CI the suite is launched under ``dbus-run-session`` so
``DBUS_SESSION_BUS_ADDRESS`` is already set; this fixture is a no-op there.

On macOS (and any other host without a session bus), if ``dbus-daemon`` is
available on ``PATH`` we start one against a temporary unix socket so the
integration tests can connect to a real bus locally.

If ``dbus-daemon`` is not available we yield without setting anything;
integration tests will fail with ``InvalidAddressError`` exactly as they did
before this fixture existed.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest

try:
    from blockbuster import BlockBuster, blockbuster_ctx
except ImportError:  # s390x leg skips installing blockbuster under QEMU
    BlockBuster = None  # type: ignore[assignment,misc]
    blockbuster_ctx = None  # type: ignore[assignment]

from dbus_fast._private.unmarshaller import is_compiled

# blockbuster monkey-patches threading.Lock.acquire and walks the frame
# stack via inspect.getframeinfo. Coverage's CTracer takes that lock on
# every traced line, and walking a frame whose code object belongs to a
# Cython extension has segfaulted in CI. The SKIP_CYTHON matrix leg
# still exercises blockbuster, so blocking-call detection is preserved.
_RUNNING_COMPILED = is_compiled()

# The same frame walk has segfaulted intermittently on Python 3.10 and
# 3.11 even on the skip_cython leg; restrict blockbuster to 3.12+ where
# the frame APIs are stable enough for it to coexist with coverage.
_PY_SUPPORTS_BLOCKBUSTER = sys.version_info >= (3, 12)

_BENCHMARKS_DIR = "tests/benchmarks"

# Tests that perform sync IO inside the asyncio event loop and trip
# blockbuster. Marked xfail so CI is green; pop entries as they get
# fixed so the underlying blocking call is gone for good.
_KNOWN_BLOCKING: frozenset[str] = frozenset()


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Mark known-blocking tests xfail so CI is green while we work through them."""
    if blockbuster_ctx is None or not _PY_SUPPORTS_BLOCKBUSTER:
        return
    marker = pytest.mark.xfail(
        reason="blockbuster: blocking call in asyncio path, to be fixed",
        strict=False,
    )
    for item in items:
        if item.nodeid in _KNOWN_BLOCKING:
            item.add_marker(marker)


@pytest.fixture(autouse=True)
def blockbuster(
    request: pytest.FixtureRequest,
) -> Iterator[BlockBuster | None]:
    """Fail any test that performs a blocking call inside the asyncio loop."""
    if (
        blockbuster_ctx is None
        or _RUNNING_COMPILED
        or not _PY_SUPPORTS_BLOCKBUSTER
        or _BENCHMARKS_DIR in str(request.node.fspath)
    ):
        yield None
        return
    with blockbuster_ctx() as bb:
        yield bb


_SESSION_CONF = """<!DOCTYPE busconfig PUBLIC "-//freedesktop//DTD D-Bus Bus Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">
<busconfig>
  <type>session</type>
  <keep_umask/>
  <listen>unix:tmpdir={tmpdir}</listen>
  <auth>EXTERNAL</auth>
  <policy context="default">
    <allow send_destination="*" eavesdrop="true"/>
    <allow eavesdrop="true"/>
    <allow own="*"/>
  </policy>
</busconfig>
"""


@pytest.fixture(scope="session", autouse=True)
def _dbus_session_bus() -> Iterator[None]:
    if os.environ.get("DBUS_SESSION_BUS_ADDRESS"):
        yield
        return

    dbus_daemon = shutil.which("dbus-daemon")
    if dbus_daemon is None:
        yield
        return

    with tempfile.TemporaryDirectory(prefix="dbus-fast-test-") as tmp:
        conf_path = Path(tmp) / "session.conf"
        conf_path.write_text(_SESSION_CONF.format(tmpdir=tmp))

        with subprocess.Popen(  # noqa: S603
            [
                dbus_daemon,
                "--config-file",
                str(conf_path),
                "--print-address",
                "--nofork",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ) as proc:
            try:
                assert proc.stdout is not None
                address = proc.stdout.readline().strip()
                if not address:
                    stderr = proc.stderr.read() if proc.stderr else ""
                    raise RuntimeError(
                        f"dbus-daemon did not print an address. stderr: {stderr!r}"
                    )

                os.environ["DBUS_SESSION_BUS_ADDRESS"] = address
                try:
                    yield
                finally:
                    os.environ.pop("DBUS_SESSION_BUS_ADDRESS", None)
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
