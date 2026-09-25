# Tests and release packaging

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

The minimal environment runs Home Assistant's test fixtures in process, without a running HA server, frontend, live controller or API token.

## Reproduce tests

Use Python **3.14.7** and uv. The two complete dependency lock files are:

- `requirements/ha-2026.9.2.txt` — HA 2026.9.2, pytest-homeassistant-custom-component 0.13.365.
- `requirements/ha-2026.9.3.txt` — HA 2026.9.3, plugin 0.13.366.

```bash
python3.14 scripts/test_matrix.py --install
python3.14 scripts/test_matrix.py --release-gate
```

The first command creates isolated environments, checks dependencies and runs regressions. Dependency installation needs network access; pytest blocks network sockets and mocks HTTP. The second runs the acceptance gate without treating known defects as expected failures. Use `--ha 2026.9.3` to select one row.

Candidate 1.1.1 validation is recorded in docs/RELEASE-1.1.1-VALIDATION.md; the suite contains 645 tests, with network sockets blocked. Results and coverage are written to `results/matrix/`. Supplied sanitized read captures cover all three model profiles; two additional write captures prove the recorded v20/v32 round trips only; synthetic tests are labeled separately. Outstanding hardware evidence is listed in TODO.md.

## Build packages

```bash
python3.14 scripts/build_release.py --output dist
```

The builder uses only Python's standard library. It validates the component manifest, compiles Python source without writing bytecode, and creates:

- `microclimate-1.1.1-install.zip`: only the installable `custom_components/microclimate_integration` tree.
- `microclimate-1.1.1-development.zip`: integration, README/TODO/changelog, tests, fixtures, pinned requirements and scripts.
- `SHA256SUMS`: checksums for both archives.

Files are selected from explicit directories. Virtual environments, caches, bytecode, source-baseline records, runtime results/logs and previous archives are excluded. ZIP paths, ordering, timestamps and permissions are fixed, so identical inputs generate identical archive bytes. No code is downloaded or deployed by the builder. The development archive can recreate both packages and the test results.

On this Codex workspace, the existing `outputs/microclimate-test-matrix.sh` wrapper also runs the test matrix. That absolute workspace wrapper is not required by portable bundles.
