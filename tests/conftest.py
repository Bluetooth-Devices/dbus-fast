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
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest

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
