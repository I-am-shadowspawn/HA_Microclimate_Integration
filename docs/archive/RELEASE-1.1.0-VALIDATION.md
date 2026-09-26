# 1.1.0 validation — 24 September 2026

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

All offline implementation gates passed. No physical controller writes or live HA deployment were performed.

| HA | Python | Regression | Release gate | Line coverage |
|---|---|---|---|---|
| 2026.9.2 | 3.14.7 | 601 passed | 601 passed | 97.24% |
| 2026.9.3 | 3.14.7 | 601 passed | 601 passed | 97.24% |

No skipped or expected-failure tests. Dependency checks passed for both pinned environments. Tests block network sockets and use Home Assistant's real in-process setup/service/entity fixtures. Production Python syntax and English translation parity were checked. No separate type-checker or linter is configured in this workspace.

Coverage includes all original observation/config/lifecycle regressions and 134 added write tests: allowlist/pins, boundaries, captured date/time encoding, every field dispatch/readback for each model, empty acknowledgement, errors/oversize/redirect/credential handling, no-op/delayed/mismatched/uncertain outcomes, authentication, queue/options/token races, lock order, independent entries, cancellation/deadlines, startup/unload failures, metric/US controls and diagnostic defaults.

The source diff was reviewed against the preserved 1.0.9 development archive (the workspace copy has no Git metadata). Read-only IDs remain unchanged. The original repository was not edited. Generation counters were replaced by an I/O lock spanning refresh publication and writes, with both arrival orders tested. Responses are bounded to 1 MiB for reads and 64 KiB for updates.

Build commands and dependency pins are in README-TESTING.md. The builder compiles sources and validates archive contents. Final delivery additionally verifies two-build byte reproducibility, archive integrity and application of the full source patch to the 1.0.9 development baseline. Versioned checksums and microclimate-1.1.0-test-results.json accompany the artifacts.

Remaining validation is hardware/operational: complete model/firmware write/display/persistence checks, real UI acceptance and soak. The two captured successful v20/v32 writes do not establish universal physical behavior. See TODO.md and WRITE-CONTROLS.md. Constant target, ramps, periodic intervals/durations and batch editing are explicitly outside this release.
