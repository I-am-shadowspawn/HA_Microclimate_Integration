# Tested platform and initial public support baseline

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

Confirmed by the maintainer on 25 September 2026 as the platform with full integration testing:

| Component | Version |
|---|---|
| Home Assistant Core | 2026.9.3 |
| Supervisor | 2026.09.2 |
| Home Assistant Operating System | 18.2 |
| Frontend | 20260826.7 |

The initial HACS minimum is Home Assistant Core 2026.9.3. Supervisor, OS and Frontend versions record the tested environment; they are not independent dependencies of this custom integration. Other installation types have not been established as fully tested by this report.

Automated integration suites also passed on Core 2026.9.2, but that does not lower the selected public minimum. Exact installed Microclimate release was not specified in this platform confirmation; do not infer new 1.3.0 clean-install or future V2/HACS acceptance from it. Future releases must validate the declared minimum and then-current supported stable Core version.
