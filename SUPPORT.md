# Support and reporting

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

All integration and custom-card support is handled through [this GitHub repository](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration). Use [Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues) for bugs, questions and feature requests. This is volunteer-maintained software; no response-time guarantee is offered. Microclimate does not support this independent project.

Before reporting, check existing issues, [the README](README.md), [card usage](docs/CARD-USAGE.md), [write controls](docs/WRITE-CONTROLS.md) and [the tested platform](docs/TESTED-PLATFORM.md).

Include integration/card versions, Home Assistant Core version, controller model and firmware, reproduction steps, expected/observed behaviour and sanitized logs. You can use the integration entry's **Download diagnostics** action under Settings → Devices & services: its bounded export includes model/version, option flags, poll/write status and response shape, without raw pins or credential identifiers. Review it before attaching it to an issue. Clearly distinguish simulated results from controller observations. Never include an API token, token-bearing URL, full HA backup or unreviewed getAll capture. Redact controller names and other personal data where appropriate. Full response DEBUG logging is a separate opt-in capture and should be disabled after investigation.

Potential vulnerabilities and credential exposure belong in [private vulnerability reporting](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/security/advisories/new), not public Issues. See [SECURITY.md](SECURITY.md).
