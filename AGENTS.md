# Repository instructions for coding agents

These instructions apply to AI coding agents and automated contributors working in this repository.

## General principles

- Make the smallest coherent change required for the requested task.
- Preserve existing public behaviour unless the task explicitly requires a change.
- Do not introduce speculative compatibility, protocol behaviour, controller fields, units, ranges or device capabilities.
- Treat unknown or unverified vendor behaviour as unknown. Preserve raw values where required rather than guessing their meaning.
- Do not perform unrelated refactoring while implementing a scoped change.
- Do not modify live controllers, credentials, captures or external services unless the task explicitly authorizes it.

## Authoritative documentation

Use the current repository documentation as the source of truth.

User-facing behaviour:
- `README.md`
- `docs/user/`

Implementation contracts and architecture:
- `docs/technical/`

Project/licensing/publication information:
- `docs/project/`

Historical material:
- `docs/archive/`

The archive is retained for provenance. **Do not treat archived documentation as defining current behaviour.**

If current implementation and current documentation disagree, investigate the discrepancy rather than silently choosing one.

## Documentation management

When implementing a change, update documentation only where the change alters documented behaviour.

Use the following placement rules:

- `README.md` — product overview, installation, supported devices, major capabilities and important limitations.
- `docs/user/` — instructions needed to configure, operate or troubleshoot the integration.
- `docs/technical/` — architecture, data contracts, API behaviour, testing and implementation details.
- `docs/project/` — licensing, branding, publication and project-governance material.
- `docs/archive/` — superseded release records and historical engineering evidence.
- `CHANGELOG.md` — release-visible changes.
- `TODO.md` — current unresolved engineering/release work only.

Do not:
- add release-history detail to `README.md`;
- move technical implementation detail into user documentation;
- copy the same normative information into several documents unnecessarily;
- update archived documents to reflect current behaviour;
- create a new documentation file when an existing authoritative document is the appropriate home.

When moving or renaming documentation, update all repository links that reference it.

## Public documentation

Public documentation must describe the integration as it exists now.

Do not present unpublished prototypes, internal development stages or historical implementation experiments as public product versions.

Keep the independence notice accurate:
- this is an unofficial project;
- it is not affiliated with, endorsed by or supported by Microclimate or Blynk;
- Microclimate/Blynk names are used only to identify compatibility and service dependencies.

Do not make claims about private commercial or licensing arrangements between Microclimate and Blynk unless supported by documented evidence.

## Service dependency

The integration depends on the external Microclimate/Blynk cloud service.

Do not imply:
- local controller communication exists when it does not;
- continued cloud/API availability is guaranteed;
- the project controls the external service;
- compatibility with an untested controller or firmware has been established.

## Supported devices and protocol evidence

Currently documented supported controller families are:

- Evo Connect
- Evo Connect II
- Evo Connect III

Evo Connect Pro is untested/unknown unless new evidence establishes otherwise.

Before changing pin mappings, timing semantics, units, ranges or schedule behaviour, consult the relevant technical contracts, including:

- `docs/technical/SCHEDULE-CONTRACT.md`
- `docs/technical/VALIDATION-CONTRACT.md`
- `docs/technical/PIN-VERIFICATION.md`

Do not infer protocol meaning solely from field names, nearby values or apparent patterns.

## Editing and write safety

Controller writes require particular care.

Preserve the established principles documented in the write/runtime contracts, including:

- validated inputs;
- current permission checks;
- fresh state where required;
- serialized/shared I/O ownership;
- readback confirmation;
- no speculative rollback;
- no automatic repeated writes unless explicitly designed and documented;
- preservation of useful failure information without leaking credentials.

A successful HTTP request alone must not be treated as proof that the controller accepted or persisted a change.

## Tests

Run the smallest relevant test subset while developing.

After a coherent change is stable, run the broader applicable test suite once rather than repeatedly running unrelated tests.

The repository test matrix is authoritative for release validation.

Relevant files include:

- `pytest-review.ini`
- `conftest.py`
- `scripts/test_matrix.py`
- `docs/technical/TESTING.md`

Do not remove apparently small pytest configuration files without first checking how the test runner uses them.

For frontend changes, also run the relevant type, lint, unit and browser tests.

Do not weaken, skip or delete a regression test merely to make a change pass unless the test represents behaviour that has deliberately been changed and the replacement expectation is documented.

## Fixtures, captures and credentials

Never commit:

- Auth Tokens;
- passwords or API keys;
- credential-bearing URLs;
- private controller captures that have not been reviewed for publication;
- local filesystem paths or environment-specific secrets.

New captures or fixtures must be reviewed and sanitized before inclusion.

Preserve provenance for captured protocol evidence.

## Images and screenshots

User-facing screenshots belong under:

- `docs/images/onboarding/`
- `docs/images/cards/`

Use repository-relative paths in Markdown.

Before adding screenshots, check for:
- credentials;
- personal information;
- controller/account identifiers;
- unrelated Home Assistant data.

## Change completion

Before considering a task complete:

1. confirm the requested behaviour is implemented;
2. run the relevant tests;
3. update affected current documentation;
4. update `CHANGELOG.md` if the change is release-visible;
5. update `TODO.md` only when the task changes the status of an active TODO item;
6. verify links and image paths if documentation moved;
7. leave historical/archive documents unchanged unless the task specifically concerns archival organization.

Prefer a focused, reviewable change over broad repository cleanup.