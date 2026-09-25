# Licensing and provenance review

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

The maintainer confirmed that the original integration code has no other code sources and authorized the MIT licence, copyright 2026 Simon Burke. The project licence is in [LICENSE](../LICENSE); an identical copy is included in the installable component so manual/HACS installation preserves the licence.

An esbuild input-metadata audit of the current card source identified only the following bundled external packages. Each package declares BSD-3-Clause, and its full licence text is retained verbatim in `custom_components/microclimate_integration/frontend/THIRD_PARTY_NOTICES.txt`. These notices remain separate from the project MIT licence.

| Bundled package | Installed version | Declared licence |
|---|---|---|
| lit | 3.3.3 | BSD-3-Clause |
| lit-element | 4.2.2 | BSD-3-Clause |
| lit-html | 3.3.3 | BSD-3-Clause |
| @lit/reactive-element | 2.1.2 | BSD-3-Clause |

`frontend/build.mjs` reproduces the bundled notices during every build. Build/test tools (TypeScript, ESLint, esbuild, Playwright, Vitest and their dependencies) are not bundled or shipped as node_modules; Python test environments are also excluded. Runtime Python dependencies are supplied by Home Assistant: the manifest has no separately installed requirements. This audit covers distributed third-party code, not an assertion that the entire development environment is MIT licensed.

Generated icon provenance and the excluded, unapproved vendor-like draft are documented in [BRANDING.md](BRANDING.md). Recheck dependency licences whenever the bundle changes. No permission is claimed for Microclimate trademarks or vendor artwork.
