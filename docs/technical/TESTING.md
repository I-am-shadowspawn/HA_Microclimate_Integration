# Tests and release packaging

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

All Python tests live under `tests/`; the CI test matrix discovers and runs this one directory. Shared Home Assistant setup is in `tests/conftest.py`, and test data builders/projections are in `tests/helpers.py`, so tests do not import helpers from one another. The JSON protocol and validation fixtures remain in the repository-root `fixtures/` directory because both backend and frontend contract tests consume them. The release builder includes only the reviewed fixture allowlist in the development archive; fixtures and release evidence stay outside the installed runtime component.

The test harness runs Home Assistant in process with mocked HTTP. It needs no running HA server or controller token. The supported minimum is **Home Assistant Core 2026.9.3**. The 2026.9.2 lockfile is retained as historical evidence, not a supported CI target.

The shared Python/TypeScript [validation contract](VALIDATION-CONTRACT.md) records observation/edit boundaries and the fixture-driven parity tests.

Runtime ownership, resource bounds and the retained HA hook are documented in [runtime lifecycle](RUNTIME-LIFECYCLE.md).

## Public identity and upgrade contract

The disposable pre-1.3.0 prototype required a one-time clean install. The public baseline is the compact release series, with v1.4.5-delta2 used as the frozen comparison for the V2-11 regression. The config entry schema remains version 1. The token's SHA-256 digest is the entry's unique ID for duplicate detection, while Home Assistant's persistent `entry_id` anchors the root device, channel devices, entity unique IDs and card device selections. Rotating the token changes the digest but must retain the entry ID. A normal release installation or rollback within this schema does not recreate the entry or require a migration.

`tests/test_public_upgrade_contract.py` checks the baseline identifier forms from that tagged candidate against the current runtime, then exercises a loaded entry through reload, rename/token reconfiguration, reauthentication and another reload. It checks customized entity/device registry rows and both saved root/channel card device IDs after each step. The test uses one installed code version and mocked cloud traffic. Separately, the maintainer reported a manual upgrade and rollback between v1.4.5 and v1.4.5-delta2 on 27 September 2026: controller/channel devices, entity IDs and saved card selections remained intact in both directions. Earlier HACS upgrades through release 1.3.2 also retained existing cards. V2-06 adds two successful UI/YAML uninstall/reinstall cycles, explicit resource instructions and a browser double-load regression; fresh reinstalls create new IDs and do not attach old history to them.

For future release checks, back up HA, record one root and one channel device ID, their entity registry IDs (including a renamed entity and a disabled diagnostic), and both cards' saved `device_id` values. Upgrade without deleting the config entry, then compare those records and confirm both cards load. If rollback is exercised, restore the earlier release through the supported install method, restart HA and refresh the browser resource before comparing again. Record both integration versions, HA Core version, card resource URLs and outcomes without publishing tokens or private controller data. A missing card after upgrade may be a stale frontend resource rather than a registry migration; check the resource before changing the config entry.

## Reproduce the CI checks

Use Python **3.14.x**, [uv](https://docs.astral.sh/uv/) 0.6.1, Node.js **24.21.0** and npm. GitHub CI pins Python 3.14.7 and installs the locked HA 2026.9.3 environment. uv uses its normal cache unless you set `UV_CACHE_DIR` yourself.

```sh
python3.14 scripts/test_matrix.py --install --release-gate --ha 2026.9.3
uvx --from ruff==0.16.9 ruff check scripts/build_release.py scripts/test_matrix.py tests/test_release_package.py
uvx --from ruff==0.16.9 ruff format --check scripts/build_release.py scripts/test_matrix.py tests/test_release_package.py
cd frontend
npm ci
npm run typecheck
npm run lint
npm test
npm run build
npx playwright install --with-deps chromium firefox webkit
npm run test:e2e
cd ..
git diff --exit-code -- custom_components/microclimate_integration/frontend/microclimate-cards.js custom_components/microclimate_integration/frontend/THIRD_PARTY_NOTICES.txt
python3.14 -m unittest tests.test_release_package -q
python3.14 scripts/build_release.py --output dist
```

The frontend build check proves the committed browser bundle and bundled dependency notices match the source and lockfile. Browser tests run in Chromium, Firefox and WebKit against a local HTTP server on port 8767; no running Home Assistant is needed. The tests include malformed WebSocket data, stale replies, local-only edits, focus after Multi changes, keyboard input and mobile-size touch behavior. WebKit's Linux binaries require the Playwright supported system libraries; CI installs them on Ubuntu. The builder itself uses only the Python standard library and does not run npm. Test output is under `results/matrix/` and is not packaged.

## What the archives contain

`microclimate-<version>-install.zip` is a **manual config-root archive**: extract its `custom_components/microclimate_integration` directory into the Home Assistant config directory. It contains the compiled card JavaScript, brand icon, MIT licence and bundled third-party notices. It needs no Node/npm installation at runtime.

`microclimate-<version>-development.zip` includes the runtime component plus source, tests, reviewed/sanitized fixtures, lockfiles, docs, HACS metadata and CI files. New captures must be reviewed and explicitly added to the public fixture list in `scripts/build_release.py`. Caches, virtual environments, local results, unreviewed captures and credential files are excluded. `SHA256SUMS` covers both archives.

The archives use stable paths, ordering, timestamps and file permissions. The package test checks byte-for-byte repeatability and clean extraction. The normal HACS integration installation uses the repository's `custom_components/microclimate_integration` folder; `hacs.json` does **not** enable `zip_release`. Do not select the config-root manual ZIP as a HACS release ZIP without a separately tested layout.

The GitHub workflow gates its package artifact on hassfest, HACS, Python, frontend and browser checks. Pushing a `v<manifest version>` tag after review runs the same gates; only a matching tag can create a GitHub Release from the checked artifacts. A tag push is the release action, so do not create one merely to test CI. HACS installation/update on a live HA instance is tracked separately in V2-07.
