# Microclimate pin verification worksheet

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

No field is verified by this blank worksheet. Maintain separate evidence per model and firmware; do not generalize between controllers without observations.

- Model:
- Firmware/version (or “unknown”):
- Observation date/time and timezone:
- Non-secret local controller label:
- Source: controller display / official app:
- Candidate pin:
- Existing source-code interpretation, if any:
- Raw API value:
- Displayed value and unit:
- Channel and operating mode:
- Observation conditions and any single setting changed through the official interface:
- Repeated observations (include idle/active or boundary examples where relevant):
- Missing, disconnected or restart behavior:
- Confidence: unknown / provisional / repeatedly verified:
- Remaining conflicting observations:

| Timestamp | Pin | Raw value | Display/app value | Unit | Mode | Change or observation |
|---|---|---|---|---|---|---|
| | | | | | | |

Use passive comparisons first. Do not infer that a percentage is watts, that an absent alarm means healthy, or that an F suffix proves Fahrenheit: the maintainer has confirmed Celsius numbers can carry an F label. Record the relevant endpoint/firmware scope as evidence becomes available. Remove API tokens, query URLs containing tokens, account information and unrelated response fields before sharing fixtures.

Promotion criterion: repeatable agreement with a known physical/display quantity, documented units and missing-value behavior for that model/firmware, followed by fixture-backed tests. Synthetic test data alone cannot satisfy this criterion.
