# Security Policy

## Reporting a vulnerability

Please report security vulnerabilities privately through GitHub's
[private vulnerability reporting][gh-report] for this repository.
That route sends the report directly to the maintainers and lets
us coordinate a fix, a CVE, and a release before public
disclosure.

**Do not** open a regular GitHub issue, a pull request, or post
to a public channel (mailing list, chat room, Stack Overflow,
etc.) for a suspected vulnerability. If you are unsure whether
something is a vulnerability, use the private report — we would
rather see a false alarm than a public one.

We aim to acknowledge new reports within a few business days.

[gh-report]: https://github.com/Bluetooth-Devices/dbus-fast/security/advisories/new

## Supported versions

Security fixes are released against the latest `4.x` line on
PyPI. Older releases are not maintained — please upgrade to the
current release before reporting, and confirm the issue still
reproduces there.

## Scope

`dbus-fast` is a D-Bus client/server library. By design it
exchanges wire-format frames with a `dbus-daemon` over a Unix
socket, so any process the daemon has admitted to the bus can
deliver bytes to the parsing code. In-scope issues include:

- Memory-safety, parsing, or denial-of-service issues triggered
  by crafted D-Bus messages or type signatures reaching the
  unmarshaller (`_private/unmarshaller.py`), the marshaller
  (`_private/marshaller.py`), the signature parser
  (`signature.py`), or the address parser (`_private/address.py`).
- Authentication-handshake flaws in `auth.py` (SASL EXTERNAL /
  ANONYMOUS / DBUS_COOKIE_SHA1) that let a peer connect, escalate,
  or impersonate beyond what the bus policy permits.
- Logic bugs in `message_bus.py` / `aio/message_bus.py` /
  `service.py` that cause the library to dispatch, expose, or
  reply to a method or signal it should not — including bypasses
  of the matching/registration rules a caller relied on.
- Issues in the build / packaging pipeline (`build_ext.py`,
  Cython output in `TO_CYTHONIZE`, wheel contents, signed-release
  flow) that could lead to a compromised wheel on PyPI.

Out of scope:

- Risks inherent to running on a shared D-Bus instance — D-Bus
  access control is enforced by `dbus-daemon`'s own policy files,
  not by this library. Reports of the form "a co-resident
  process the daemon admitted can call my exported method" are
  expected behaviour unless they cross one of the lines above.
- Running `dbus-daemon` over an unauthenticated TCP transport,
  or other deployment-side misconfiguration of the bus.
- Misuse of the API by a consuming application (e.g. exporting a
  privileged method without any caller check) — that is the
  consumer's policy decision, not a library bug.
