# 1.1.1 validation — 24 September 2026

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

645 tests passed on each of HA 2026.9.2 and 2026.9.3 (Python 3.14.7), in both regression and release-gate modes. No skipped tests, failures or errors; 97% integration line coverage. Dependency checks passed. HTTP is mocked and network sockets are blocked.

The 44 new tests supplement the 601-test baseline: complete calendar permutations, user examples/corrections, duplicates and malformed/missing/unset dates, ramp bounds/units/integral serialization, HA number services, fresh-baseline changes, readback conflicts, conflicting queued dates and separate hour/minute requests. Existing all-field tests now include ramps across every eligible profile. Production source syntax and English translation parity checks pass.

Yellow v48 and Evo III Red v78 are editable as 0–240 whole minutes. Blue has no ramp write. Root date edits enforce a strict yearly cycle including the last-to-first boundary, permit a December/January crossing and reject duplicate or invalid dates. Explicit 00/00 siblings allow initial population; this is not a claim of hardware disable semantics. A changed sibling is revalidated from the fresh baseline, and an invalid observed cycle cannot be confirmed as successful.

The maintainer confirmed testing all previously enabled 1.1.0 attributes on Evo II and Evo III. This record acknowledges that confirmation without assigning an unreported firmware or claiming new capture evidence. New ramp/order behavior needs live acceptance; Evo I writes, persistence and soak remain separate.

Separate hour/minute submissions remain separate full-time operations. No silent debounce or command coalescing was introduced. Use one complete time.set_value action or an explicit draft/Apply workflow to avoid intermediate times; see WRITE-CONTROLS.md.

Packaging verification: install/development archives are built twice and byte-compared, checked for integrity/manifest/source syntax, and accompanied by SHA256 checksums. The source patch is applied to the preserved 1.1.0 development archive in a temporary directory and the results are compared byte-for-byte with 1.1.1. No original-repository modification, deployment or live controller write is performed.
