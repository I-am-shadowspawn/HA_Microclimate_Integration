# V2 public-release readiness review

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

## Tooling follow-up — 25 September 2026

V2-03 and V2-04 are implemented. The builder now has explicit public inputs and deterministic package checks; the portable workflow gates Python, frontend, browser, HACS, hassfest and packaging before a future tagged release. Core 2026.9.3 is the configured minimum. This review below records the earlier baseline; see [tests and release packaging](../README-TESTING.md) and the active [TODO](../TODO.md) for current status.

## Publication follow-up — 25 September 2026

V2-01 and V2-02 are complete. The source is uploaded and both public HACS and hassfest checks passed; V2-07 HACS install/update and release remain separate. This review below records the earlier baseline. See [publication preparation](V2-PUBLICATION-PREPARATION.md) and the active [TODO](../TODO.md) for current status.

Reviewed 25 September 2026 against workspace 1.3.0. Recommendation: retain the architecture and prepare a focused public-release cycle, not another wholesale rewrite. V1.3 is a strong functional baseline but is not yet a complete public/HACS distribution.

Scope: static review of runtime/frontend/build code, manifests, current and historical TODOs, completed write/card/compact plans, prior validation evidence, and current official HACS requirements. No live HA/controller access, publishing, destructive changes or new test run in this review. The 697-pass-per-HA-version / 21-unit / 43-browser evidence belongs to the completed 1.3.0 validation; it is not a fresh certification of V2.

## Findings

| Priority | Finding and evidence | Recommended response |
|---|---|---|
| Release gate | manifest.json has no documentation or issue_tracker and codeowners is empty. No hacs.json, project LICENSE, brand directory or .github workflows in the working distribution. | Establish publication identity, licensing, HACS manifest, assets and CI before claiming public readiness. |
| Release gate | scripts/build_release.py includes only selected text extensions and explicitly selected root files. It excludes PNG icons, YAML workflow/service files, licence files without extensions and a future hacs.json. | Make release contents explicit and test packaged assets; do not assume the manual ZIP is a valid HACS zip_release layout. |
| Release gate | Installation currently requires a separately registered module resource and manual version-query updates. frontend/src/index.ts unconditionally registers custom elements. | Test HACS installation AND card onboarding/update/cache behavior. Duplicate resource URLs can load the module twice and throw duplicate-registration errors; add a tested guard and deduplicate picker entries, with stale-version guidance. |
| Release gate | const.py still enables raw diagnostics by default; __init__.py automatically re-enables integration-disabled diagnostics. | Adopt public diagnostic defaults and remove the temporary re-enable behavior. Keep the aggregate schedule sensor enabled: it is now a permission dependency, despite being categorized diagnostic. |
| Release gate | Current release process is workspace-local, relies on a specific Python patch version and has no repository CI. | Establish portable contributor/bootstrap commands, HACS/hassfest validation and reproducible tagged release jobs. |
| Recommended | helpers.MicroclimateBaseEntity constructs a name-derived device identity that climate immediately overwrites; climate.entity_name is unused; climate/base async_update methods manually publish after coordinator refresh. | Replace with an entry-aware base, remove dead naming paths and prove a single refresh/state publication path. Preserve registry identity and observed-only climate semantics. |
| Recommended | transformation.py retains old enum/time/format dispatch helpers, while current consumers predominantly use validation.py, schedule.py and write_contract.py. Some helpers are only used by tests. | Audit symbols, remove unconsumed paths and port tests to current contracts. Important: validation.py still imports convert_temperature; deleting the whole module now would break runtime. Preserve the upstream F-label/Celsius nuance. |
| Recommended | Validation is distributed among read parser, write contract, card projection and TypeScript draft code; card_model.value_of separately parses clock tokens. | Define typed internal contracts and consolidate truly identical rules. Preserve deliberately different read observation vs write validation behavior, especially zero dates, opaque time suffixes and unknown values. Use shared fixtures for Python/TypeScript boundaries. |
| Recommended | card_api.py mixes transport, job state, lifecycle and writes; coordinator has dynamically added _card_* fields; frontend/src/card.ts is 1,346 lines. | Extract typed job/session state and smaller UI components in independently validated steps. Avoid a generic framework or introducing another polling owner. |
| Recommended | DataUpdateCoordinator._async_refresh is overridden; code reaches private coordinator locks/state and hass.data stores entries alongside a separate card API singleton. | Review against supported HA versions and reduce private coupling; consider typed entry.runtime_data plus a typed card service. Preserve locking, cancellation and independent-entry behavior. |
| Recommended | Batch writes perform multiple fresh reads, while publication exposes each observed intermediate state. | Measure request/notification volume before optimization. A successful N-step batch normally needs at least 3N+2 reads plus N updates in the current path. Remove redundant work only with race, permission-revocation and readback tests. No parallel vendor writes or blanket retries. |
| Recommended | No diagnostics.py support export; model/firmware evidence lives in several historical documents. Entity/card labels are mainly hard-coded English. | Add redacted diagnostics and a concise support matrix; improve translations and actionable user-facing errors. |
| External acceptance | 1.2.2 all-feature success is user-confirmed; 1.3.0 clean reinstall has not been explicitly confirmed in this conversation. Physical persistence, failure/soak and rate-limit behavior remain separate from happy-path tests. | Carry forward targeted acceptance checks, not every stale unchecked historical item. |

