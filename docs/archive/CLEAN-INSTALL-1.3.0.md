# 1.3.0 clean reinstall for the single testing instance

> **Unofficial, independent project.** This integration and its custom cards are not affiliated with, endorsed by, or supported by Microclimate. Their only connection to Microclimate is that they work with its products. Product names are used solely to identify compatibility. For integration support, use this project’s [GitHub Issues](https://github.com/I-am-shadowspawn/HA_Microclimate_Integration/issues).

This release intentionally removes individual schedule point entities. No migration, old-ID compatibility or full-exposure mode is included. It does not change controller pin mappings or reset stored schedules.

1. Save controller name/model/token securely; copy card YAML, titles and custom colours. Keep the 1.2.2 ZIP as rollback. Do not put credentials in reports.
2. Wait for pending Save operations to finish. Remove the old Microclimate entries through Settings → Devices & services. Verify their devices/entities have gone; remove any remaining orphaned Microclimate-only records through HA UI. Do not edit `.storage` files.
3. Replace `config/custom_components/microclimate_integration` with the directory in the install ZIP. Do not overlay: `time.py` and `const2.py` are intentionally removed. Restart HA.
4. Add new entries with the same controller credentials/model. Setup reads existing controller configuration; it sends no reset, schedule clear or write.
5. In existing cards, reselect the new channel/root devices. Recheck any entity references in templates or automations; entry/device IDs may change. Individual schedule entities cannot be restored in this version.
6. Edit the existing JavaScript-module resource to `/microclimate_integration/microclimate-cards.js?v=1.3.0`. Do not add a duplicate. Hard-refresh/reload the frontend.
7. Confirm schedule/modes/observations read correctly before choosing any test Save. Keep Reported schedule periods enabled; it now anchors channel schedule permissions. Mode/ramp/alarm controls and root dates retain independent permissions.

Expected fresh-install totals (default diagnostics enabled): Connect 59, Evo II 66, Evo III 93 entities, reduced from 123/130/189. Unrelated diagnostics remain exposed. The aggregate schedule still contains all eight stored slots; Day/Night uses two. No active-period inference has been added.

Rollback: remove the new entries, replace the integration folder with 1.2.2, restart and recreate/rebind cards. This does not restore prior HA registry IDs. HA uninstall/reinstall must not clear remote schedules; verify current values by reading before any manual write.
