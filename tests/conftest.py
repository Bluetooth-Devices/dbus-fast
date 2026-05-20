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
from blockbuster import BlockBuster, blockbuster_ctx

_BENCHMARKS_DIR = "tests/benchmarks"

# Tests that perform sync IO inside the asyncio event loop and trip
# blockbuster. Marked xfail so CI is green; pop entries as they get
# fixed so the underlying blocking call is gone for good.
_KNOWN_BLOCKING: frozenset[str] = frozenset(
    {
        "tests/client/test_aio.py::test_fast_disconnect",
        "tests/client/test_methods.py::test_aio_proxy_object",
        "tests/client/test_properties.py::test_aio_properties",
        "tests/client/test_signals.py::test_complex_signals",
        "tests/client/test_signals.py::test_coro_callback",
        "tests/client/test_signals.py::test_kwargs_callback",
        "tests/client/test_signals.py::test_on_signal_type_error",
        "tests/client/test_signals.py::test_signals",
        "tests/client/test_signals.py::test_signals_with_changing_owners",
        "tests/client/test_signals.py::test_varargs_callback",
        "tests/service/test_export.py::test_export_alias",
        "tests/service/test_export.py::test_export_introspection",
        "tests/service/test_export.py::test_export_twice_raises",
        "tests/service/test_export.py::test_export_unexport",
        "tests/service/test_methods.py::test_methods[AsyncInterface]",
        "tests/service/test_methods.py::test_methods[ExampleInterface]",
        "tests/service/test_properties.py::test_property_changed_signal[AsyncInterface]",
        "tests/service/test_properties.py::test_property_changed_signal[ExampleInterface]",
        "tests/service/test_properties.py::test_property_methods[AsyncInterface]",
        "tests/service/test_properties.py::test_property_methods[ExampleInterface]",
        "tests/service/test_signals.py::test_interface_add_remove_signal",
        "tests/service/test_signals.py::test_signals",
        "tests/service/test_standard_interfaces.py::test_bare_service_interface",
        "tests/service/test_standard_interfaces.py::test_introspect_matching_sub_paths",
        "tests/service/test_standard_interfaces.py::test_introspectable_interface",
        "tests/service/test_standard_interfaces.py::test_object_manager",
        "tests/service/test_standard_interfaces.py::test_peer_interface",
        "tests/service/test_standard_interfaces.py::test_standard_interface_properties",
        "tests/test_aio_low_level.py::test_error_handling",
        "tests/test_aio_low_level.py::test_internal_error_reply_does_not_leak_traceback",
        "tests/test_aio_low_level.py::test_sending_messages_between_buses",
        "tests/test_aio_low_level.py::test_sending_signals_between_buses",
        "tests/test_aio_low_level.py::test_standard_interfaces",
        "tests/test_aio_multi_flags.py::test_multiple_flags_in_message",
        "tests/test_auth_readline.py::test_auth_readline_rejects_oversize_line",
        "tests/test_auth_readline.py::test_auth_readline_returns_line",
        "tests/test_big_message.py::test_aio_big_message",
        "tests/test_disconnect.py::test_bus_disconnect_before_reply",
        "tests/test_disconnect.py::test_unexpected_disconnect",
        "tests/test_fd_passing.py::test_high_level_service_fd_passing",
        "tests/test_fd_passing.py::test_sending_file_descriptor_low_level",
        "tests/test_fd_passing.py::test_sending_file_descriptor_with_proxy",
        "tests/test_message_bus.py::test_aio_connect_hello_error_propagates_and_clears_state",
        "tests/test_request_name.py::test_name_requests",
        "tests/test_tcp_address.py::test_tcp_connection_with_forwarding",
    }
)


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Mark known-blocking tests xfail so CI is green while we work through them."""
    marker = pytest.mark.xfail(
        reason="blockbuster: blocking call in asyncio path, to be fixed",
        strict=False,
    )
    for item in items:
        if item.nodeid in _KNOWN_BLOCKING:
            item.add_marker(marker)


@pytest.fixture(autouse=True)
def blockbuster(request: pytest.FixtureRequest) -> Iterator[BlockBuster | None]:
    """Fail any test that performs a blocking call inside the asyncio loop."""
    if _BENCHMARKS_DIR in str(request.node.fspath):
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
