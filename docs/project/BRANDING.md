# Independent project branding

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

The maintainer supplied the current integration icon and Evo Connect, Evo Connect II and Evo Connect III artwork on 27 September 2026, and confirmed the artwork is original with redistribution rights. The integration icon is packaged at `custom_components/microclimate_integration/brand/icon.png`. Model artwork is packaged under `custom_components/microclimate_integration/frontend/` and displayed by the bundled controller and channel cards. The integration and HACS names include “Unofficial”.

The maintainer also supplied red, yellow and blue channel artwork. These files are packaged under `custom_components/microclimate_integration/static/` and used as `entity_picture` on channel entities. Root-controller entities retain their normal icons. Home Assistant screens decide whether to render an entity's picture, so appearance can vary by card and frontend version.

Home Assistant supports [local custom-integration brand images](https://developers.home-assistant.io/docs/core/integration/brand_images/); HACS requires a [brand icon](https://hacs.xyz/docs/publish/integration/).

Home Assistant Core 2026.9.3 does not expose a supported per-device image field in the device registry. Its native device page therefore uses the integration brand image; the model image appears in the bundled cards instead. Model images do not change device identifiers or registry metadata.

![Integration icon](../../custom_components/microclimate_integration/brand/icon.png)
