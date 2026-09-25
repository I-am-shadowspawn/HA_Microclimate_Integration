# Contributing

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

Discuss substantial changes in a GitHub issue before opening a pull request. Include the affected controller model, firmware, expected behaviour and evidence. New pin meanings must have controller/capture evidence; preserve unknowns rather than guessing. Keep credentials and unredacted captures out of issues, commits and pull requests.

Contributions must be your own or carry compatible redistribution rights and attribution. Contributions to this project are provided under its MIT licence; retain existing third-party notices. Do not add vendor artwork without documented permission.

Use Python 3.14.7 and the environments in [README-TESTING.md](README-TESTING.md). From the repository root:

```sh
python3.14 scripts/test_matrix.py --install --ha 2026.9.3
python3.14 scripts/test_matrix.py --release-gate --ha 2026.9.3
cd frontend
npm ci
npm run typecheck
npm run lint
npm test
npm run build
npx playwright install chromium
npm run test:e2e
```

The automated harness mocks device calls. Never use real tokens in automated tests or make unattended live writes. For hardware tests, record model/firmware, before/after observations and persistence separately from simulated test results. See [CARD-VALIDATION.md](docs/CARD-VALIDATION.md).

Keep changes focused, include meaningful regressions, update usage documentation and report commands/results in the pull request. Preserve one coordinator, explicit Save/Cancel, validated writes and partial-failure reporting. Run the HACS/hassfest workflow after uploading changes; a passing local JSON check is not a substitute.

Report security issues privately as described in [SECURITY.md](SECURITY.md).
