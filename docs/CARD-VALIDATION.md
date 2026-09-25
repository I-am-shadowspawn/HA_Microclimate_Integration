# Current release

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

See [1.3.0 compact-refactor validation](RELEASE-1.3.0-VALIDATION.md). Earlier reports below are historical.

# Current release: 1.2.1

See [1.2.1 fixes and validation](RELEASE-1.2.1-VALIDATION.md) for the input/HTTP correction and its focused test results. The following 1.2.0 evidence is retained as the implementation baseline.

# Microclimate 1.2.0 — card validation

Software validation completed on 24 September 2026. No live controller requests, deployments, or edits to the original source repository were performed.

| Check | Result |
|---|---|
| HA 2026.9.2 / Python 3.14.7 — regression | 683 passed, no skips/failures |
| HA 2026.9.3 / Python 3.14.7 — regression | 683 passed, no skips/failures |
| HA 2026.9.2 — release gate | 683 passed, no skips/failures |
| HA 2026.9.3 — release gate | 683 passed, no skips/failures |
| Python line coverage | 96% (rounded) |
| TypeScript strict check, ESLint, production build | Passed |
| Frontend model/unit cases | 17 passed |
| Chromium browser cases | 33 passed |

The Python suite includes all 645 previous cases and 38 card-specific cases. Tests cover complete insertion/deletion position matrices, exact destinations, invalid inputs, partial failure/no retry, request deduplication/expiry, registry renaming/disable, ACL, live settings conflict, unload during the second pin, reload rebinding, real authenticated HA WebSocket save/status/recovery and local static resource loading. Network writes use mocks; no credentials are used.

Browser coverage includes local drafts/Cancel, one final clock Save after several input changes, prefix editing/minimum/capacity, root vs channel roles, four seasonal rows, keyboard and pointer edits, polling conflicts, partial results, read-only/profile restrictions, modes, °F, schema mismatch, lost acknowledgement lookup, device-switch draft protection, repair states and initial enum selection. Responsive screenshots cover 320/390/768/1280 widths, light/dark, and the supported views. Mobile seasonal and Multi edit screenshots were visually inspected; visual review found and fixed incorrect initial select presentation. Additional editor/readonly checks fixed an ambiguous device-picker label and unstable read-only point numbering/selection. Invalid Multi tables now show incomplete timeline state instead of a sorted valid-looking preview.

The module is bundled locally with Lit license notices. The development ZIP includes the npm lockfile, sources, fixtures and test/build configuration; node_modules and test caches are excluded. The extracted source is rebuilt offline during artifact verification; final bundle comparison and archive hashes are recorded in the release implementation report.

## Remaining external acceptance

- Test controller-backed Multi insertion/deletion, zero-tail behavior, transient time/target effects and persistence on each model/firmware in an explicitly authorized hardware session.
- Install the resource in the user's HA dashboard and confirm actual browser/theme/mobile behavior and restricted-user usage. Chromium is automated here; Firefox/WebKit were not separately run.
- Constant target and Periodic interval/duration writes remain outside this mapped contract.

These are external acceptance/future mapping items, not hidden unfinished card implementation. The single-pin vendor API cannot provide atomic Save or eliminate races with an external application.

## Engineering choices

Shared card rendering resides in `frontend/src/card.ts`; two subclasses register separate elements. A read-only `request` API recovers a lost Save acknowledgement without re-sending updates. Existing `likely_unused` observation attributes remain compatible, with new confirmed `card_storage_role` evidence for the editing contract. Module resources are registered manually by the user, never inserted into their dashboards automatically.

Development tooling is pinned by package-lock.json; npm reports ESLint 9.39.5 as deprecated. It is development-only, passed the configured lint checks, and is not shipped in the install ZIP. Updating that tooling major can be done separately from controller behavior.
