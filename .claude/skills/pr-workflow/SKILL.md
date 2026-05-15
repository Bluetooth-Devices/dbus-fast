---
name: pr-workflow
description: Create pull requests for bluetooth-devices/dbus-fast. Use when creating PRs, submitting changes, or preparing contributions.
allowed-tools: Read, Bash, Glob, Grep
---

# dbus-fast PR Workflow

When creating a pull request for `bluetooth-devices/dbus-fast`,
follow these steps. Repo-wide conventions live in
[CLAUDE.md](../../../CLAUDE.md); this skill summarises the parts
that matter at PR-creation time.

## 1. Create branch from origin/main

`origin` points at `bluetooth-devices/dbus-fast`; there is no fork
in this workflow. Always re-fetch first so the branch is based on
the latest `main`:

```bash
git fetch origin
git checkout -b <branch-name> origin/main
```

## 2. Conventional Commits — for both commit subjects AND PR title

Every commit subject and the PR title MUST follow
[Conventional Commits](https://www.conventionalcommits.org/). Two
separate CI gates check this:

- **`commitlint`** (`ci.yml`) — runs
  `@commitlint/config-conventional` over every commit on the
  branch.
- **`pr-title.yml`** — runs
  `amannn/action-semantic-pull-request` over the PR title (which
  GitHub uses as the squash-merge subject).

Accepted types: `build`, `chore`, `ci`, `docs`, `feat`, `fix`,
`perf`, `refactor`, `revert`, `style`, `test`. Scope is optional.
The subject (text after `type(scope):`) must start lowercase.
Examples that pass both gates:

```
feat: add async context manager to MessageBus
fix(unmarshaller): handle empty arrays at end of frame
perf!: drop python 3.9 support
```

### Pick the type that matches the release impact

`python-semantic-release` reads the commit log on `main` to decide
the next version and write `CHANGELOG.md`:

| Type                                                               | Release effect                                  |
| ------------------------------------------------------------------ | ----------------------------------------------- |
| `feat:`                                                            | minor bump, shows in changelog under Features   |
| `fix:`, `perf:`                                                    | patch bump, shows under Bug Fixes / Performance |
| any with `!` or `BREAKING CHANGE:` footer                          | major bump                                      |
| `chore:`, `docs:`, `test:`, `ci:`, `style:`, `build:`, `refactor:` | no bump                                         |

A user-visible bugfix tagged `chore:` will be silently omitted
from the changelog; an internal refactor tagged `feat!:` will
mint a fake major release. Pick the type a changelog reader would
expect.

## 3. There is no PR template

The repo does not ship a `.github/PULL_REQUEST_TEMPLATE.md`, so
the PR body is freeform. Write a short description of:

- **What** the change does (one or two sentences of prose).
- **Why** — the motivating bug, benchmark, or feature ask.
- **Linked issues** — `fixes #N` / `closes #N` for issue
  closure, or a bare reference if the change is related but
  doesn't close.

Keep it focused; the commit messages carry the per-commit detail.

## 4. Commit hygiene

- **Imperative-mood subject line** — "Add X", not "Added X".
- **No `Co-Authored-By` trailers for LLM tools.** Project
  preference — commits attribute the human who reviewed the
  change.
- Let pre-commit run (ruff lint + format, pyupgrade,
  trailing-whitespace, etc.). If a hook auto-fixes a file, the
  commit aborts — re-stage the auto-fixed files and re-commit.
- Write tests for behavioural changes (under `tests/`). Run them
  under `dbus-run-session` since the suite needs a session bus:

  ```bash
  dbus-run-session -- poetry run pytest --timeout=5
  ```

## 5. Push and create the PR

```bash
git push -u origin <branch-name>
gh pr create --repo bluetooth-devices/dbus-fast --base main \
  --title "type(scope): lowercase subject under ~70 chars" \
  --body-file /tmp/pr-body.md
```

Use `--body-file` rather than `--body "..."` so that backticks,
asterisks, and other Markdown in the body are passed through
verbatim instead of being mangled by shell quoting.

The PR title is independently linted by `pr-title.yml` — if it
fails the Conventional Commits check, the workflow blocks merge
until the title is fixed. Fix it in the GitHub UI (or with
`gh pr edit --title`); no push is needed.

## 6. After the PR is open

CI runs:

- `lint` — pre-commit (ruff lint + format, pyupgrade,
  trailing-whitespace).
- `commitlint` — per-commit Conventional Commits check.
- `pr-title` — PR-title Conventional Commits check.
- `test` matrix — Python 3.10–3.14 + `3.14t`, each in both
  `SKIP_CYTHON=1` and `REQUIRE_CYTHON=1` modes.
- `test_big_endian` — s390x via `uraimo/run-on-arch-action`,
  catches endian regressions in the marshaller/unmarshaller.
- `benchmark` — CodSpeed run for the hot paths.

A red `test_big_endian` job almost always means a byte-order
assumption leaked into the marshaller/unmarshaller — re-check
any `struct` format strings and endian conversions in
`src/dbus_fast/_private/`. A CodSpeed regression on a Cythonized
path is worth investigating before merge; if the regression is
intentional, call it out in the PR body so reviewers don't have
to guess.
