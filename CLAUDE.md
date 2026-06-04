# Notes for LLM contributors

A short orientation file for an LLM working in this repo. Skim
before making changes; keep edits consistent with what's described
here. Read [README.md](README.md) for the user-facing intro and
[CONTRIBUTING.md](CONTRIBUTING.md) for the human contributor flow.

## What this project is

`dbus-fast` is a Python client/server library for
[D-Bus](https://dbus.freedesktop.org/), targeting Linux desktop and
mobile environments. It's a performance-focused fork of
[`python-dbus-next`](https://github.com/altdesktop/python-dbus-next)
and powers D-Bus-side integrations in
[Home Assistant](https://www.home-assistant.io/) and the
[bluetooth-devices](https://github.com/bluetooth-devices/) ecosystem
(BlueZ, BleakDBus, etc.).

Two IO backends are shipped from the same wire-level core:

- `dbus_fast.aio` — asyncio (`MessageBus`, `MessageReader`,
  `ProxyObject`). What most callers use.
- `dbus_fast.glib` — GLib main-loop bindings, for GTK/GObject
  callers.

Hot paths are Cythonized at build time for throughput. They keep
working as pure Python — `SKIP_CYTHON=1` disables the extension
build — but production wheels ship compiled and CodSpeed
benchmarks track that path. See _Build conventions_ below.

## Code style

- **Docstrings: terse, default to single-line.** A docstring is
  the function's _contract_, not its narrative. Almost every
  docstring should be one line — `"""Summary."""` — describing
  what the function does and what the caller can pass. Multi-line
  is the exception, only justified when there is non-obvious
  caller-visible behaviour the type signature and parameter names
  don't already convey.

  **What does NOT belong in docstrings or comments:**
  - Rationale / motivation / "why we used to do X" — that's the
    PR description and the commit message. Git already remembers.
  - Cross-references to issue numbers ("closes #N", "follow-up
    to #M") — the PR body carries those.
  - Restatement of the function body in prose. If the next line
    of the docstring is just describing what the next line of
    code does, delete the docstring line.
  - Test docstrings retelling the production-side story. A test
    docstring should name what the test pins, in one sentence —
    not re-explain the bug, the fix, or the surrounding flow.

- **Comments**: same bar. Default to writing no comments. Add
  one only when the _why_ is non-obvious: a hidden constraint, a
  subtle invariant, a workaround for a specific bug, behaviour
  that would surprise a reader. If removing the comment wouldn't
  confuse a future reader, don't write it.

  **Don't remove existing comments** unless the code they
  describe is gone — the original author left them for a reason.
  Comments around Cython-specific patterns (`if cython.compiled:`,
  branch hints, manual inlines) frequently exist _because_
  removing them regressed a benchmark or broke the C build.

- **Don't pad commits, docstrings, or comments with cross-
  references** to old codepaths or issue numbers unless there's
  a clear reason a future reader needs that link.

- **D-Bus type annotations: no signature strings.** Since v4.0.0
  the supported form is the `Annotated` aliases in
  `dbus_fast.annotations` (`DBusInt32`, `DBusUInt16`, `DBusStr`,
  …) or `Annotated[..., DBusSignature(sig)]` for a runtime
  signature. The old string form (`def m(self) -> "i":`) is
  deprecated. No runtime `DeprecationWarning` is emitted, so
  review feedback is the only signal — don't reintroduce it in
  code or docs.

- **Method order**: public API at the top, private helpers
  (`_underscore_prefixed`) at the bottom.

- **Line length**: 88 (ruff default with overrides — see
  `pyproject.toml`). `python_requires = ">=3.10"`,
  `target-version = "py310"` for ruff and `--py310-plus` for
  pyupgrade. Don't introduce 3.11+-only syntax.

- **Imports**: ruff/isort sorted (`profile = "black"`,
  `known_first_party = ["dbus_fast", "tests"]`). Prefer absolute
  imports rooted at `dbus_fast.*`.

- **Generated artefacts are not checked in to source paths.**
  Cython produces `*.c`, `*.html`, and `*.so` siblings of each
  `.py` listed in `TO_CYTHONIZE`; `*.c` is excluded from the
  wheel via `pyproject.toml`'s `exclude` list and `*.html` /
  `*.so` are build outputs — don't commit them.

## Commit / PR conventions

- **Conventional Commits, lowercase subject.** Repo is squash-
  merge only with `squash_merge_commit_title = PR_TITLE`, so the
  PR title — not the individual branch commits — becomes the
  subject of the commit that lands on `main`. The
  `pr-title.yml` workflow runs
  `amannn/action-semantic-pull-request` against the title; the
  `commitizen` pre-commit hook gives local feedback on per-commit
  subjects but CI no longer re-checks them, because the squash
  discards them anyway. Accepted types: `build`, `chore`, `ci`,
  `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`,
  `test`. Scopes are optional. The subject (text after
  `type(scope):`) must start lowercase. Examples that pass:
  - `feat: add async context manager to MessageBus`
  - `fix(unmarshaller): handle empty arrays at end of frame`
  - `perf!: drop python 3.9 support`
- **Releases are commit-driven.** `python-semantic-release` reads
  the commit log on `main` to decide the next version and write
  `CHANGELOG.md`. `feat:` → minor bump, `fix:`/`perf:` → patch
  bump, anything with `!` or a `BREAKING CHANGE:` footer →
  major. `chore:`, `docs:`, `test:`, `ci:`, `style:`, `build:`,
  `refactor:` don't bump on their own. Pick the type that
  reflects the actual user-visible effect — the changelog reader
  is downstream.
- **PR title becomes the squash subject.** GitHub uses the PR
  title as the commit subject for "Squash and merge", and the
  `pr-title.yml` workflow is the gate on it. Title length isn't
  capped by the workflow (`header-max-length` isn't enforced),
  but keep it readable — under ~70 chars for the GitHub PR list,
  the body carries the detail.
- **No `Co-Authored-By` trailers for LLM authorship.** Project
  preference: commits attribute the human who reviewed the
  change, not the tool that produced the draft.
- **No PR template.** The repo doesn't ship a
  `.github/PULL_REQUEST_TEMPLATE.md`, so the body is freeform —
  describe what the change does and why, link the issue if one
  exists. The `pr-workflow` skill (under
  `.claude/skills/pr-workflow/`) summarises this end-to-end.
- **Pre-commit auto-fixes; re-stage.** `ruff --fix`, `ruff
format`, `pyupgrade --py310-plus`, and the
  `pre-commit-hooks` set (trailing-whitespace, end-of-file-fixer,
  etc.) run on commit and will modify files in place. When a hook
  rewrites a file, the commit aborts — re-stage the auto-fixed
  files and commit again.

## Running tests

The full suite needs a session bus, so run it under
`dbus-run-session`:

```bash
poetry install
dbus-run-session -- poetry run pytest --timeout=5
```

CI runs the matrix across Python 3.10–3.14 plus `3.14t` (free-
threaded), each in both `SKIP_CYTHON=1` and `REQUIRE_CYTHON=1`
modes, on `ubuntu-latest`, with an additional `s390x` big-endian
run via `uraimo/run-on-arch-action`. Tests must pass on every
cell of that matrix; in particular, endian-sensitive code in the
marshaller/unmarshaller is covered by the s390x leg.

CodSpeed benchmarks live under `tests/benchmarks/` and
`bench/` and run in CI on a separate path
(`pytest-codspeed`). Don't regress them on the marshalling /
unmarshalling hot paths without a deliberate trade-off in the PR
body.

## Build conventions

- **Cython is optional but expected in wheels.** `build_ext.py`
  cythonizes the modules listed in `TO_CYTHONIZE`
  (`message.py`, `message_bus.py`, `service.py`, `signature.py`,
  `unpack.py`, `_private/address.py`, `_private/marshaller.py`,
  `_private/unmarshaller.py`, `aio/message_reader.py`). The
  custom `BuildExt` swallows build failures so source installs
  fall back to pure Python; CI wheel builds set
  `REQUIRE_CYTHON=1` to make the build fail loudly if the
  extension can't be produced. `SKIP_CYTHON=1` disables the
  Cython step entirely (used by the pure-Python CI leg).
- **`.pxd` discipline.** Modules that get Cythonized ship a
  sibling `.pxd` for type declarations
  (`message.pxd`, `message_bus.pxd`, `_private/unmarshaller.pxd`,
  etc.). When changing the signature of a Cythonized function or
  the layout of a Cythonized class, update the `.pxd` in the
  same commit, or the extension build will pick up a stale
  declaration and either fail to compile or — worse — silently
  fall back to the slower Python path.
- **`language_level = "3"`.** Set in `build_ext.py`'s `cythonize`
  call. Don't introduce Python-2-compatible syntax.
- **Free-threaded build target.** The matrix includes `3.14t`
  (PEP 703). Anything added to `TO_CYTHONIZE` must stay free-
  threading-safe — no module-level mutable globals, no
  C-level shared state without a lock.
- **`cython.compiled` guards.** Code that needs to differ
  between the compiled and pure-Python paths uses
  `if cython.compiled:` (see `_private/_cython_compat.py`).
  The coverage config excludes those branches
  (`exclude_also = ["if cython.compiled:"]`) — don't count their
  absence in coverage as a missing test.

## Cython gotchas (things that have bitten us)

These are non-obvious traps in the `.py` + `.pxd` setup that work
fine in pure-Python mode but break or silently misbehave in the
shipped Cython wheels. The `SKIP_CYTHON=1` leg of CI is happy to
sail past most of them — the `REQUIRE_CYTHON=1` leg, the s390x
leg, or CodSpeed catch what's left, but only if you read the
matrix carefully. Several were hit on the marshaller /
unmarshaller hot paths.

- **`cdef`-typed module constants are not Python-importable.**
  Declaring `cdef unsigned int _MAX_X` in `.pxd` makes Cython
  treat `_MAX_X = 5` in the `.py` as a C int assignment; the
  Python module dict never gets the binding. `from module import
_MAX_X` succeeds in pure-Python but raises `ImportError` under
  Cython. Pattern — define both names, the un-prefixed one for
  Python (tests, cross-module) and the underscored one for the
  cdef hot path:

  ```python
  # in .py
  MAX_MESSAGE_SIZE = 134_217_728      # Python-importable
  _MAX_MESSAGE_SIZE = MAX_MESSAGE_SIZE  # cdef'd C int alias
  ```

  ```cython
  # in .pxd
  cdef unsigned int _MAX_MESSAGE_SIZE
  ```

  This was the trap hit on the `_read_header` size-cap fix
  (`src/dbus_fast/_private/unmarshaller.py`). See PR
  [esphome/aioesphomeapi#1651][aio-1651] for the related
  upstream lesson.

- **`unsigned int` returned through `cdef int` can flip sign.**
  A wire field decoded into `unsigned int` and returned via
  `cdef int` will come back negative for any value with bit 31
  set. If the caller does `if x < 0: return`, an attacker-
  controlled large value silently hits the early-return branch
  instead of being rejected. Either cap the input range so
  decoded values stay in signed-int range, or check explicit
  sentinel values (`x == _SENTINEL_INCOMPLETE`) instead of
  generic `< 0`. The marshaller/unmarshaller deal with `uint32`
  body lengths and field sizes that routinely have bit 31 set,
  so this is a live class-of-bug for any new cdef int returns.

- **Sign-compare warnings in generated C are real.** `clang`/`gcc`
  warns when an `unsigned int` is compared with `int` because
  the signed value is implicitly converted to unsigned for the
  compare — a negative value becomes a huge positive. Match
  signedness in the `.pxd` (if the local is `unsigned int`,
  declare the constant `cdef unsigned int`; if the local is
  `int`, declare `cdef int`). Don't dismiss the warning as
  cosmetic — it predicts the unsigned-vs-signed sentinel-bypass
  class of bug above.

- **`noexcept` cdef paths must be pure C.** Calling a Python
  method that can raise from inside a `cdef ... noexcept`
  function is undefined / lossy — Cython prints the exception
  via `WriteUnraisable` and silently continues. Keep `noexcept`
  paths to sentinel returns and let the caller (or a separate
  `except *` wrapper) handle Python-level work. The
  `_ustr_uint32` family in `_private/unmarshaller.pxd` is the
  template — pure C, no Python calls.

- **`except *` adds a `PyErr_Occurred()` check after every
  call.** Switching a hot-path `cdef ... noexcept` to `except *`
  inserts a per-call exception check in the generated C. Cold
  paths don't care; the marshalling/unmarshalling hot path
  does. CodSpeed will catch a regression but only if the
  change is on a path the benchmarks exercise — when adding
  `except *` to anything in `_private/marshaller.pxd` or
  `_private/unmarshaller.pxd`, check the CodSpeed delta on the
  PR and justify if it moved.

- **Module-level Python int constants force `PyLong_AsLong`
  per access.** A bare `MAX_X = 5` in the `.py` (without a
  matching `cdef int MAX_X` in the `.pxd`) compiles to a Python
  attribute lookup and `PyLong_AsLong` on every comparison —
  fine for the once-per-message validation path, expensive
  inside the per-field marshalling loop. For constants used
  inside the unmarshaller's per-token loops, declare the
  underscored alias in the `.pxd` as `cdef unsigned int` (see
  the dual-name pattern above).

- **CodSpeed regressions only show on the Cython build.** Pure-
  Python (`SKIP_CYTHON=1`) tests can pass while the production
  wire-format hot paths regress. Trust the CodSpeed check on
  PRs that touch `TO_CYTHONIZE` files; before pushing perf-
  sensitive changes, run
  `REQUIRE_CYTHON=1 python setup.py build_ext --inplace` and
  `pytest tests/benchmarks/` locally.

[aio-1651]: https://github.com/esphome/aioesphomeapi/pull/1651

## Reporting security issues

Suspected security vulnerabilities go through GitHub's [private
vulnerability reporting][gh-report], not public issues or pull
requests. The policy is spelled out in [SECURITY.md](SECURITY.md).
If a user describes what sounds like a vulnerability in chat,
point them at that route instead of opening a public issue, PR,
or commit that names the bug class and the affected code path.

[gh-report]: https://github.com/Bluetooth-Devices/dbus-fast/security/advisories/new

## Useful entry points

| Path                                     | What                                                             |
| ---------------------------------------- | ---------------------------------------------------------------- |
| `src/dbus_fast/aio/message_bus.py`       | High-level asyncio `MessageBus` — what most callers use          |
| `src/dbus_fast/aio/message_reader.py`    | asyncio frame reader (Cythonized)                                |
| `src/dbus_fast/aio/proxy_object.py`      | asyncio `ProxyObject` / `ProxyInterface`                         |
| `src/dbus_fast/glib/`                    | GLib main-loop backend (`MessageBus`, `ProxyObject`)             |
| `src/dbus_fast/message_bus.py`           | Wire-level `BaseMessageBus` shared by both backends (Cythonized) |
| `src/dbus_fast/message.py`               | `Message` dataclass and serialisation entry point (Cythonized)   |
| `src/dbus_fast/service.py`               | Service-side decorators and method dispatch (Cythonized)         |
| `src/dbus_fast/signature.py`             | `SignatureTree`, `SignatureType`, `Variant` (Cythonized)         |
| `src/dbus_fast/unpack.py`                | `unpack_variants` — fast variant flattening (Cythonized)         |
| `src/dbus_fast/_private/marshaller.py`   | Outgoing wire encoder (Cythonized)                               |
| `src/dbus_fast/_private/unmarshaller.py` | Incoming wire decoder (Cythonized; endian-sensitive)             |
| `src/dbus_fast/_private/address.py`      | Bus address parser (Cythonized)                                  |
| `src/dbus_fast/auth.py`                  | EXTERNAL / ANONYMOUS SASL handshake                              |
| `src/dbus_fast/errors.py`                | Exception hierarchy rooted at `DBusFastError`                    |
| `src/dbus_fast/constants.py`             | `BusType`, `MessageType`, `MessageFlag`, etc.                    |
| `src/dbus_fast/validators.py`            | Bus / interface / member / object-path validators                |
| `src/dbus_fast/introspection.py`         | XML introspection parser/emitter                                 |
| `tests/`                                 | Pytest suite — run under `dbus-run-session`                      |
| `tests/benchmarks/`, `bench/`            | CodSpeed benchmarks                                              |
| `build_ext.py`                           | Cython build step + `TO_CYTHONIZE` list                          |

## Things not to do

- **Don't introduce 3.11+-only syntax** — the package supports
  3.10+ and pyupgrade is pinned to `--py310-plus`.
- **Don't change a Cythonized module's public signature
  without updating its `.pxd`** — the extension will silently
  pick up a stale declaration or fall back to pure Python.
- **Don't commit Cython build outputs** (`*.c`, `*.html`, `*.so`)
  into the source tree as part of an unrelated change. They're
  regenerated by `build_ext.py`.
- **Don't pick a Conventional Commit type that under- or over-
  states the release impact.** `chore:` for a user-visible
  bugfix hides it from the changelog; `feat!:` for an internal
  refactor mints a fake major release.
- **Don't add `Co-Authored-By` trailers for LLM tools.** Project
  preference — see _Commit / PR conventions_ above.
- **Don't bypass `BuildExt`'s exception swallowing in
  `build_ext.py` without thought.** The pure-Python fallback is
  a feature for source installs on platforms without a compiler.
