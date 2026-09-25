# V2-01 / V2-02 publication preparation — 25 September 2026

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

## V2-01 — local preparation complete

- Public repository verified by GitHub API: `I-am-shadowspawn/HA_Microclimate_Integration`, public, Issues enabled, default branch `main`; currently empty. Documentation/support URLs point to that repository and will become usable once its files are published.
- Maintainer confirmed no other original code sources. MIT licence and Simon Burke copyright recorded; installable component includes the licence too.
- Bundled dependency licence texts checked against esbuild's actual input package set; see [LICENSING.md](LICENSING.md).
- CONTRIBUTING.md, SUPPORT.md, SECURITY.md, CODEOWNERS, bug/feature forms and pull-request guidance added. All reporting goes through GitHub. Private vulnerability reporting enabled and verified through the GitHub API.
- Original generated thermometer/clock draft included with provenance; supplied gecko excluded. See [BRANDING.md](BRANDING.md).
- Local caches, environments and token files excluded by .gitignore; existing fixtures are sanitized. No source or release has been uploaded as part of this task.

## V2-02 — local changes complete; remote acceptance pending

Manifest and root hacs.json retain domain `microclimate_integration`, unofficial display name, genuine owner/links, `device` integration type and minimum Core 2026.9.3. The current candidate remains 1.3.0; no premature V2 version bump.

The original draft icon is at `custom_components/microclimate_integration/brand/icon.png`. Its appearance remains open to maintainer review before release. Both release-package types now include the component licence and icon; the development package additionally includes HACS metadata, support documents and GitHub templates/workflow. This fixes the omissions directly relevant to these tasks; broader release-pipeline work remains V2-03/V2-04.

Full local hassfest validation passed with zero invalid integrations and no warnings, using unmodified Home Assistant Core validator source at commit `5e95eae1ee8d77da87c82343a3bf637ab5795845`, all default plugins, Python 3.14.7. Validator-only dependencies are in a separate workspace environment; existing test dependencies were reused read-only. The Docker daemon is unavailable locally; this was a source-based run, not a container run. Fixed manifest ordering and declared config-entry-only setup in response to the validator. Logs are retained in the workspace `outputs/v2-publication-validation/hassfest.txt`.

`.github/workflows/validate.yml` runs the official hassfest and HACS integration actions, with no ignored checks and read-only repository permissions. HACS performs checks against GitHub repository contents; the verified empty repository cannot pass until source is uploaded. A local schema check is not recorded as a HACS pass.

Backend regression validation after the setup-schema change: **697 passed in 24.04 seconds** on Home Assistant Core 2026.9.3. No live API calls or controller writes were used.

## Next concrete action

Obtain explicit authorization to upload the prepared source to the named public repository (no stable release or device operations implied). Review the draft icon, upload the candidate, run both workflow jobs and resolve any failures. Only mark V2-02 complete after the actual HACS check passes. HACS custom-repository install/update and catalogue submission remain the separate V2-07 task.

References: [HACS requirements](https://hacs.xyz/docs/publish/integration/), [HACS action](https://hacs.xyz/docs/publish/action/), [HA local branding](https://developers.home-assistant.io/docs/core/integration/brand_images/).
