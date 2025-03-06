# CHANGELOG


## v2.37.0 (2025-03-06)

### Features

- Add support for finding message handlers when interface is None
  ([#403](https://github.com/Bluetooth-Devices/dbus-fast/pull/403),
  [`bfd48a3`](https://github.com/Bluetooth-Devices/dbus-fast/commit/bfd48a3a38cba0dc66d581eedd0da0b228bc1953))


## v2.36.0 (2025-03-05)

### Chores

- Add covdefaults ([#401](https://github.com/Bluetooth-Devices/dbus-fast/pull/401),
  [`dc3d8e7`](https://github.com/Bluetooth-Devices/dbus-fast/commit/dc3d8e7609f37a2f064a45ae525c5ce5711ea272))

- Upgrade typing on private modules
  ([#402](https://github.com/Bluetooth-Devices/dbus-fast/pull/402),
  [`640e1f8`](https://github.com/Bluetooth-Devices/dbus-fast/commit/640e1f8d87a753d6721dae77ee94ff8702a2f508))

* chore: upgrade typing on private modules

* chore: typing fixes

### Features

- Refactor service bus handler lookup to avoid linear searches
  ([#400](https://github.com/Bluetooth-Devices/dbus-fast/pull/400),
  [`996659e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/996659e1b5fefeda7eb01259714a4a17fc224b9f))


## v2.35.1 (2025-03-05)

### Bug Fixes

- Reduce size of wheels ([#399](https://github.com/Bluetooth-Devices/dbus-fast/pull/399),
  [`6531b93`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6531b93a5ba5447494818cf7f8c38454b1338052))

first attempt failed to change the correct constant in build_ext.py


## v2.35.0 (2025-03-05)

### Chores

- **deps-ci**: Bump python-semantic-release/python-semantic-release from 9.17.0 to 9.21.0 in the
  github-actions group ([#394](https://github.com/Bluetooth-Devices/dbus-fast/pull/394),
  [`a7e1a90`](https://github.com/Bluetooth-Devices/dbus-fast/commit/a7e1a907e360c1f3fc01a62a414693782f536e61))

chore(deps-ci): bump python-semantic-release/python-semantic-release

Bumps the github-actions group with 1 update:
  [python-semantic-release/python-semantic-release](https://github.com/python-semantic-release/python-semantic-release).

Updates `python-semantic-release/python-semantic-release` from 9.17.0 to 9.21.0 - [Release
  notes](https://github.com/python-semantic-release/python-semantic-release/releases) -
  [Changelog](https://github.com/python-semantic-release/python-semantic-release/blob/master/CHANGELOG.rst)
  -
  [Commits](https://github.com/python-semantic-release/python-semantic-release/compare/v9.17.0...v9.21.0)

--- updated-dependencies: - dependency-name: python-semantic-release/python-semantic-release
  dependency-type: direct:production

update-type: version-update:semver-minor

dependency-group: github-actions ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump pytest from 8.3.4 to 8.3.5
  ([#395](https://github.com/Bluetooth-Devices/dbus-fast/pull/395),
  [`0d0e600`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0d0e600a940fa4cb82473fec7bfb8706ed7ff7f7))

- **deps-dev**: Bump setuptools from 75.8.0 to 75.8.2
  ([#396](https://github.com/Bluetooth-Devices/dbus-fast/pull/396),
  [`2623a74`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2623a7412afeb906b2863b05fefb0d94e8881dcb))

- **pre-commit.ci**: Pre-commit autoupdate
  ([#392](https://github.com/Bluetooth-Devices/dbus-fast/pull/392),
  [`3ef89bf`](https://github.com/Bluetooth-Devices/dbus-fast/commit/3ef89bfbf45592401dae60bf93104e063f082160))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>

- **pre-commit.ci**: Pre-commit autoupdate
  ([#397](https://github.com/Bluetooth-Devices/dbus-fast/pull/397),
  [`3dd7c35`](https://github.com/Bluetooth-Devices/dbus-fast/commit/3dd7c358fad92ef7dcb42c361ebac367f10e3ce2))

updates: - [github.com/commitizen-tools/commitizen: v4.2.2 →
  v4.4.1](https://github.com/commitizen-tools/commitizen/compare/v4.2.2...v4.4.1) -
  [github.com/astral-sh/ruff-pre-commit: v0.9.7 →
  v0.9.9](https://github.com/astral-sh/ruff-pre-commit/compare/v0.9.7...v0.9.9)

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>

### Features

- Reduce size of wheels ([#398](https://github.com/Bluetooth-Devices/dbus-fast/pull/398),
  [`a4c2743`](https://github.com/Bluetooth-Devices/dbus-fast/commit/a4c2743420f619d8808413d8877b2c9badc5f3f0))

Compile with -g0 to reduce the binary size


## v2.34.0 (2025-02-24)

### Chores

- **deps-dev**: Bump cython from 3.0.11 to 3.0.12
  ([#391](https://github.com/Bluetooth-Devices/dbus-fast/pull/391),
  [`5f26f5d`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5f26f5d58c5e0ed6251c66ab4724f27a383500a0))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **pre-commit.ci**: Pre-commit autoupdate
  ([#389](https://github.com/Bluetooth-Devices/dbus-fast/pull/389),
  [`c713bf3`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c713bf3de994564c92628f92bdf341fbf813c8f4))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>

### Features

- Resync generic D-Bus errors ([#393](https://github.com/Bluetooth-Devices/dbus-fast/pull/393),
  [`e4f37ee`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e4f37ee10bd2af64716de0bd389db90b47373b76))


## v2.33.0 (2025-02-05)

### Chores

- **deps-dev**: Bump pytest-asyncio from 0.25.2 to 0.25.3
  ([#385](https://github.com/Bluetooth-Devices/dbus-fast/pull/385),
  [`e6c75a6`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e6c75a61828e260830720cff36a010e54b7efebe))

- **deps-dev**: Bump pytest-codspeed from 3.1.2 to 3.2.0
  ([#384](https://github.com/Bluetooth-Devices/dbus-fast/pull/384),
  [`9f966af`](https://github.com/Bluetooth-Devices/dbus-fast/commit/9f966af1dbeba8af6d7119877801e5140daf4002))

- **pre-commit.ci**: Pre-commit autoupdate
  ([#386](https://github.com/Bluetooth-Devices/dbus-fast/pull/386),
  [`0a9e4c5`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0a9e4c5a2140f20f580c67bed2a68ff0ac524b62))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>

### Features

- Build macos arm wheels ([#387](https://github.com/Bluetooth-Devices/dbus-fast/pull/387),
  [`829e0fc`](https://github.com/Bluetooth-Devices/dbus-fast/commit/829e0fc149957b3bf0fc0f4a89bb2e676e584f84))


## v2.32.0 (2025-02-02)

### Features

- Speed up marshalling messages ([#383](https://github.com/Bluetooth-Devices/dbus-fast/pull/383),
  [`d7213be`](https://github.com/Bluetooth-Devices/dbus-fast/commit/d7213be28578b3effa3aeea85bab5de92bba224d))


## v2.31.0 (2025-02-02)

### Features

- Speed up bytearray creation in unmarshaller
  ([#382](https://github.com/Bluetooth-Devices/dbus-fast/pull/382),
  [`89026e3`](https://github.com/Bluetooth-Devices/dbus-fast/commit/89026e3b597bd1a318114b6cf50e27d29d9cbca8))


## v2.30.4 (2025-02-02)

### Bug Fixes

- Docs build ([#381](https://github.com/Bluetooth-Devices/dbus-fast/pull/381),
  [`c21a2ac`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c21a2ac15a09b2ebf79afa53439fbc45214d4dc0))


## v2.30.3 (2025-02-02)

### Bug Fixes

- Attempting to unmarshall some arrays twice
  ([#380](https://github.com/Bluetooth-Devices/dbus-fast/pull/380),
  [`586dc23`](https://github.com/Bluetooth-Devices/dbus-fast/commit/586dc233fdb2ebc7d627cb94b55d80a77631416f))

### Chores

- Bump the github-actions group with 9 updates
  ([#372](https://github.com/Bluetooth-Devices/dbus-fast/pull/372),
  [`94ba266`](https://github.com/Bluetooth-Devices/dbus-fast/commit/94ba26653987b7200cfb85ed92d46ea5d95a95a0))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: J. Nick Koston <nick@koston.org>

- Bump upload/download artifact to v4
  ([#370](https://github.com/Bluetooth-Devices/dbus-fast/pull/370),
  [`29be224`](https://github.com/Bluetooth-Devices/dbus-fast/commit/29be224be7fd05970aa5473b8e86810c8978ab6c))

- Fix commitlint config ([#374](https://github.com/Bluetooth-Devices/dbus-fast/pull/374),
  [`b13712f`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b13712f4c51810d9384b1fc924e61ad984800719))

- Fix release process ([#375](https://github.com/Bluetooth-Devices/dbus-fast/pull/375),
  [`de57a21`](https://github.com/Bluetooth-Devices/dbus-fast/commit/de57a21a3c22224032fd5e2672560a00e2fbcd12))

- Fix release upload ([#377](https://github.com/Bluetooth-Devices/dbus-fast/pull/377),
  [`eb56b64`](https://github.com/Bluetooth-Devices/dbus-fast/commit/eb56b6464d9dc0c18465bf68030634f78a36fc5c))

- Fix semantic release fields ([#376](https://github.com/Bluetooth-Devices/dbus-fast/pull/376),
  [`4fe13e8`](https://github.com/Bluetooth-Devices/dbus-fast/commit/4fe13e88d1b636136e88ff6eacec0d6293280868))

- Update dependabot.yml prefix
  ([`c4e37b0`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c4e37b077cb27d2916150aa57a90633b3eea3489))

- Update dependabot.yml to include actions
  ([`56c1595`](https://github.com/Bluetooth-Devices/dbus-fast/commit/56c1595be9f8047fd8f983e4baca9a92d5de0772))

- **deps-ci**: Bump the github-actions group with 2 updates
  ([#379](https://github.com/Bluetooth-Devices/dbus-fast/pull/379),
  [`1aab230`](https://github.com/Bluetooth-Devices/dbus-fast/commit/1aab2304398de8a3dd7789efe4f82fb04eb54e37))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump pytest from 7.4.4 to 8.3.4
  ([#334](https://github.com/Bluetooth-Devices/dbus-fast/pull/334),
  [`9ad3873`](https://github.com/Bluetooth-Devices/dbus-fast/commit/9ad38730d57d92bf621d5ed799369b63e15aa1c0))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: J. Nick Koston <nick@koston.org>

- **deps-dev**: Bump pytest-asyncio from 0.23.8 to 0.25.2
  ([#373](https://github.com/Bluetooth-Devices/dbus-fast/pull/373),
  [`922840b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/922840ba9d537a60b139f5becfd993fe84b1d50d))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **pre-commit.ci**: Pre-commit autoupdate
  ([#369](https://github.com/Bluetooth-Devices/dbus-fast/pull/369),
  [`9953959`](https://github.com/Bluetooth-Devices/dbus-fast/commit/995395953045969103361d08bf4f5de52ebe8790))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>

- **pre-commit.ci**: Pre-commit autoupdate
  ([#378](https://github.com/Bluetooth-Devices/dbus-fast/pull/378),
  [`b58620a`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b58620afd8e4981162677464689d2afd4474621d))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>


## v2.30.2 (2025-01-17)

### Bug Fixes

- Fetching release tag during build
  ([#368](https://github.com/Bluetooth-Devices/dbus-fast/pull/368),
  [`5a80415`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5a804159669c2caad9d1144120ebaeb602d9ad28))


## v2.30.1 (2025-01-17)

### Bug Fixes

- Wheel builds on aarch64 ([#367](https://github.com/Bluetooth-Devices/dbus-fast/pull/367),
  [`18132b9`](https://github.com/Bluetooth-Devices/dbus-fast/commit/18132b99bcbada1f090ccfc1c0050caf0827cd11))


## v2.30.0 (2025-01-17)

### Features

- Migrate to using native arm runners for wheel builds
  ([#366](https://github.com/Bluetooth-Devices/dbus-fast/pull/366),
  [`bdf08d2`](https://github.com/Bluetooth-Devices/dbus-fast/commit/bdf08d253bff9bc1edd7c9a5688b7d9e4eb73839))


## v2.29.0 (2025-01-15)

### Bug Fixes

- Void validate arguments/properties name
  ([#358](https://github.com/Bluetooth-Devices/dbus-fast/pull/358),
  [`f58f1a6`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f58f1a6466d7ffb3a600774f8c36b5c93279437b))

### Chores

- **deps**: Bump sphinx from 7.1.2 to 7.4.7
  ([#361](https://github.com/Bluetooth-Devices/dbus-fast/pull/361),
  [`0487639`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0487639ed702892a365f70991682f023aec29116))

- **deps-dev**: Bump pytest-codspeed from 3.1.1 to 3.1.2
  ([#362](https://github.com/Bluetooth-Devices/dbus-fast/pull/362),
  [`e7750ca`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e7750caed5791aef0cbb8c62e82ccabf02f65df7))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump pytest-cov from 5.0.0 to 6.0.0
  ([#363](https://github.com/Bluetooth-Devices/dbus-fast/pull/363),
  [`244ea83`](https://github.com/Bluetooth-Devices/dbus-fast/commit/244ea83a31631c54b3d97ad47b91786e1d02387f))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump setuptools from 75.7.0 to 75.8.0
  ([#364](https://github.com/Bluetooth-Devices/dbus-fast/pull/364),
  [`8eee3a8`](https://github.com/Bluetooth-Devices/dbus-fast/commit/8eee3a82fdf2f2fde2dac52c4854b16e8bf0ac8d))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **pre-commit.ci**: Pre-commit autoupdate
  ([#365](https://github.com/Bluetooth-Devices/dbus-fast/pull/365),
  [`e006a1e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e006a1e861df6c3368f10600f6c390becae15c5c))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>

### Features

- **introspect**: Implement annotations
  ([#359](https://github.com/Bluetooth-Devices/dbus-fast/pull/359),
  [`5b61869`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5b61869baec88cd1382419f4580c345473543493))

Co-authored-by: J. Nick Koston <nick@koston.org>

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>


## v2.28.0 (2025-01-07)

### Bug Fixes

- Revert avoid building wheels if a release is not made
  ([#357](https://github.com/Bluetooth-Devices/dbus-fast/pull/357),
  [`ebdf07e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ebdf07ec9e875806c050c97027b6f7dca077bd7d))

### Features

- Improve performance of marshalling message headers
  ([#356](https://github.com/Bluetooth-Devices/dbus-fast/pull/356),
  [`e1aaf0a`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e1aaf0a3969d595bc9d789cb5e40dfd59ef232c9))

- Improve performance of unmarshalling variants
  ([#354](https://github.com/Bluetooth-Devices/dbus-fast/pull/354),
  [`d376bb1`](https://github.com/Bluetooth-Devices/dbus-fast/commit/d376bb13ade9bac8b478a183a4a280d37d121ab9))


## v2.27.0 (2025-01-07)

### Chores

- Add marshall benchmark ([#353](https://github.com/Bluetooth-Devices/dbus-fast/pull/353),
  [`1164ca5`](https://github.com/Bluetooth-Devices/dbus-fast/commit/1164ca55dd7bb915bcac61e8a9b15ae009d51b66))

- Avoid building wheels if a release is not made
  ([#355](https://github.com/Bluetooth-Devices/dbus-fast/pull/355),
  [`f9ec254`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f9ec25415064deb272e5664cd215f7dd31b869c0))

### Features

- Speed up marshalling messages ([#352](https://github.com/Bluetooth-Devices/dbus-fast/pull/352),
  [`b1e6551`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b1e6551de32bec5a8a5164540d44e1b1bfe86881))


## v2.26.0 (2025-01-07)

### Features

- Speed up constructing messages from the unmarshaller
  ([#344](https://github.com/Bluetooth-Devices/dbus-fast/pull/344),
  [`b162494`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b162494aa25fe4b23debdd9a44b49ea21c771ad1))


## v2.25.0 (2025-01-07)

### Bug Fixes

- Race in test_tcp_connection_with_forwarding
  ([#350](https://github.com/Bluetooth-Devices/dbus-fast/pull/350),
  [`4116261`](https://github.com/Bluetooth-Devices/dbus-fast/commit/41162618d4a78c193d91fb9525eb7d2763f17587))

### Chores

- Add codspeed badge ([#351](https://github.com/Bluetooth-Devices/dbus-fast/pull/351),
  [`1f7f52d`](https://github.com/Bluetooth-Devices/dbus-fast/commit/1f7f52dd89f7728c650f92182f14fe768f456621))

### Features

- Speed up unmarshalling headers ([#347](https://github.com/Bluetooth-Devices/dbus-fast/pull/347),
  [`5825758`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5825758991a5d5f476b082c0277e5ecb0767c7e5))


## v2.24.6 (2025-01-07)

### Bug Fixes

- Disable wheel builds for old python versions
  ([#346](https://github.com/Bluetooth-Devices/dbus-fast/pull/346),
  [`a249777`](https://github.com/Bluetooth-Devices/dbus-fast/commit/a249777e03d71502cbbde5d20cab2f3685fb5adb))

### Chores

- Bump codecov action to v5 ([#343](https://github.com/Bluetooth-Devices/dbus-fast/pull/343),
  [`d1298de`](https://github.com/Bluetooth-Devices/dbus-fast/commit/d1298de2a1e0f7aa6277835a55df1229c6552e8a))


## v2.24.5 (2025-01-07)

### Bug Fixes

- Ensure exceptions are logged when no reply is expected
  ([#342](https://github.com/Bluetooth-Devices/dbus-fast/pull/342),
  [`1c20dcc`](https://github.com/Bluetooth-Devices/dbus-fast/commit/1c20dcc50471b453d9b55bc2be197fd5b0c38a9c))

### Chores

- Add codspeed benchmarks ([#340](https://github.com/Bluetooth-Devices/dbus-fast/pull/340),
  [`5bf90b9`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5bf90b9fb15e243801f7d39e7e57b52f5c694bcc))

- Drop Python 3.8 support as it has reached EOL
  ([#338](https://github.com/Bluetooth-Devices/dbus-fast/pull/338),
  [`42a786b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/42a786b23ff519d653d8accf7950b18604f3070a))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>

- Split wheel builds to speed up releases
  ([#341](https://github.com/Bluetooth-Devices/dbus-fast/pull/341),
  [`439b2da`](https://github.com/Bluetooth-Devices/dbus-fast/commit/439b2da8789d7e0ca0a70e4d4c074666248bd492))

- Switch to ruff ([#339](https://github.com/Bluetooth-Devices/dbus-fast/pull/339),
  [`eda3706`](https://github.com/Bluetooth-Devices/dbus-fast/commit/eda37061c4b4068a2fd6b051f9becfc8ae7bba10))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>

- **deps**: Bump sphinx-rtd-theme from 3.0.1 to 3.0.2
  ([#332](https://github.com/Bluetooth-Devices/dbus-fast/pull/332),
  [`42ef44a`](https://github.com/Bluetooth-Devices/dbus-fast/commit/42ef44a4aa38491b7608f84d84a6349aa11703e6))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump sphinx-rtd-theme from 3.0.1 to 3.0.2
  ([#335](https://github.com/Bluetooth-Devices/dbus-fast/pull/335),
  [`663b371`](https://github.com/Bluetooth-Devices/dbus-fast/commit/663b37136f1b75245292d6bc6633e3184ff3d228))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **pre-commit.ci**: Pre-commit autoupdate
  ([#333](https://github.com/Bluetooth-Devices/dbus-fast/pull/333),
  [`b5c01a9`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b5c01a926c95d6e65c2c597846596373393c88a2))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>

- **pre-commit.ci**: Pre-commit autoupdate
  ([#336](https://github.com/Bluetooth-Devices/dbus-fast/pull/336),
  [`ea24a86`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ea24a86c1b2bb2b25da8e892a641bcd4e6b24b30))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>

- **pre-commit.ci**: Pre-commit autoupdate
  ([#337](https://github.com/Bluetooth-Devices/dbus-fast/pull/337),
  [`471e680`](https://github.com/Bluetooth-Devices/dbus-fast/commit/471e68035470b2f6b29500347ec3e0443dc3648e))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>


## v2.24.4 (2024-11-15)

### Bug Fixes

- Exclude .c files from being shipped
  ([#331](https://github.com/Bluetooth-Devices/dbus-fast/pull/331),
  [`9c73022`](https://github.com/Bluetooth-Devices/dbus-fast/commit/9c7302299ab002a1aec80062f0b9bd5c1bde46f9))

### Chores

- **deps**: Bump sphinx-rtd-theme from 2.0.0 to 3.0.0
  ([#319](https://github.com/Bluetooth-Devices/dbus-fast/pull/319),
  [`f30bc57`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f30bc57bbad6e3fa2c62956233d171dfc9e7f3d9))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump sphinx-rtd-theme from 2.0.0 to 3.0.1
  ([#322](https://github.com/Bluetooth-Devices/dbus-fast/pull/322),
  [`3131841`](https://github.com/Bluetooth-Devices/dbus-fast/commit/31318414720ecaa4b86ac8afbdb20066c9f43e07))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump sphinx-rtd-theme from 3.0.0 to 3.0.1
  ([#326](https://github.com/Bluetooth-Devices/dbus-fast/pull/326),
  [`2831f9c`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2831f9cc3633d4c6e47232f741213da2adbaf71a))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump setuptools from 75.1.0 to 75.2.0
  ([#324](https://github.com/Bluetooth-Devices/dbus-fast/pull/324),
  [`fa3faa8`](https://github.com/Bluetooth-Devices/dbus-fast/commit/fa3faa86eec5568d74db2d1b8aa4c9af18b236f1))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump setuptools from 75.2.0 to 75.3.0
  ([#328](https://github.com/Bluetooth-Devices/dbus-fast/pull/328),
  [`83bb550`](https://github.com/Bluetooth-Devices/dbus-fast/commit/83bb5502ed17a1d8256d27ef86079c3688d5a3cd))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **pre-commit.ci**: Pre-commit autoupdate
  ([#320](https://github.com/Bluetooth-Devices/dbus-fast/pull/320),
  [`46bc330`](https://github.com/Bluetooth-Devices/dbus-fast/commit/46bc3304a31149c3a0c4fdc3aa2047ea2232a22d))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>

Co-authored-by: J. Nick Koston <nick@koston.org>

- **pre-commit.ci**: Pre-commit autoupdate
  ([#323](https://github.com/Bluetooth-Devices/dbus-fast/pull/323),
  [`9e2f17a`](https://github.com/Bluetooth-Devices/dbus-fast/commit/9e2f17a974fa7b2defdccc5038ace446567bb0b0))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>

- **pre-commit.ci**: Pre-commit autoupdate
  ([#327](https://github.com/Bluetooth-Devices/dbus-fast/pull/327),
  [`4d3acc4`](https://github.com/Bluetooth-Devices/dbus-fast/commit/4d3acc49659779e6d3d2a57ed47ede49ce6b4208))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>


## v2.24.3 (2024-10-05)

### Bug Fixes

- Remove deprecated no_type_check_decorator
  ([#316](https://github.com/Bluetooth-Devices/dbus-fast/pull/316),
  [`0f04a79`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0f04a794f2e8b494c194e4f4856e43917bdda58a))

### Chores

- **deps**: Bump sphinx from 5.2.3 to 7.1.2
  ([#312](https://github.com/Bluetooth-Devices/dbus-fast/pull/312),
  [`34d0d46`](https://github.com/Bluetooth-Devices/dbus-fast/commit/34d0d461c8764ae4aca0992909a22f03bf7d3133))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump setuptools from 74.1.2 to 75.1.0
  ([#314](https://github.com/Bluetooth-Devices/dbus-fast/pull/314),
  [`aaa1e1e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/aaa1e1e0ea5a399897eaf185ce696f03d17ff4a9))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **pre-commit.ci**: Pre-commit autoupdate
  ([#317](https://github.com/Bluetooth-Devices/dbus-fast/pull/317),
  [`f2de447`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f2de4472dde27ca7dc1a83f049fbb89e0b2c6bb9))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>


## v2.24.2 (2024-09-06)

### Bug Fixes

- Ensure build uses cython3 ([#311](https://github.com/Bluetooth-Devices/dbus-fast/pull/311),
  [`2dabf2d`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2dabf2ddcbbd7e46551521100734372a52458ce4))


## v2.24.1 (2024-09-06)

### Bug Fixes

- Add missing cython version pin to the build system
  ([#310](https://github.com/Bluetooth-Devices/dbus-fast/pull/310),
  [`1b7d28c`](https://github.com/Bluetooth-Devices/dbus-fast/commit/1b7d28cd1f1b78631335cc9945be218aacf6e3f6))

### Chores

- **deps**: Bump myst-parser from 1.0.0 to 3.0.1
  ([#306](https://github.com/Bluetooth-Devices/dbus-fast/pull/306),
  [`8b3e95c`](https://github.com/Bluetooth-Devices/dbus-fast/commit/8b3e95c6cc6d9e8396d2ee6b1883df700fb3f23b))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump sphinx from 5.2.3 to 7.1.2
  ([#307](https://github.com/Bluetooth-Devices/dbus-fast/pull/307),
  [`e393611`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e393611fbf44f5f0598c8f7762034356a893cdbb))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump setuptools from 73.0.1 to 74.0.0
  ([#308](https://github.com/Bluetooth-Devices/dbus-fast/pull/308),
  [`757a742`](https://github.com/Bluetooth-Devices/dbus-fast/commit/757a7424d20efc61f2de1f5f447277fd17eb94ed))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>


## v2.24.0 (2024-08-26)

### Chores

- **deps**: Bump myst-parser from 0.18.1 to 1.0.0
  ([#296](https://github.com/Bluetooth-Devices/dbus-fast/pull/296),
  [`b225cca`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b225cca97a60a8c05b892d438b461904efc42fa2))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump myst-parser from 0.18.1 to 1.0.0
  ([#304](https://github.com/Bluetooth-Devices/dbus-fast/pull/304),
  [`0b372ea`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0b372eac98e962c349d1933472d37085fb5abad7))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump myst-parser from 1.0.0 to 3.0.1
  ([#305](https://github.com/Bluetooth-Devices/dbus-fast/pull/305),
  [`dae0088`](https://github.com/Bluetooth-Devices/dbus-fast/commit/dae00881a7922af67a5d1076a31bc295d43f5e14))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump sphinx from 5.2.3 to 6.2.1
  ([#300](https://github.com/Bluetooth-Devices/dbus-fast/pull/300),
  [`ad1e078`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ad1e078ee9d11ab8bcffe3df8e20f2d0337a2dd1))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump sphinx-rtd-theme from 1.0.0 to 2.0.0
  ([#293](https://github.com/Bluetooth-Devices/dbus-fast/pull/293),
  [`95df9a6`](https://github.com/Bluetooth-Devices/dbus-fast/commit/95df9a6265b62d9e7f0c243f1cf5b0e64a18f369))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump sphinx-rtd-theme from 1.0.0 to 2.0.0
  ([#302](https://github.com/Bluetooth-Devices/dbus-fast/pull/302),
  [`6e496eb`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6e496eb222ed3c20627c0fc7c2c3f2e5f0dfb807))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump pytest-cov from 3.0.0 to 5.0.0
  ([#301](https://github.com/Bluetooth-Devices/dbus-fast/pull/301),
  [`84c7346`](https://github.com/Bluetooth-Devices/dbus-fast/commit/84c73467ac43218091320989b3e32f8a36840c23))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

### Features

- Use dbus-run-session to drop X11 dependency
  ([#299](https://github.com/Bluetooth-Devices/dbus-fast/pull/299),
  [`42f1d4a`](https://github.com/Bluetooth-Devices/dbus-fast/commit/42f1d4a3f2515a301c12f8f485457a878d7df2dc))


## v2.23.0 (2024-08-21)

### Chores

- **deps-dev**: Bump certifi from 2024.6.2 to 2024.7.4 in the pip group across 1 directory
  ([#298](https://github.com/Bluetooth-Devices/dbus-fast/pull/298),
  [`705ad28`](https://github.com/Bluetooth-Devices/dbus-fast/commit/705ad28ce7bd5b455d643101ba9ad682d503360b))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump cython from 0.29.37 to 3.0.11
  ([#292](https://github.com/Bluetooth-Devices/dbus-fast/pull/292),
  [`8b4cdef`](https://github.com/Bluetooth-Devices/dbus-fast/commit/8b4cdefe3e20e8eccdbfbe6402e0593cc8134bbd))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump pytest-asyncio from 0.19.0 to 0.23.8
  ([#294](https://github.com/Bluetooth-Devices/dbus-fast/pull/294),
  [`f946183`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f9461831f49a1172af5a77df3138bdffbd94c61b))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump setuptools from 65.7.0 to 73.0.1
  ([#295](https://github.com/Bluetooth-Devices/dbus-fast/pull/295),
  [`af4989b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/af4989b7f71eb9f77e92832901aeeeee4c7f8504))

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **pre-commit.ci**: Pre-commit autoupdate
  ([#286](https://github.com/Bluetooth-Devices/dbus-fast/pull/286),
  [`5d9bb92`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5d9bb92da6e363320b8afa5942e6f0b4a4ecd4d0))

* chore(pre-commit.ci): pre-commit autoupdate

updates: - [github.com/commitizen-tools/commitizen: v2.32.4 →
  v3.27.0](https://github.com/commitizen-tools/commitizen/compare/v2.32.4...v3.27.0) -
  [github.com/pre-commit/pre-commit-hooks: v4.3.0 →
  v4.6.0](https://github.com/pre-commit/pre-commit-hooks/compare/v4.3.0...v4.6.0) -
  [github.com/pre-commit/mirrors-prettier: v2.7.1 →
  v4.0.0-alpha.8](https://github.com/pre-commit/mirrors-prettier/compare/v2.7.1...v4.0.0-alpha.8) -
  [github.com/asottile/pyupgrade: v2.37.3 →
  v3.16.0](https://github.com/asottile/pyupgrade/compare/v2.37.3...v3.16.0) -
  [github.com/PyCQA/isort: 5.12.0 → 5.13.2](https://github.com/PyCQA/isort/compare/5.12.0...5.13.2)
  - [github.com/psf/black: 22.8.0 → 24.4.2](https://github.com/psf/black/compare/22.8.0...24.4.2)

* chore(pre-commit.ci): auto fixes

---------

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>

- **pre-commit.ci**: Pre-commit autoupdate
  ([#287](https://github.com/Bluetooth-Devices/dbus-fast/pull/287),
  [`b508e1f`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b508e1fc5fbd4f5200b1fa46c913569fc02f6f4e))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>

- **pre-commit.ci**: Pre-commit autoupdate
  ([#288](https://github.com/Bluetooth-Devices/dbus-fast/pull/288),
  [`c960552`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c96055289d697b847e93ed4f4c7fc7c1893e1642))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>

- **pre-commit.ci**: Pre-commit autoupdate
  ([#289](https://github.com/Bluetooth-Devices/dbus-fast/pull/289),
  [`398f643`](https://github.com/Bluetooth-Devices/dbus-fast/commit/398f643f718e15903183f480726d959e0d85c4da))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>

- **pre-commit.ci**: Pre-commit autoupdate
  ([#290](https://github.com/Bluetooth-Devices/dbus-fast/pull/290),
  [`ee98f7c`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ee98f7c4536e9020f1b28fc916c2bfeb52cc31ac))

Co-authored-by: pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>

### Features

- Python 3.13 support ([#291](https://github.com/Bluetooth-Devices/dbus-fast/pull/291),
  [`45c0e74`](https://github.com/Bluetooth-Devices/dbus-fast/commit/45c0e7491da85ed754a86358bffa2260f96c240f))


## v2.22.1 (2024-06-26)

### Bug Fixes

- Wheel build exclude for pp37 ([#285](https://github.com/Bluetooth-Devices/dbus-fast/pull/285),
  [`c44eb2c`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c44eb2cabd8a7c5156d9cb2228f058140c004c36))


## v2.22.0 (2024-06-26)

### Chores

- Drop python 3.7 support ([#284](https://github.com/Bluetooth-Devices/dbus-fast/pull/284),
  [`fa48bc0`](https://github.com/Bluetooth-Devices/dbus-fast/commit/fa48bc025c1edf30451a7c0fb4ec639d927d045c))

### Features

- Build wheels for aarch64 to allow use in embedded systems
  ([#283](https://github.com/Bluetooth-Devices/dbus-fast/pull/283),
  [`d0ac990`](https://github.com/Bluetooth-Devices/dbus-fast/commit/d0ac990a7aa9eec14d8c9c9720e4894de6dcf9b5))


## v2.21.3 (2024-05-20)

### Bug Fixes

- Clear exception flag on disconnect future if its also sent to handlers
  ([#281](https://github.com/Bluetooth-Devices/dbus-fast/pull/281),
  [`be68a79`](https://github.com/Bluetooth-Devices/dbus-fast/commit/be68a79c523e7ff360a4f9914b41956b5f430d93))


## v2.21.2 (2024-05-08)

### Bug Fixes

- Introspection bogus child paths ([#280](https://github.com/Bluetooth-Devices/dbus-fast/pull/280),
  [`7da5d44`](https://github.com/Bluetooth-Devices/dbus-fast/commit/7da5d44caacecd9af2f8198e7403d7d043c87579))


## v2.21.1 (2024-01-16)

### Bug Fixes

- Avoid expensive runtime inspection of known callables
  ([#277](https://github.com/Bluetooth-Devices/dbus-fast/pull/277),
  [`0271825`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0271825e7338dd8422975d9289768363b5b6b9de))


## v2.21.0 (2023-12-12)

### Features

- Speed up message callbacks ([#276](https://github.com/Bluetooth-Devices/dbus-fast/pull/276),
  [`2b8770b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2b8770b892ee75b851d5d58967e3a9e3149430dc))


## v2.20.0 (2023-12-04)

### Features

- Speed up run time constructed method handlers
  ([#275](https://github.com/Bluetooth-Devices/dbus-fast/pull/275),
  [`9f54fc3`](https://github.com/Bluetooth-Devices/dbus-fast/commit/9f54fc3194370bb4c6fd51c158b577adce1b517f))


## v2.19.0 (2023-12-04)

### Features

- Speed up ServiceInterface callbacks with cython methods
  ([#274](https://github.com/Bluetooth-Devices/dbus-fast/pull/274),
  [`0e57d79`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0e57d798a2f171f804603cb5a3659de08092e74b))


## v2.18.0 (2023-12-04)

### Features

- Small speed up to the aio message reader
  ([#273](https://github.com/Bluetooth-Devices/dbus-fast/pull/273),
  [`8ee18a1`](https://github.com/Bluetooth-Devices/dbus-fast/commit/8ee18a1355b247e3ef9c7ad5f561d7cc8f9cf4a2))


## v2.17.0 (2023-12-04)

### Features

- Reduce duplicate code in aio MessageBus
  ([#272](https://github.com/Bluetooth-Devices/dbus-fast/pull/272),
  [`502ab0d`](https://github.com/Bluetooth-Devices/dbus-fast/commit/502ab0d47f667bb24cd7b3f1d8fa97e2d0345676))


## v2.16.0 (2023-12-04)

### Features

- Speed up sending messages with call on the MessageBus
  ([#271](https://github.com/Bluetooth-Devices/dbus-fast/pull/271),
  [`6d7f522`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6d7f522e1cc5181e75209e4c00109426baa335fc))


## v2.15.0 (2023-11-22)

### Features

- Make ErrorType enums compare as strings
  ([#269](https://github.com/Bluetooth-Devices/dbus-fast/pull/269),
  [`c6a8301`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c6a8301704162e1c4d07470c32ca0830f531b6d4))

The DBusError exception stores the error type as string. This makes the exception not directly
  compare to the ErrorType members (for example DBusError(ErrorType.FAILED, "").type !=
  ErrorType.FAILED). This makes ErrorType also a string to make this comparision work.


## v2.14.0 (2023-11-10)

### Features

- Add support for tuples to the marshaller
  ([#267](https://github.com/Bluetooth-Devices/dbus-fast/pull/267),
  [`0ccb7c5`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0ccb7c5d879fc787c12e35c659b0be88bcbed7fe))


## v2.13.1 (2023-11-07)

### Bug Fixes

- Re-release since the previous release ran out of space on PyPI
  ([#266](https://github.com/Bluetooth-Devices/dbus-fast/pull/266),
  [`1586221`](https://github.com/Bluetooth-Devices/dbus-fast/commit/158622157f547aba80bbd06579915d7a5e145d58))


## v2.13.0 (2023-11-07)

### Features

- Improve marshaller performance ([#264](https://github.com/Bluetooth-Devices/dbus-fast/pull/264),
  [`5bdb161`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5bdb161c0a70074e0466e9332dce9c27b497916b))


## v2.12.1 (2023-11-07)

### Bug Fixes

- Send reply test failure with cython
  ([#265](https://github.com/Bluetooth-Devices/dbus-fast/pull/265),
  [`e634fc2`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e634fc2c701c25353f805dbe5fe52f67fa896b7d))


## v2.12.0 (2023-10-18)

### Bug Fixes

- Reduce size of wheels by excluding generated .c files
  ([#262](https://github.com/Bluetooth-Devices/dbus-fast/pull/262),
  [`dca4599`](https://github.com/Bluetooth-Devices/dbus-fast/commit/dca459900e19e7340b68601d13422c83a7d67a19))

### Features

- Update for final cpython release ([#263](https://github.com/Bluetooth-Devices/dbus-fast/pull/263),
  [`460a072`](https://github.com/Bluetooth-Devices/dbus-fast/commit/460a072652793829b217720846fbf10f8e2ebadb))


## v2.11.1 (2023-10-04)

### Bug Fixes

- Marshall multi-byte strings correctly
  ([#261](https://github.com/Bluetooth-Devices/dbus-fast/pull/261),
  [`4de31a3`](https://github.com/Bluetooth-Devices/dbus-fast/commit/4de31a36463ff8e2d85225973c4553c15623afb6))

### Chores

- Add benchmark for GetValue ([#258](https://github.com/Bluetooth-Devices/dbus-fast/pull/258),
  [`2fc723e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2fc723eacb24802b87ca712c89b76f6f95a64f1a))

- Add more unmarshall tests ([#259](https://github.com/Bluetooth-Devices/dbus-fast/pull/259),
  [`4d3b666`](https://github.com/Bluetooth-Devices/dbus-fast/commit/4d3b666564fae3b813f57b446fb43dd27691e16e))

- Add more unmarshall tests ([#260](https://github.com/Bluetooth-Devices/dbus-fast/pull/260),
  [`f9e5d1d`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f9e5d1d02025fee50f641ee2bb82607a494c06dd))


## v2.11.0 (2023-09-27)

### Features

- Speed up unpacking arrays ([#257](https://github.com/Bluetooth-Devices/dbus-fast/pull/257),
  [`5c8bfe5`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5c8bfe5e15a1c5de150975ebdaf1677801397555))


## v2.10.0 (2023-09-25)

### Features

- Speed up constructing Variant objects
  ([#256](https://github.com/Bluetooth-Devices/dbus-fast/pull/256),
  [`0d7a665`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0d7a6652d797efcffaa0fa35039252c33522c15e))


## v2.9.0 (2023-09-20)

### Features

- Speed up unmarshalling message body
  ([#255](https://github.com/Bluetooth-Devices/dbus-fast/pull/255),
  [`5aed075`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5aed07516611692f935cac6fb612204c6f419fec))


## v2.8.0 (2023-09-20)

### Features

- Speed up unmarshalling Variants ([#254](https://github.com/Bluetooth-Devices/dbus-fast/pull/254),
  [`dd74a84`](https://github.com/Bluetooth-Devices/dbus-fast/commit/dd74a8409db40abdaeba2fdcd578ae3998692470))


## v2.7.0 (2023-09-13)

### Features

- Speed up readers in the unmarshall path
  ([#253](https://github.com/Bluetooth-Devices/dbus-fast/pull/253),
  [`f9b61b8`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f9b61b8bc734b0179bde2c08e46c02de65f27e50))


## v2.6.0 (2023-09-12)

### Features

- Speed up first connection when using asyncio
  ([#251](https://github.com/Bluetooth-Devices/dbus-fast/pull/251),
  [`0b6ba93`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0b6ba93f733a78f1fb52ddfa24163de44f09df53))


## v2.5.0 (2023-09-12)

### Features

- Speed up unmarshaller ([#250](https://github.com/Bluetooth-Devices/dbus-fast/pull/250),
  [`e4cae13`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e4cae13e1a25356437658a03ee60522a68a56d56))


## v2.4.0 (2023-09-12)

### Chores

- Bump cpython CI version ([#249](https://github.com/Bluetooth-Devices/dbus-fast/pull/249),
  [`16b31f9`](https://github.com/Bluetooth-Devices/dbus-fast/commit/16b31f91e50e8def4b7ee7066be0bd375b123f0a))

### Features

- Add cython typing for ServiceInterface.name
  ([#248](https://github.com/Bluetooth-Devices/dbus-fast/pull/248),
  [`98c7e75`](https://github.com/Bluetooth-Devices/dbus-fast/commit/98c7e753755741967bad0618f056605bc2eaa743))


## v2.3.0 (2023-09-11)

### Features

- Speed up connect and disconnect ([#247](https://github.com/Bluetooth-Devices/dbus-fast/pull/247),
  [`8f39ba3`](https://github.com/Bluetooth-Devices/dbus-fast/commit/8f39ba3ada1dfdec8d7230c77e52ef802e91b23d))


## v2.2.0 (2023-09-10)

### Features

- Speed up unmarshalling by skipping unused unix_fds header
  ([#246](https://github.com/Bluetooth-Devices/dbus-fast/pull/246),
  [`5f5a150`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5f5a150ca01810bf3a2a90043f77ee7100c8242d))


## v2.1.0 (2023-09-10)

### Features

- Reduce overhead to reset between messages
  ([#245](https://github.com/Bluetooth-Devices/dbus-fast/pull/245),
  [`da30b04`](https://github.com/Bluetooth-Devices/dbus-fast/commit/da30b04a15aed08ba920fabd0abad372e953c394))


## v2.0.1 (2023-09-08)

### Bug Fixes

- Clean up address parsing and tests
  ([#244](https://github.com/Bluetooth-Devices/dbus-fast/pull/244),
  [`370791d`](https://github.com/Bluetooth-Devices/dbus-fast/commit/370791da869040d4a0d92cde30c4d2d4d684bcdc))


## v2.0.0 (2023-09-07)

### Features

- Don't import backends by default ([#243](https://github.com/Bluetooth-Devices/dbus-fast/pull/243),
  [`091d421`](https://github.com/Bluetooth-Devices/dbus-fast/commit/091d421a94752f749999858540000e0ab8a83da4))


## v1.95.2 (2023-09-07)

### Bug Fixes

- Handling of None messages from notify callback
  ([#236](https://github.com/Bluetooth-Devices/dbus-fast/pull/236),
  [`14f52f2`](https://github.com/Bluetooth-Devices/dbus-fast/commit/14f52f216d49fb52bf223d5d96306465bb61e49c))

Co-authored-by: Remy Noel <remy.noel@blade-group.com>

Co-authored-by: J. Nick Koston <nick@koston.org>


## v1.95.1 (2023-09-07)

### Bug Fixes

- Handle multiple flag bits when unmarshalling
  ([#241](https://github.com/Bluetooth-Devices/dbus-fast/pull/241),
  [`6f6f5f8`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6f6f5f86c020866a0c1ef5573547e25c63c8d3c3))

### Chores

- Add test coverage for issue 239 ([#240](https://github.com/Bluetooth-Devices/dbus-fast/pull/240),
  [`0386dc2`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0386dc232274c6de0717e9a3f280d98379acbf45))


## v1.95.0 (2023-09-06)

### Features

- Small speed up to the unmarshaller
  ([#238](https://github.com/Bluetooth-Devices/dbus-fast/pull/238),
  [`b8d0e9b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b8d0e9be4c7eb7c16347e7bf57f8bf40d0c293d0))


## v1.94.1 (2023-08-27)

### Bug Fixes

- Rebuild wheels with cython 3.0.2 ([#235](https://github.com/Bluetooth-Devices/dbus-fast/pull/235),
  [`e8901a8`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e8901a8f7d82a93ed2e72576859fde8f942a8889))


## v1.94.0 (2023-08-24)

### Chores

- Bump cpython 3.12 version in CI ([#233](https://github.com/Bluetooth-Devices/dbus-fast/pull/233),
  [`5364492`](https://github.com/Bluetooth-Devices/dbus-fast/commit/53644927b9a35d45cc07499d6bc5e6183f9239fb))

### Features

- Build cpython 3.12 wheels ([#234](https://github.com/Bluetooth-Devices/dbus-fast/pull/234),
  [`b38aa58`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b38aa58aa7b15cf4498edfefabf9a3df37804494))


## v1.93.1 (2023-08-24)

### Bug Fixes

- Avoid cythonizing SendReply ([#232](https://github.com/Bluetooth-Devices/dbus-fast/pull/232),
  [`d12266d`](https://github.com/Bluetooth-Devices/dbus-fast/commit/d12266ddef920a6064c716c4e71ff8414094d0fd))

### Chores

- Add more coverage for send_reply ([#231](https://github.com/Bluetooth-Devices/dbus-fast/pull/231),
  [`ed5c87f`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ed5c87f49206d219e4d43d7091b1453ef9932ac4))

- Add send_reply tests ([#230](https://github.com/Bluetooth-Devices/dbus-fast/pull/230),
  [`a8b9e72`](https://github.com/Bluetooth-Devices/dbus-fast/commit/a8b9e721d56c0b2283cd0cc3d3eb2a44d83bdc3d))


## v1.93.0 (2023-08-21)

### Features

- Improve performance of processing incoming messages
  ([#228](https://github.com/Bluetooth-Devices/dbus-fast/pull/228),
  [`ce61aea`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ce61aea37a55c9498f1800ec4bd68e8eaf7c7f48))


## v1.92.0 (2023-08-18)

### Features

- Reduce overhead to dispatch method handlers
  ([#227](https://github.com/Bluetooth-Devices/dbus-fast/pull/227),
  [`b222552`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b2225527ae57d1bccec21df950d621797d30732d))


## v1.91.4 (2023-08-17)

### Bug Fixes

- Subpath bad matching ([#202](https://github.com/Bluetooth-Devices/dbus-fast/pull/202),
  [`5d6f90b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5d6f90ba32c61b14368f80b91e1d3d9a6279126f))

Co-authored-by: Remy Noel <remy.noel@blade-group.com>

Co-authored-by: J. Nick Koston <nick@koston.org>


## v1.91.3 (2023-08-17)

### Bug Fixes

- Messages could be sent out of order if they had to queue
  ([#225](https://github.com/Bluetooth-Devices/dbus-fast/pull/225),
  [`4051cf2`](https://github.com/Bluetooth-Devices/dbus-fast/commit/4051cf283f61bbfefc4d63c8933b3818483a2d1a))


## v1.91.2 (2023-08-09)

### Bug Fixes

- Avoid checking if a message expects a reply twice
  ([#223](https://github.com/Bluetooth-Devices/dbus-fast/pull/223),
  [`823e85f`](https://github.com/Bluetooth-Devices/dbus-fast/commit/823e85fddc44ceff60558d490013b601ae4bdacd))


## v1.91.1 (2023-08-09)

### Bug Fixes

- Revert changes to _expects_reply from speed up to processing bluez passive data
  ([#222](https://github.com/Bluetooth-Devices/dbus-fast/pull/222),
  [`dfa9053`](https://github.com/Bluetooth-Devices/dbus-fast/commit/dfa9053a03692d3e14032c7d4a4a375400262c78))


## v1.91.0 (2023-08-09)

### Features

- Speed up to processing bluez passive data
  ([#221](https://github.com/Bluetooth-Devices/dbus-fast/pull/221),
  [`8e7432d`](https://github.com/Bluetooth-Devices/dbus-fast/commit/8e7432d31b38fecbbed585c2d5ae510d24ff5af7))


## v1.90.2 (2023-08-05)

### Bug Fixes

- Spelling of `dbus_fast.auth.AuthAnnonymous` to `dbus_fast.auth.AuthAnonymous`
  ([#220](https://github.com/Bluetooth-Devices/dbus-fast/pull/220),
  [`6c2412f`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6c2412f4ca214f1fc95046ab8118bf330aa646da))


## v1.90.1 (2023-08-02)

### Bug Fixes

- More cython3 optional fixes ([#219](https://github.com/Bluetooth-Devices/dbus-fast/pull/219),
  [`5b6cbc5`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5b6cbc560e6add5a0f3f20fc9d37716cb30e9121))


## v1.90.0 (2023-08-02)

### Features

- Remove async_timeout dependency ([#218](https://github.com/Bluetooth-Devices/dbus-fast/pull/218),
  [`7826897`](https://github.com/Bluetooth-Devices/dbus-fast/commit/78268973591985695cb3fa76dd502bb1ef1895ec))


## v1.89.0 (2023-08-02)

### Features

- Speed up Message creation and callbacks
  ([#217](https://github.com/Bluetooth-Devices/dbus-fast/pull/217),
  [`04d6451`](https://github.com/Bluetooth-Devices/dbus-fast/commit/04d64511579be08c7d416664c66d527a7d6d12b6))


## v1.88.0 (2023-08-02)

### Features

- Optimize passive bluez message unmarshaller
  ([#216](https://github.com/Bluetooth-Devices/dbus-fast/pull/216),
  [`e0e87ec`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e0e87ec16ce424dbae83114ca5da13406b913deb))


## v1.87.6 (2023-08-01)

### Bug Fixes

- Exception handler failure when exception is not DBusError
  ([#215](https://github.com/Bluetooth-Devices/dbus-fast/pull/215),
  [`d771bcf`](https://github.com/Bluetooth-Devices/dbus-fast/commit/d771bcf6a2ed08486affe0e2c30bd8dd95ccbb5d))


## v1.87.5 (2023-07-28)

### Bug Fixes

- Result typing in ServiceInterface._handle_signal
  ([#214](https://github.com/Bluetooth-Devices/dbus-fast/pull/214),
  [`5bda04b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5bda04b089b5f089c90c333ca0db02d40d38a8ca))


## v1.87.4 (2023-07-28)

### Bug Fixes

- Avoid double buffering when using asyncio reader without negotiate_unix_fd
  ([#213](https://github.com/Bluetooth-Devices/dbus-fast/pull/213),
  [`c933be7`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c933be709508e0504e97254247bec70eb9e8c6d4))


## v1.87.3 (2023-07-27)

### Bug Fixes

- Relax typing on _fn_result_to_body to allow Any
  ([#212](https://github.com/Bluetooth-Devices/dbus-fast/pull/212),
  [`2f5fc38`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2f5fc3800702f6eb680d94de94b997ed5d8b9b77))


## v1.87.2 (2023-07-24)

### Bug Fixes

- Typing on _fn_result_to_body was incorrect which was caused an exception with cython3
  ([#210](https://github.com/Bluetooth-Devices/dbus-fast/pull/210),
  [`c40c7bc`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c40c7bcc4a8bbbce73d4d090ac840f8fe95d943e))


## v1.87.1 (2023-07-24)

### Bug Fixes

- Cython3 compat ([#208](https://github.com/Bluetooth-Devices/dbus-fast/pull/208),
  [`43b3d48`](https://github.com/Bluetooth-Devices/dbus-fast/commit/43b3d48c8934a5274e4fae9b2c65c8ce6477a65b))


## v1.87.0 (2023-07-24)

### Features

- Initial cpython 3.12 support ([#207](https://github.com/Bluetooth-Devices/dbus-fast/pull/207),
  [`c755193`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c755193ee038e4d35ad25d5d02e0a1a8cecd9d6d))


## v1.86.0 (2023-05-03)

### Chores

- Update deps via poetry ([#201](https://github.com/Bluetooth-Devices/dbus-fast/pull/201),
  [`a17d6d0`](https://github.com/Bluetooth-Devices/dbus-fast/commit/a17d6d0fd08fde630942aa7f44a8fb452c48d761))

### Features

- Improve performance of reading from the socket during unmarshall
  ([#200](https://github.com/Bluetooth-Devices/dbus-fast/pull/200),
  [`e5d355f`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e5d355ff407baf58a8e5b03c3e9ca25213a95e05))


## v1.85.0 (2023-04-21)

### Features

- Improve unmarshall performance ([#199](https://github.com/Bluetooth-Devices/dbus-fast/pull/199),
  [`3dc98be`](https://github.com/Bluetooth-Devices/dbus-fast/commit/3dc98be7e948d61cd98b326ece4bc9eef7803684))


## v1.84.2 (2023-02-20)

### Bug Fixes

- Corrects Variant documentation ([#197](https://github.com/Bluetooth-Devices/dbus-fast/pull/197),
  [`9c6a472`](https://github.com/Bluetooth-Devices/dbus-fast/commit/9c6a472100a471c8f41d495707182eca8d5d25a1))

Co-authored-by: J. Nick Koston <nick@koston.org>


## v1.84.1 (2023-02-14)

### Bug Fixes

- Missing c extensions with newer poetry
  ([#194](https://github.com/Bluetooth-Devices/dbus-fast/pull/194),
  [`72ddb15`](https://github.com/Bluetooth-Devices/dbus-fast/commit/72ddb156f0ac0fe0910ea41360f32f75a13cc7e4))

### Chores

- Bump isort to 5.12.0 to fix ci ([#195](https://github.com/Bluetooth-Devices/dbus-fast/pull/195),
  [`7b04136`](https://github.com/Bluetooth-Devices/dbus-fast/commit/7b04136822be9e2bc892c0d70d1eca40fe0634e8))

- Bump python-semantic-release to fix CI
  ([#196](https://github.com/Bluetooth-Devices/dbus-fast/pull/196),
  [`6387f82`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6387f821e012c0b43e1e0637e3a8d2311c298662))


## v1.84.0 (2023-01-07)

### Features

- Add support for EXTERNAL auth without uid
  ([#193](https://github.com/Bluetooth-Devices/dbus-fast/pull/193),
  [`4939ef8`](https://github.com/Bluetooth-Devices/dbus-fast/commit/4939ef80e523af8a08900fe78abc2f3c54ec835e))


## v1.83.1 (2022-12-24)

### Bug Fixes

- Cleanup typing in marshaller and unmarshaller
  ([#190](https://github.com/Bluetooth-Devices/dbus-fast/pull/190),
  [`830183e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/830183e1887a7abb876813098f17e22550453569))


## v1.83.0 (2022-12-23)

### Features

- Allow hardcoding uid in auth ([#189](https://github.com/Bluetooth-Devices/dbus-fast/pull/189),
  [`091c262`](https://github.com/Bluetooth-Devices/dbus-fast/commit/091c262e2747be5170596ea9e84b2cd884d01762))

Closes https://github.com/Bluetooth-Devices/dbus-fast/issues/188


## v1.82.0 (2022-12-09)

### Features

- Avoid enum dunder overhead in message_bus calls
  ([#187](https://github.com/Bluetooth-Devices/dbus-fast/pull/187),
  [`b3c7d51`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b3c7d5139d4cfa5bcea2435b6acdb6e1e059ceb4))


## v1.81.0 (2022-12-09)

### Chores

- Add passive unmarshall benchmark ([#185](https://github.com/Bluetooth-Devices/dbus-fast/pull/185),
  [`5b0d9d0`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5b0d9d024aa2e2b2378bc801607c63d6ca7b6bbe))

### Features

- Speed up processing bluez passive advertisements
  ([#186](https://github.com/Bluetooth-Devices/dbus-fast/pull/186),
  [`fb0cc35`](https://github.com/Bluetooth-Devices/dbus-fast/commit/fb0cc3584888bd307db3eb689f0dd81a025a1396))


## v1.80.0 (2022-12-09)

### Features

- Speed up checking if a message needs a reply
  ([#181](https://github.com/Bluetooth-Devices/dbus-fast/pull/181),
  [`d1366ac`](https://github.com/Bluetooth-Devices/dbus-fast/commit/d1366aca644d78f446f47b8fd607b82f73299fb8))


## v1.79.0 (2022-12-09)

### Features

- Add a cython pxd for services ([#180](https://github.com/Bluetooth-Devices/dbus-fast/pull/180),
  [`f3c9250`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f3c925079a1ea632ed850f71aaf26ba1e57f2ca8))


## v1.78.0 (2022-12-08)

### Chores

- Disable some more tests that segfault under py3.10
  ([#179](https://github.com/Bluetooth-Devices/dbus-fast/pull/179),
  [`b23086b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b23086b25ddf57580cff4b86c8adb031e6203268))

### Features

- Simplify creation of SendReply in message_bus
  ([#178](https://github.com/Bluetooth-Devices/dbus-fast/pull/178),
  [`24faa00`](https://github.com/Bluetooth-Devices/dbus-fast/commit/24faa00062237cbee83ea118e4c11f319899538f))


## v1.77.0 (2022-12-08)

### Features

- Avoid replacing unix_fds if there are no unix_fds
  ([#176](https://github.com/Bluetooth-Devices/dbus-fast/pull/176),
  [`06647d7`](https://github.com/Bluetooth-Devices/dbus-fast/commit/06647d7e49aa29b40146c7655f0edd4979a5500d))


## v1.76.0 (2022-12-08)

### Chores

- Disable flakey glib test on newer python
  ([#173](https://github.com/Bluetooth-Devices/dbus-fast/pull/173),
  [`7edfc38`](https://github.com/Bluetooth-Devices/dbus-fast/commit/7edfc38b6314337dd0cec2bf92e9e07f0dfdfeba))

- Disable one more flakey glib test on py3.10
  ([#174](https://github.com/Bluetooth-Devices/dbus-fast/pull/174),
  [`2fa7cdb`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2fa7cdb15653e8d6df079e24876419b2c896bf05))

### Features

- Only construct handlers once ([#175](https://github.com/Bluetooth-Devices/dbus-fast/pull/175),
  [`fb4d540`](https://github.com/Bluetooth-Devices/dbus-fast/commit/fb4d5402ba254e62989cbd0e36c3ad510bb0d358))


## v1.75.1 (2022-11-23)

### Bug Fixes

- Fix remaining altdesktop links ([#169](https://github.com/Bluetooth-Devices/dbus-fast/pull/169),
  [`67255f7`](https://github.com/Bluetooth-Devices/dbus-fast/commit/67255f7e01f7970e4acdd57c9a399f9452fc1d0c))

There were still a few links incorrectly pointing back to altdesktop/python-dbus-next on GitHub.


## v1.75.0 (2022-11-17)

### Features

- Add unmarshaller cython typing for SignatureType and SignatureTree
  ([#168](https://github.com/Bluetooth-Devices/dbus-fast/pull/168),
  [`98d5c5a`](https://github.com/Bluetooth-Devices/dbus-fast/commit/98d5c5aec2c800351666921c14aaa64741ca2831))


## v1.74.2 (2022-11-17)

### Bug Fixes

- Small fixes for typing with older python versions
  ([#167](https://github.com/Bluetooth-Devices/dbus-fast/pull/167),
  [`1e32f28`](https://github.com/Bluetooth-Devices/dbus-fast/commit/1e32f284cd7a15da81d278ffa9f5abe34563aafc))


## v1.74.1 (2022-11-16)

### Bug Fixes

- Building via PEP 517 ([#166](https://github.com/Bluetooth-Devices/dbus-fast/pull/166),
  [`6694fda`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6694fda49f966814ebc900a52812b4c5e4ff1980))


## v1.74.0 (2022-11-14)

### Features

- Improve cdef types for marshaller
  ([#164](https://github.com/Bluetooth-Devices/dbus-fast/pull/164),
  [`9fb4440`](https://github.com/Bluetooth-Devices/dbus-fast/commit/9fb4440b805fa5bf432fa1b23d9b1fac1de31b96))


## v1.73.1 (2022-11-14)

### Bug Fixes

- Allow non-string objects to be marshalled by write_string
  ([#163](https://github.com/Bluetooth-Devices/dbus-fast/pull/163),
  [`46f1d6b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/46f1d6bbc09860185db04c7985b9fd7c23e7a1bf))


## v1.73.0 (2022-11-11)

### Chores

- Add a test for unmarshalling a big endian message
  ([#156](https://github.com/Bluetooth-Devices/dbus-fast/pull/156),
  [`b329700`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b3297008bc3776c6220b66a0036cfdf2b636157d))

- Add big endian github workflow ([#155](https://github.com/Bluetooth-Devices/dbus-fast/pull/155),
  [`984738c`](https://github.com/Bluetooth-Devices/dbus-fast/commit/984738c8030aff5e0a614a2b398ec690d21636fb))

thanks to https://til.simonwillison.net/docker/emulate-s390x-with-qemu

- Make big endian workflow manual until we get it working properly
  ([#157](https://github.com/Bluetooth-Devices/dbus-fast/pull/157),
  [`9240bfd`](https://github.com/Bluetooth-Devices/dbus-fast/commit/9240bfda6e280bc75d8f249ba3470202a0318913))

- Prepare marshaller to be able to generate big endian messages
  ([#154](https://github.com/Bluetooth-Devices/dbus-fast/pull/154),
  [`b2327c0`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b2327c08558ba6a785064788c5fe448784d56be0))

### Features

- Reduce latency to process messages
  ([#161](https://github.com/Bluetooth-Devices/dbus-fast/pull/161),
  [`113f0c9`](https://github.com/Bluetooth-Devices/dbus-fast/commit/113f0c9a325d538592555ae89e1df1ea29398aa9))

Improve `message_bus.py` `_process_message` performance with a `pxd` file


## v1.72.0 (2022-11-04)

### Chores

- Add benchmark and tests for GetManagedObjects
  ([#150](https://github.com/Bluetooth-Devices/dbus-fast/pull/150),
  [`2d56622`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2d566224d34217cb720aacef1cc9a656f564901c))

### Features

- Add optimized reader for GetManagedObjects
  ([#152](https://github.com/Bluetooth-Devices/dbus-fast/pull/152),
  [`7ed453f`](https://github.com/Bluetooth-Devices/dbus-fast/commit/7ed453f31a654f8cc9b99eb17f872370f4b06a4e))


## v1.71.0 (2022-11-04)

### Features

- Small speed up to _unpack_variants
  ([#148](https://github.com/Bluetooth-Devices/dbus-fast/pull/148),
  [`ef7acdc`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ef7acdcbe59123bfa3b17d5dafc9f8235ac0f360))


## v1.70.0 (2022-11-04)

### Features

- Use cimports for message marshalling
  ([#149](https://github.com/Bluetooth-Devices/dbus-fast/pull/149),
  [`ef7d9d4`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ef7d9d440775cf0ddcb6b3bc6115b3884be35792))


## v1.69.0 (2022-11-04)

### Features

- Refactor message_reader to avoid python wrappers
  ([#147](https://github.com/Bluetooth-Devices/dbus-fast/pull/147),
  [`b81de45`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b81de4553fc1414476ff8a1c2b73db7b1a497841))


## v1.68.0 (2022-11-04)

### Features

- Use cimports for unmarshaller Variant and Message
  ([#146](https://github.com/Bluetooth-Devices/dbus-fast/pull/146),
  [`6418ed4`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6418ed4bb69a835768596f66ab5b514ea48b82cc))


## v1.67.0 (2022-11-03)

### Features

- Optimize unmarshaller by dropping exception that was only used internally
  ([#145](https://github.com/Bluetooth-Devices/dbus-fast/pull/145),
  [`79d52a5`](https://github.com/Bluetooth-Devices/dbus-fast/commit/79d52a50bd9651fa489e81935bda04d53285b2c1))


## v1.66.0 (2022-11-03)

### Features

- Speed up creating Variant objects
  ([#144](https://github.com/Bluetooth-Devices/dbus-fast/pull/144),
  [`2ff84e3`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2ff84e3ac56f4348c8276515ac398fcbda8a0657))


## v1.65.0 (2022-11-03)

### Features

- Add cython def for unmarshaller read_sock for fd passing
  ([#143](https://github.com/Bluetooth-Devices/dbus-fast/pull/143),
  [`f438c36`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f438c369bd86956f50fb839ec4a0a8069de7d018))


## v1.64.0 (2022-11-03)

### Features

- Speed up marshalling headers ([#142](https://github.com/Bluetooth-Devices/dbus-fast/pull/142),
  [`7d6fb63`](https://github.com/Bluetooth-Devices/dbus-fast/commit/7d6fb63dc011404955fc1219924cd2c6f6634ccd))


## v1.63.0 (2022-11-03)

### Features

- Speed up marshall align ([#137](https://github.com/Bluetooth-Devices/dbus-fast/pull/137),
  [`d7d301c`](https://github.com/Bluetooth-Devices/dbus-fast/commit/d7d301c773beb312be752accf7018a3dacecde02))

- Speed up marshall write_string and write_variant
  ([#138](https://github.com/Bluetooth-Devices/dbus-fast/pull/138),
  [`71cf524`](https://github.com/Bluetooth-Devices/dbus-fast/commit/71cf52430bd3ece01083309c5f0f5d934dca3d59))


## v1.62.0 (2022-11-03)

### Chores

- Add explicit test for workaround of python/cpython#98976
  ([#135](https://github.com/Bluetooth-Devices/dbus-fast/pull/135),
  [`b486e32`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b486e3248baf7335f133ed3e67641df9a6beb091))

- Update pyproject.toml dependencies
  ([#136](https://github.com/Bluetooth-Devices/dbus-fast/pull/136),
  [`4a23e0e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/4a23e0e0c5a1f4f52670f59433855dd87bf36371))

### Features

- Speed up marshaller by pre-packing bools
  ([#139](https://github.com/Bluetooth-Devices/dbus-fast/pull/139),
  [`c10a241`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c10a241dc5e889fd58323789dc4af45ec1e5616a))


## v1.61.1 (2022-11-01)

### Bug Fixes

- Re-release due to pypi not seeing the new version
  ([#134](https://github.com/Bluetooth-Devices/dbus-fast/pull/134),
  [`2f21ee8`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2f21ee8b8d52975624c19b6593a96976fa19047b))

### Chores

- Adjust poetry for python 3.11 ([#133](https://github.com/Bluetooth-Devices/dbus-fast/pull/133),
  [`6d7391a`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6d7391a8f865ad377e3edd2b47b42c296b267cab))


## v1.61.0 (2022-11-01)

### Chores

- Drop async-timeout dependency on Python >= 3.11
  ([#132](https://github.com/Bluetooth-Devices/dbus-fast/pull/132),
  [`1b5c9e1`](https://github.com/Bluetooth-Devices/dbus-fast/commit/1b5c9e1cb94d19925776d91196cf1b657264c494))

### Features

- Add support and workarounds for cpython3.11
  ([#31](https://github.com/Bluetooth-Devices/dbus-fast/pull/31),
  [`b53a467`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b53a4675d78f8e4e37be322ebda3eeec80f15723))


## v1.60.0 (2022-10-31)

### Features

- Speed up auth phase ([#131](https://github.com/Bluetooth-Devices/dbus-fast/pull/131),
  [`3eef636`](https://github.com/Bluetooth-Devices/dbus-fast/commit/3eef6368268c2d46db3b31bf907959da36dbf2a4))


## v1.59.2 (2022-10-31)

### Bug Fixes

- Correctly fallback to pure python when cython is missing
  ([#130](https://github.com/Bluetooth-Devices/dbus-fast/pull/130),
  [`8ab1f9d`](https://github.com/Bluetooth-Devices/dbus-fast/commit/8ab1f9d0b380293294a0f847664e0c459061c2d9))


## v1.59.1 (2022-10-29)

### Bug Fixes

- Pass return value to SendReply.__exit__
  ([#127](https://github.com/Bluetooth-Devices/dbus-fast/pull/127),
  [`f8c67ed`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f8c67ed00fa8fe58a85b6ba73b5fa5974f802004))

### Chores

- Add additional coverage for multiple messages in the same packet
  ([#126](https://github.com/Bluetooth-Devices/dbus-fast/pull/126),
  [`8f6a431`](https://github.com/Bluetooth-Devices/dbus-fast/commit/8f6a431ea49fc168adf484732af5e10debdad93f))


## v1.59.0 (2022-10-29)

### Features

- Speed up decoding headers by avoiding unicode checks
  ([#125](https://github.com/Bluetooth-Devices/dbus-fast/pull/125),
  [`6121781`](https://github.com/Bluetooth-Devices/dbus-fast/commit/61217819fbbe073007a44db69328008941d6bb4c))


## v1.58.0 (2022-10-29)

### Features

- Add optimized parser for properties changed messages with service data
  ([#124](https://github.com/Bluetooth-Devices/dbus-fast/pull/124),
  [`c8a9452`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c8a945210ae3ea8d25e4547f70b25d61b778ffe1))


## v1.57.0 (2022-10-29)

### Features

- Add optimized parser for InterfacesRemoved
  ([#123](https://github.com/Bluetooth-Devices/dbus-fast/pull/123),
  [`09822a5`](https://github.com/Bluetooth-Devices/dbus-fast/commit/09822a59ffad07b8dcb6d216d98e6dccbe338b06))


## v1.56.0 (2022-10-29)

### Features

- Optimize for interfaces added messages
  ([#122](https://github.com/Bluetooth-Devices/dbus-fast/pull/122),
  [`c05a27a`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c05a27aef9395eb688385109c4ff7204d5103dda))


## v1.55.0 (2022-10-29)

### Features

- Add optimized reader for uint16 ([#121](https://github.com/Bluetooth-Devices/dbus-fast/pull/121),
  [`52881d9`](https://github.com/Bluetooth-Devices/dbus-fast/commit/52881d9054e35ae3d727c4adafd7e0958b1c99af))


## v1.54.0 (2022-10-28)

### Features

- Speed up unmarshaller with common signature trees
  ([#120](https://github.com/Bluetooth-Devices/dbus-fast/pull/120),
  [`5b32072`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5b32072934a7269ffc7186aaaed77a0eb6872cd9))

Co-authored-by: David Lechner <david@lechnology.com>


## v1.53.0 (2022-10-28)

### Features

- Add additional pxd defs for message
  ([#118](https://github.com/Bluetooth-Devices/dbus-fast/pull/118),
  [`3eb123b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/3eb123b0366ed143d395e0609540c580398cd896))


## v1.52.0 (2022-10-28)

### Chores

- Fix ci ([#119](https://github.com/Bluetooth-Devices/dbus-fast/pull/119),
  [`3c773e1`](https://github.com/Bluetooth-Devices/dbus-fast/commit/3c773e118c78e6bc336d432eab57e36a0ed7213d))

### Features

- Small speed up to unpack_variants
  ([#117](https://github.com/Bluetooth-Devices/dbus-fast/pull/117),
  [`3c164a9`](https://github.com/Bluetooth-Devices/dbus-fast/commit/3c164a9291b9fb6e75aed0fc5aab1dfc7b79c376))


## v1.51.0 (2022-10-27)

### Features

- Inline cast uint32 and int16 to speed up unmarshall
  ([#115](https://github.com/Bluetooth-Devices/dbus-fast/pull/115),
  [`24dd9d9`](https://github.com/Bluetooth-Devices/dbus-fast/commit/24dd9d9742e8c779b9c8aa751ba8b2815b61b15b))


## v1.50.0 (2022-10-27)

### Features

- Speed up unmarshall ([#114](https://github.com/Bluetooth-Devices/dbus-fast/pull/114),
  [`e1836b2`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e1836b2034ca4bfbb004027f98b42c68f6c6edce))


## v1.49.0 (2022-10-26)

### Features

- Speed up unmarshaller ([#113](https://github.com/Bluetooth-Devices/dbus-fast/pull/113),
  [`8f7f982`](https://github.com/Bluetooth-Devices/dbus-fast/commit/8f7f982a75fe9c998e5a983090e361ba52e2e6a3))


## v1.48.0 (2022-10-20)

### Features

- Add typing to auth module ([#110](https://github.com/Bluetooth-Devices/dbus-fast/pull/110),
  [`e07e281`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e07e281ded44f9ded3002c34803f802146a9e3c9))


## v1.47.0 (2022-10-19)

### Features

- Speed up unmarshaller ([#109](https://github.com/Bluetooth-Devices/dbus-fast/pull/109),
  [`2443cf9`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2443cf99909af02db040caeeded7024a020c50a5))


## v1.46.0 (2022-10-19)

### Features

- Speed up marshaller and add typing
  ([#108](https://github.com/Bluetooth-Devices/dbus-fast/pull/108),
  [`e8f568c`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e8f568c074965bf7955f29cd89cf14f1b8dd5643))


## v1.45.0 (2022-10-13)

### Features

- Optimize signature readers for most common messages
  ([#107](https://github.com/Bluetooth-Devices/dbus-fast/pull/107),
  [`d5fb4d9`](https://github.com/Bluetooth-Devices/dbus-fast/commit/d5fb4d9c8bf17c51762ea961d745c5db7d8d8a22))


## v1.44.0 (2022-10-12)

### Features

- Speed up unpack_variants ([#105](https://github.com/Bluetooth-Devices/dbus-fast/pull/105),
  [`a4fdda2`](https://github.com/Bluetooth-Devices/dbus-fast/commit/a4fdda271f7a96e267826ffa3f268ec02078ba73))


## v1.43.0 (2022-10-12)

### Features

- Improve aio message reader performance
  ([#104](https://github.com/Bluetooth-Devices/dbus-fast/pull/104),
  [`9fa697d`](https://github.com/Bluetooth-Devices/dbus-fast/commit/9fa697da65d449b7402aa7f2f26762b0d2e175c6))


## v1.42.0 (2022-10-12)

### Features

- Complete some more missing typing
  ([#103](https://github.com/Bluetooth-Devices/dbus-fast/pull/103),
  [`5787032`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5787032af7cae1ffffd1561390cdb02053776345))


## v1.41.0 (2022-10-11)

### Features

- Add more typing to unmarshaller ([#102](https://github.com/Bluetooth-Devices/dbus-fast/pull/102),
  [`e7048fa`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e7048fa38b63ea45e819930a51ca5744f86da73f))


## v1.40.0 (2022-10-10)

### Features

- Speed up unmarshaller ([#101](https://github.com/Bluetooth-Devices/dbus-fast/pull/101),
  [`a6a248b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/a6a248b3b1dbbb06784f700b49a7fe92b30cc7b5))


## v1.39.0 (2022-10-10)

### Features

- Add additional typing ([#100](https://github.com/Bluetooth-Devices/dbus-fast/pull/100),
  [`cde1893`](https://github.com/Bluetooth-Devices/dbus-fast/commit/cde1893dca1872d8b482a145337ee3bbf47c35b4))


## v1.38.0 (2022-10-09)

### Features

- Optimize for reading a{sv} messages and headers
  ([#98](https://github.com/Bluetooth-Devices/dbus-fast/pull/98),
  [`4648d29`](https://github.com/Bluetooth-Devices/dbus-fast/commit/4648d29df4b616f49c06ca9fcbfbc27717d97135))


## v1.37.0 (2022-10-09)

### Chores

- Adjust unmarshall benchmarks since they are now fast enough to hit the margin of error
  ([#97](https://github.com/Bluetooth-Devices/dbus-fast/pull/97),
  [`0ee88e4`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0ee88e4018d4c436ffedb1a00136088606ba3977))

### Features

- Speed up empty array unmarshall ([#96](https://github.com/Bluetooth-Devices/dbus-fast/pull/96),
  [`2c6ee99`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2c6ee99b73dcfb2e2d45d2610a3fa10a4ff2136a))


## v1.36.0 (2022-10-09)

### Features

- Add cdef to unpack_variants ([#95](https://github.com/Bluetooth-Devices/dbus-fast/pull/95),
  [`dbf42c3`](https://github.com/Bluetooth-Devices/dbus-fast/commit/dbf42c370784236ff31e9324968f02a5efb58586))


## v1.35.0 (2022-10-09)

### Features

- Add unpack variants benchmark ([#94](https://github.com/Bluetooth-Devices/dbus-fast/pull/94),
  [`eb966fd`](https://github.com/Bluetooth-Devices/dbus-fast/commit/eb966fd7cf3a3f05879c29f7eb98727dd117c317))


## v1.34.0 (2022-10-09)

### Features

- Add additional typing ([#93](https://github.com/Bluetooth-Devices/dbus-fast/pull/93),
  [`7326bdf`](https://github.com/Bluetooth-Devices/dbus-fast/commit/7326bdf097310eafa21364dd46f6ebb72baa1a3d))


## v1.33.0 (2022-10-09)

### Features

- Improve performance of unmarshalling headers
  ([#88](https://github.com/Bluetooth-Devices/dbus-fast/pull/88),
  [`b6d4069`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b6d40691fd11ff8d4e46a57fd8cc97a9b6806089))


## v1.32.0 (2022-10-08)

### Features

- Speed up marshalling arrays ([#87](https://github.com/Bluetooth-Devices/dbus-fast/pull/87),
  [`f554345`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f554345b3640524300fbe406f4ac25dbf61a2274))


## v1.31.0 (2022-10-08)

### Features

- Speed up marshalling variants ([#86](https://github.com/Bluetooth-Devices/dbus-fast/pull/86),
  [`7847e26`](https://github.com/Bluetooth-Devices/dbus-fast/commit/7847e26e6e6cfe172437544d7709dc0c87a65402))


## v1.30.0 (2022-10-08)

### Features

- Speed up aligning data during marshall
  ([#85](https://github.com/Bluetooth-Devices/dbus-fast/pull/85),
  [`07e6886`](https://github.com/Bluetooth-Devices/dbus-fast/commit/07e68862d93cd5dc470ad2a3ae6f8eaf12808271))


## v1.29.1 (2022-10-07)

### Bug Fixes

- Remove unused unmarshaller code ([#83](https://github.com/Bluetooth-Devices/dbus-fast/pull/83),
  [`3613ff8`](https://github.com/Bluetooth-Devices/dbus-fast/commit/3613ff846b8bb66000c65c778bb06596cd643b22))


## v1.29.0 (2022-10-07)

### Features

- Unpack header names as message kwargs
  ([#82](https://github.com/Bluetooth-Devices/dbus-fast/pull/82),
  [`7398a3f`](https://github.com/Bluetooth-Devices/dbus-fast/commit/7398a3fc4726fa20b34840967a6c3777eef12f52))


## v1.28.1 (2022-10-07)

### Bug Fixes

- Disconnect race in tests ([#79](https://github.com/Bluetooth-Devices/dbus-fast/pull/79),
  [`f2bb106`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f2bb10680a5d4e363ff8e7762fef25ec75ef8b14))


## v1.28.0 (2022-10-07)

### Features

- Speed up unmarshalling int16 types ([#81](https://github.com/Bluetooth-Devices/dbus-fast/pull/81),
  [`18213c0`](https://github.com/Bluetooth-Devices/dbus-fast/commit/18213c0a00f162cbf74fa7fc0bbcf12c1109c347))


## v1.27.0 (2022-10-07)

### Features

- Cythonize headers in unmarshaller ([#80](https://github.com/Bluetooth-Devices/dbus-fast/pull/80),
  [`ae96be7`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ae96be70f5e960d3feb726b7c769dff26b41c428))


## v1.26.0 (2022-10-06)

### Bug Fixes

- Incorrect pxd typing for for _marshall
  ([#75](https://github.com/Bluetooth-Devices/dbus-fast/pull/75),
  [`cf1f012`](https://github.com/Bluetooth-Devices/dbus-fast/commit/cf1f0129baaac48d6a4804e8c6a0af5bc7ef8d16))

### Features

- Add cython defs for Variant class ([#74](https://github.com/Bluetooth-Devices/dbus-fast/pull/74),
  [`cd08f06`](https://github.com/Bluetooth-Devices/dbus-fast/commit/cd08f063cc352c65d2330cbe09ca72a367c58806))


## v1.25.0 (2022-10-05)

### Features

- Add cython extension for messages ([#73](https://github.com/Bluetooth-Devices/dbus-fast/pull/73),
  [`8676f12`](https://github.com/Bluetooth-Devices/dbus-fast/commit/8676f12a7e040d7c3f20584739a74ad1074a4717))


## v1.24.0 (2022-10-04)

### Features

- Add cython extension for signature ([#72](https://github.com/Bluetooth-Devices/dbus-fast/pull/72),
  [`0ad8801`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0ad8801215093cdbf0f62fce5b953d9b01e9d524))


## v1.23.0 (2022-10-04)

### Features

- Speed up unmarshall performance ([#71](https://github.com/Bluetooth-Devices/dbus-fast/pull/71),
  [`f38e08f`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f38e08fa7cc8d41e896663ab0f163aa37a472abe))


## v1.22.0 (2022-10-03)

### Features

- Speed up message bus matching ([#70](https://github.com/Bluetooth-Devices/dbus-fast/pull/70),
  [`cccfea3`](https://github.com/Bluetooth-Devices/dbus-fast/commit/cccfea30b9ec5417eecef5093ee02f7b7a254c45))


## v1.21.17 (2022-10-02)

### Bug Fixes

- Install python-semantic-release in wheel workflow
  ([#68](https://github.com/Bluetooth-Devices/dbus-fast/pull/68),
  [`cca0d6e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/cca0d6e98a5934fee83ccafbd2ed47cf60a3ce99))


## v1.21.16 (2022-10-02)

### Bug Fixes

- Ensure we can get the latest version in the wheels build process
  ([#67](https://github.com/Bluetooth-Devices/dbus-fast/pull/67),
  [`ecd5a70`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ecd5a7036945ccdd79e3049a7f2904709544af51))


## v1.21.15 (2022-10-02)

### Bug Fixes

- Checkout main for wheels ([#66](https://github.com/Bluetooth-Devices/dbus-fast/pull/66),
  [`3051a93`](https://github.com/Bluetooth-Devices/dbus-fast/commit/3051a9322cc711cee24583dedf25cee31a31c3b3))


## v1.21.14 (2022-10-02)

### Bug Fixes

- Use semantic-release to find the latest tag for wheels
  ([#65](https://github.com/Bluetooth-Devices/dbus-fast/pull/65),
  [`b76eb97`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b76eb97188c204996d049d326b4d21c74bc3f325))


## v1.21.13 (2022-10-02)

### Bug Fixes

- Build wheels from the sha saved after release
  ([#64](https://github.com/Bluetooth-Devices/dbus-fast/pull/64),
  [`faee181`](https://github.com/Bluetooth-Devices/dbus-fast/commit/faee18172bb7bc72ade8a54f2a8bd0fae5e35018))


## v1.21.12 (2022-10-02)

### Bug Fixes

- Switch to on create instead of push
  ([#63](https://github.com/Bluetooth-Devices/dbus-fast/pull/63),
  [`af0ed88`](https://github.com/Bluetooth-Devices/dbus-fast/commit/af0ed889985425b33fbbe35e8c8a4d0427643367))


## v1.21.11 (2022-10-02)

### Bug Fixes

- Accept any tag to build wheels ([#62](https://github.com/Bluetooth-Devices/dbus-fast/pull/62),
  [`60fca54`](https://github.com/Bluetooth-Devices/dbus-fast/commit/60fca54d2a4da67e3211b9e3f421787154234041))


## v1.21.10 (2022-10-02)

### Bug Fixes

- Github action tag matching ([#61](https://github.com/Bluetooth-Devices/dbus-fast/pull/61),
  [`b95d0b8`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b95d0b8ce63e03c972fef72354cd67c2062bea94))


## v1.21.9 (2022-10-02)

### Bug Fixes

- Build wheels on tag instead ([#60](https://github.com/Bluetooth-Devices/dbus-fast/pull/60),
  [`6166896`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6166896c49a1358c951057fcc73d4b91ac92e08b))


## v1.21.8 (2022-10-02)

### Bug Fixes

- Publish wheels when release happens
  ([#59](https://github.com/Bluetooth-Devices/dbus-fast/pull/59),
  [`45e8ac0`](https://github.com/Bluetooth-Devices/dbus-fast/commit/45e8ac00c6473c5329b36d4f19f5eb846db19d31))


## v1.21.7 (2022-10-02)

### Bug Fixes

- Seperate wheels back out so it builds after
  ([#58](https://github.com/Bluetooth-Devices/dbus-fast/pull/58),
  [`c74c251`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c74c2519a12a0f9cbb8c1b12b8871df22dda047d))


## v1.21.6 (2022-10-02)

### Bug Fixes

- Language_level warning when running cythonize
  ([#57](https://github.com/Bluetooth-Devices/dbus-fast/pull/57),
  [`b7b441e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b7b441eeef8bfa1dc286c78435ff9bac9d072302))


## v1.21.5 (2022-10-02)

### Bug Fixes

- Cython build of unpack ([#56](https://github.com/Bluetooth-Devices/dbus-fast/pull/56),
  [`5df01ac`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5df01ac1ba3dc0515ffa8d0b01c1d386ef726e91))


## v1.21.4 (2022-10-02)

### Bug Fixes

- Increase verbosity of wheel builds ([#55](https://github.com/Bluetooth-Devices/dbus-fast/pull/55),
  [`4779e7b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/4779e7b825270268ae28b5fc1c4ddb45647c31c5))


## v1.21.3 (2022-10-02)

### Bug Fixes

- Make wheel build depend on release success
  ([#54](https://github.com/Bluetooth-Devices/dbus-fast/pull/54),
  [`49d98d0`](https://github.com/Bluetooth-Devices/dbus-fast/commit/49d98d01c2a3736adcc5d088fdd447c45b9503de))


## v1.21.2 (2022-10-02)

### Bug Fixes

- Additional tweaks to publishing wheels
  ([#53](https://github.com/Bluetooth-Devices/dbus-fast/pull/53),
  [`05b9453`](https://github.com/Bluetooth-Devices/dbus-fast/commit/05b945317380ad3d50b2f9d9114a61a2c57d99f0))


## v1.21.1 (2022-10-02)

### Bug Fixes

- Wheel builds on released ([#52](https://github.com/Bluetooth-Devices/dbus-fast/pull/52),
  [`6259fb2`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6259fb299722688ca19a41a61a7a783e9abdca8c))


## v1.21.0 (2022-10-02)

### Chores

- Add cibuildwheel action ([#50](https://github.com/Bluetooth-Devices/dbus-fast/pull/50),
  [`f6e4c3c`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f6e4c3c8aef5af04645a8249c27b9e51cfd5ad01))

### Features

- Cythonize unpack_variants ([#51](https://github.com/Bluetooth-Devices/dbus-fast/pull/51),
  [`1587211`](https://github.com/Bluetooth-Devices/dbus-fast/commit/158721123fc56675f04b9081ef4107590a8c2b17))


## v1.20.0 (2022-10-02)

### Bug Fixes

- Add missing closes to tests ([#49](https://github.com/Bluetooth-Devices/dbus-fast/pull/49),
  [`d2ce4a1`](https://github.com/Bluetooth-Devices/dbus-fast/commit/d2ce4a18462b5e304bc75983be3fffa3c426affc))

### Features

- Add additional cython types to the unmarshaller
  ([#45](https://github.com/Bluetooth-Devices/dbus-fast/pull/45),
  [`0f279a5`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0f279a5ea9cd440fdbdd7dbafc1a48b1cc3577d7))


## v1.19.0 (2022-10-02)

### Features

- Add additional cython types to marshaller
  ([#48](https://github.com/Bluetooth-Devices/dbus-fast/pull/48),
  [`ddba96a`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ddba96a73107644e31af591d8b726472a7deb85b))


## v1.18.0 (2022-10-01)

### Features

- Add optional cython extension ([#44](https://github.com/Bluetooth-Devices/dbus-fast/pull/44),
  [`b737574`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b737574cf04f5c6b6f881fbdce2663119a6dc404))


## v1.17.0 (2022-09-27)

### Features

- Improve unmarshaller performance ([#43](https://github.com/Bluetooth-Devices/dbus-fast/pull/43),
  [`c4b4a03`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c4b4a038f8822b6be7b062184b8092b6249878bc))


## v1.16.0 (2022-09-27)

### Features

- Add benchmark for bluez properties messages
  ([#42](https://github.com/Bluetooth-Devices/dbus-fast/pull/42),
  [`076c5df`](https://github.com/Bluetooth-Devices/dbus-fast/commit/076c5df825221901d1565e45f8662d7d9009ffe9))


## v1.15.3 (2022-09-27)

### Bug Fixes

- Improve typing on proxy_object ([#41](https://github.com/Bluetooth-Devices/dbus-fast/pull/41),
  [`ac955b5`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ac955b50ea2921b114f6a89c2e1d3fbf34698deb))


## v1.15.2 (2022-09-27)

### Bug Fixes

- More typing fixes ([#40](https://github.com/Bluetooth-Devices/dbus-fast/pull/40),
  [`a6b9581`](https://github.com/Bluetooth-Devices/dbus-fast/commit/a6b9581d6228bf2cb4b93531677acc959e2d4dd1))


## v1.15.1 (2022-09-26)

### Bug Fixes

- Loosen async-timeout pin to 3.0.0 ([#39](https://github.com/Bluetooth-Devices/dbus-fast/pull/39),
  [`93b9a0a`](https://github.com/Bluetooth-Devices/dbus-fast/commit/93b9a0a6ca91adb6c64d9316bd977a359c3be007))


## v1.15.0 (2022-09-26)

### Features

- Use async_timeout instead of asyncio.wait_for
  ([#38](https://github.com/Bluetooth-Devices/dbus-fast/pull/38),
  [`cb31780`](https://github.com/Bluetooth-Devices/dbus-fast/commit/cb317802d654bbff7b09233b4cce6188179f1d45))


## v1.14.0 (2022-09-25)

### Features

- Speed up unmarshaller read_array ([#37](https://github.com/Bluetooth-Devices/dbus-fast/pull/37),
  [`18ea18d`](https://github.com/Bluetooth-Devices/dbus-fast/commit/18ea18d7d224764b7f529cb6238ac524f0bd8318))


## v1.13.0 (2022-09-24)

### Features

- Improve unmarshall performance ([#35](https://github.com/Bluetooth-Devices/dbus-fast/pull/35),
  [`db436b7`](https://github.com/Bluetooth-Devices/dbus-fast/commit/db436b7a10a38438a9a7f50349ddb41b112c3312))


## v1.12.0 (2022-09-24)

### Features

- Speed up unmarshall ([#34](https://github.com/Bluetooth-Devices/dbus-fast/pull/34),
  [`5a1e26f`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5a1e26f4302ed1ff3a4582e6710e2c5f99cb4a32))


## v1.11.0 (2022-09-24)

### Features

- Speed up marshalling ([#32](https://github.com/Bluetooth-Devices/dbus-fast/pull/32),
  [`afcf5fe`](https://github.com/Bluetooth-Devices/dbus-fast/commit/afcf5fe1d9c1c4a632edc60b5d48d8af32d13159))


## v1.10.0 (2022-09-24)

### Features

- Improve writer performance with a deque
  ([#30](https://github.com/Bluetooth-Devices/dbus-fast/pull/30),
  [`09af56e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/09af56e14397d9bdf183239c30683c76b7e34801))


## v1.9.0 (2022-09-24)

### Features

- Improve asyncio write performance ([#29](https://github.com/Bluetooth-Devices/dbus-fast/pull/29),
  [`016e71e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/016e71ef6d7de4d9295f3ca170d7352ae233d74a))


## v1.8.0 (2022-09-24)

### Features

- Small speed ups to unmarshall message creation
  ([#27](https://github.com/Bluetooth-Devices/dbus-fast/pull/27),
  [`0bce72a`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0bce72a76a6af0d7b3c731e08393652747e6c53a))


## v1.7.0 (2022-09-21)

### Features

- Handle kwargs in signal callback ([#26](https://github.com/Bluetooth-Devices/dbus-fast/pull/26),
  [`2e8076b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2e8076b14abf297b83eb2c81b0cacff405845d95))


## v1.6.0 (2022-09-20)

### Bug Fixes

- Disconnect connected buses at end of tests
  ([#25](https://github.com/Bluetooth-Devices/dbus-fast/pull/25),
  [`e438890`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e43889091bf7b21f6ffd27544d74cc1d57db22d2))

### Features

- Add unpack variants option ([#20](https://github.com/Bluetooth-Devices/dbus-fast/pull/20),
  [`cfad28b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/cfad28bd2ba8dccf4c3a591461bb666871e4cbba))


## v1.5.1 (2022-09-20)

### Bug Fixes

- Marshall boolean correctly ([#23](https://github.com/Bluetooth-Devices/dbus-fast/pull/23),
  [`ca2a3c1`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ca2a3c1aa86f1f0b6372929f099e8594dab2697f))


## v1.5.0 (2022-09-19)

### Chores

- Run gi tests in the CI ([#21](https://github.com/Bluetooth-Devices/dbus-fast/pull/21),
  [`f4d173e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f4d173e0426990cd0b8b1b813949cd5027684102))

### Features

- Allow varargs callback for signals ([#22](https://github.com/Bluetooth-Devices/dbus-fast/pull/22),
  [`a3379c7`](https://github.com/Bluetooth-Devices/dbus-fast/commit/a3379c74ad8f8da1eb15b6cd941d9bea6867b5f9))


## v1.4.0 (2022-09-10)

### Features

- Improve unmarshalling performance ([#18](https://github.com/Bluetooth-Devices/dbus-fast/pull/18),
  [`4362b93`](https://github.com/Bluetooth-Devices/dbus-fast/commit/4362b93fc84406adfa026b6573bc076327c71c5b))


## v1.3.0 (2022-09-09)

### Features

- Improve callback performance ([#16](https://github.com/Bluetooth-Devices/dbus-fast/pull/16),
  [`aee3da9`](https://github.com/Bluetooth-Devices/dbus-fast/commit/aee3da9f20c36cf6379d1e69e63f33a88592f6fd))


## v1.2.0 (2022-09-09)

### Chores

- Add marshall benchmark ([#14](https://github.com/Bluetooth-Devices/dbus-fast/pull/14),
  [`e386e22`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e386e228c54914b0a1f8babe3659ea5629a3cb7d))

### Features

- Improve Marshaller performance ([#15](https://github.com/Bluetooth-Devices/dbus-fast/pull/15),
  [`a9e8866`](https://github.com/Bluetooth-Devices/dbus-fast/commit/a9e8866c2a6a97227ff5f001cae5e2196260379c))


## v1.1.9 (2022-09-09)

### Bug Fixes

- Readme ([#13](https://github.com/Bluetooth-Devices/dbus-fast/pull/13),
  [`6bc87e0`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6bc87e0f0717d4a4382e4bb36d064e22ff131751))


## v1.1.8 (2022-09-09)

### Bug Fixes

- Ensure the underlying socket is closed on disconnect
  ([#12](https://github.com/Bluetooth-Devices/dbus-fast/pull/12),
  [`6770a65`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6770a656bdddf6e090ebb6858bd046e4365ea32e))


## v1.1.7 (2022-09-09)

### Bug Fixes

- Copyrights in docs ([#10](https://github.com/Bluetooth-Devices/dbus-fast/pull/10),
  [`a97701e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/a97701ec12e4049884af33abbde2b208c4e351d4))


## v1.1.6 (2022-09-09)

### Bug Fixes

- Docs deps not needed for production ([#9](https://github.com/Bluetooth-Devices/dbus-fast/pull/9),
  [`01f8ce7`](https://github.com/Bluetooth-Devices/dbus-fast/commit/01f8ce77b945554f27723755caab550b6f246cb4))


## v1.1.5 (2022-09-09)

### Bug Fixes

- Readme ([#8](https://github.com/Bluetooth-Devices/dbus-fast/pull/8),
  [`7396b5f`](https://github.com/Bluetooth-Devices/dbus-fast/commit/7396b5f475e4b9299cf96930153a01425bb5bd3b))


## v1.1.4 (2022-09-09)

### Bug Fixes

- More rename ([#7](https://github.com/Bluetooth-Devices/dbus-fast/pull/7),
  [`116d5c6`](https://github.com/Bluetooth-Devices/dbus-fast/commit/116d5c6feb863deff95f811d79199b09c79552f9))


## v1.1.3 (2022-09-09)

### Bug Fixes

- Docs ([#6](https://github.com/Bluetooth-Devices/dbus-fast/pull/6),
  [`ee473c0`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ee473c05c5ff1ecc91f0c0167987e970eebf4c75))


## v1.1.2 (2022-09-09)

### Bug Fixes

- Docs ([#4](https://github.com/Bluetooth-Devices/dbus-fast/pull/4),
  [`ba8e5f1`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ba8e5f127f2a4e20254a8d652165c348d0b9884f))

- Readme ([#5](https://github.com/Bluetooth-Devices/dbus-fast/pull/5),
  [`f628e87`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f628e87a1b859966dac03143a7a14422ef0d79a1))


## v1.1.1 (2022-09-09)

### Bug Fixes

- Docs lang ([#3](https://github.com/Bluetooth-Devices/dbus-fast/pull/3),
  [`538db98`](https://github.com/Bluetooth-Devices/dbus-fast/commit/538db98a3b7246e5d3ace256ac3b86c3dae5b63e))


## v1.1.0 (2022-09-09)

### Chores

- Build fixes
  ([`4927a1e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/4927a1e79908dfc91b804475c80a59f13ded5c04))

- Ci fixes
  ([`fad09d6`](https://github.com/Bluetooth-Devices/dbus-fast/commit/fad09d60a8aea05efe1cf584da6c1b858227f272))

- Disable some linters
  ([`0ab9fab`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0ab9fabe2fddec729dcac1bee1b2f671f6c3b539))

- Fix ci
  ([`d187573`](https://github.com/Bluetooth-Devices/dbus-fast/commit/d18757378bb55112a0f39c4c6a8b86c29b60574e))

- Fix ci
  ([`988ff05`](https://github.com/Bluetooth-Devices/dbus-fast/commit/988ff0599454ac65e192bbbef6f61534c14bf346))

- Fix ci
  ([`6e10c51`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6e10c51d88b46e80fc9b10b082b5888167f9670b))

- Fix ci
  ([`2a2d486`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2a2d486494bde0001891f71821f588c8a25d9c4c))

- Fix ci
  ([`61e00c1`](https://github.com/Bluetooth-Devices/dbus-fast/commit/61e00c1c0782288d1a12cefe784c4b860fd260d8))

- Initial commit
  ([`169581f`](https://github.com/Bluetooth-Devices/dbus-fast/commit/169581f69121ef66a326fd100656756aee1baed9))

- Initial port
  ([`495bfac`](https://github.com/Bluetooth-Devices/dbus-fast/commit/495bfac17fd7e56d292ddfde42e7e6570e04ab01))

- Rename
  ([`60308e0`](https://github.com/Bluetooth-Devices/dbus-fast/commit/60308e0b0cb14e7a26631f632123db16e4cb09c0))

- Rename
  ([`36b08af`](https://github.com/Bluetooth-Devices/dbus-fast/commit/36b08afbff9ead520ec237f7259354185e513a0d))

- Rename
  ([`7e9609b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/7e9609b0f5f95ba9e146bd73242de4e2fe5ad124))

### Features

- Speed up unmarshaller ([#1](https://github.com/Bluetooth-Devices/dbus-fast/pull/1),
  [`eca1d31`](https://github.com/Bluetooth-Devices/dbus-fast/commit/eca1d317818d2b938ec3ed3172b1be76a44a93a4))
