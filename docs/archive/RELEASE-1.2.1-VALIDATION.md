# Microclimate 1.2.1 — date entry and channel loading fixes

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

## Fixes

1. Date inputs only captured drafts on `change` (normally blur). HA frequently replaces its frontend state object; rendering during typing reapplied the old draft value through Lit's live binding. Reproduced by typing one character, refreshing the HA object, and observing `01/06` replace the character. Inputs now capture local draft changes on every `input` event. This also protects number and schedule-time inputs. Typing still never sends an API update.
2. Channel rendering created point identifiers with `crypto.randomUUID`. On an ordinary HTTP dashboard that method is unavailable and the render failed, leaving the preceding Connecting display. Root cards initially rendered because they had no schedule points, but their Save also used the same method. IDs now use UUID v4 formatting with `crypto.getRandomValues`, preserving random request identities and HTTP compatibility. An actual non-secure HTTP browser origin now passes rendering, Add and Save tests for channels and Save for the root controller.
3. Multi time entry retains focus while crossing another point's time. The draft captures input immediately, while reordering waits for the input's change/commit event. Dragging still previews its order immediately.

The season calendar/order validation is unchanged: invalid ordering correctly disables Save; Cancel still discards the local draft. A valid four-season annual cycle may cross December/January once.

Browser reference: [randomUUID secure-context requirement](https://developer.mozilla.org/en-US/docs/Web/API/Crypto/randomUUID) and [getRandomValues availability](https://developer.mozilla.org/en-US/docs/Web/API/Crypto/getRandomValues). The test host uses plain HTTP outside localhost's secure-context exception, with every response served from an offline fixture; no controller is accessed. This reproduces a cause matching the reported channel symptom; the user's actual dashboard URL was not inspected.

## Upgrade

1. Install `microclimate-1.2.1-install.zip` into the HA configuration folder, replacing the integration, and restart HA.
2. **Edit the existing dashboard resource**, retaining type JavaScript module, to:
   `/microclimate_integration/microclimate-cards.js?v=1.2.1`
3. Hard refresh the browser or reload the HA companion-app frontend. Do not add a duplicate resource. Existing card configurations/device selections remain valid.
4. Confirm typing a date no longer reverts, then test a valid sequence. An out-of-sequence date must still leave Save inactive.

## Validation

- Both new core regression cases failed on the original 1.2.0 bundle before the fix and passed afterwards.
- 18 frontend unit tests and 38 Chromium browser tests passed, including continuous HA updates during typing, no implicit writes, insecure-HTTP channel Add/Save, insecure-HTTP root Save, and retained annual-order validation.
- Strict TypeScript, ESLint and production bundle build passed.
- All 38 card/API integration tests passed on each of HA 2026.9.2 and 2026.9.3, including served resource and authenticated save/status behavior.
- Integration Python code is byte-identical to 1.2.0; only frontend source/bundle, version metadata, tests and documentation change. The previous 683-test full HA matrix is historical baseline evidence; this patch reran the focused card/API suites, not all four full matrix runs.
- No live device writes, deployment or changes to the original repository were performed. Local install acceptance is still required after the user updates the dashboard resource.

Install/development ZIPs, a patch against 1.2.0, usage guide, test evidence and versioned checksums accompany this release. Final archive rebuild and patch equivalence are checked during packaging.