These are concrete publication gaps and maintainability opportunities, not a claim that currently functioning features are broken. Do not trade the tested write safeguards for fewer lines of code.

## HACS approach

Use a single public integration repository with the bundled frontend under custom_components/microclimate_integration/frontend. This keeps backend and card releases aligned. Prefer the normal integration directory installation route first; a separate HACS dashboard repository adds version-skew and support work without being required for this design.

HACS currently requires the integration layout/runtime files, manifest publication fields and brand assets. HA supports a local `brand/` directory inside the integration. Keep frontend build tools outside runtime while shipping the built JS and notices. [Integration requirements](https://hacs.xyz/docs/publish/integration/), [HA file structure](https://developers.home-assistant.io/docs/creating_integration_file_structure/).

Add a root hacs.json and publish actual GitHub Releases with matching integration versions. Choose and test an explicit minimum HA version; passing two September patch releases does not establish older-version support. The repository must be public. [HACS general requirements](https://hacs.xyz/docs/publish/start/).

There are two milestones: users can add a valid custom repository before it is included in HACS's default catalogue. Default inclusion requires successful HACS/hassfest checks, a release, and an owner/major-contributor submission to hacs/default; acceptance is external and not guaranteed. [Default inclusion](https://hacs.xyz/docs/publish/include/), [validation action](https://hacs.xyz/docs/publish/action/).

“HACS installation” means managed download/update delivery. It does not eliminate entering the device token/model, restarting HA when needed, or configuring dashboards. Decide whether to automate dashboard resource registration using supported interfaces, or provide a clear one-time setup path; verify storage-mode and YAML-dashboard behavior. Do not claim unattended automatic upgrades unless explicitly configured and tested.

HA's core Integration Quality Scale is a useful checklist, not a HACS certification requirement. No Bronze/Silver rating should be claimed for this custom integration. [Quality scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/).

## Prior TODO disposition

- RC-01–04, corrected timing maps, typed schedule observations, manual-time scope, shared polling/session, bounded writes, full schedule editing (old W-06), ramps/season ordering and card UI fixes are implemented. Do not reopen them as missing features.
- Historical old-ID migrations and per-point exposure are superseded by the accepted clean-reinstall/compact design. No migration from the disposable prototype is required for V2.
- User confirmation supersedes blanket “UI/features untested” notes for 1.2.2. Do not promote that to proof of reboot persistence, every firmware, interrupted-write behavior or 1.3.0 reinstall acceptance.
- Evo II is not awaiting its basic timing mapping anymore. Preserve the verified captures and user-confirmed behavior; retain only named firmware/physical edge cases needing evidence.
- v24 units, v25 interpretation, Constant target writes and Blue Periodic writes remain unverified or unsupported. They can stay clearly unavailable in V2; completing them is not a prerequisite for honest publication.
- Observed setpoint stays read-only. Calculated current period, reusable presets and public batch automation actions remain optional product extensions.

The new TODO.md is the sole active backlog; the previous content is archived in docs/TODO-PRE-V2-HISTORY.md. Old release reports/checklists remain historical evidence. No existing 1.3.0 release archive was changed.
