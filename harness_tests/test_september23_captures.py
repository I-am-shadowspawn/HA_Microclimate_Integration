"""Replay hardware evidence through the validated channel-aware mappings."""
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.microclimate_integration.api_client import normalize_response
from custom_components.microclimate_integration.const import DOMAIN
from custom_components.microclimate_integration.schedule import schedule_observation

RUNS = json.loads((Path(__file__).parents[1] / "fixtures/captures_20260923.json").read_text())["runs"]
# Independent pin expectations, deliberately not imported from the schema under test.
PINS = {
    "Yellow": ("v0", "v8", "v4", "v48", "v49", "v50"),
    "Red": ("v1", "v9", "v5", "v78", "v79", "v80"),
    "Blue": ("v2", "v10", "v6", "v108", "v109", "v110"),
}


@pytest.mark.parametrize("run", RUNS, ids=lambda run: run["run_id"])
async def test_captured_entities_all_samples(hass, run):
    entry = MockConfigEntry(domain=DOMAIN, data={"evo_device": "capture", "model": run["model"], "token": "fake"})
    entry.add_to_hass(hass)
    registry = er.async_get(hass)

    def state(suffix, platform="sensor"):
        entity_id = registry.async_get_entity_id(platform, DOMAIN, entry.entry_id + suffix)
        return hass.states.get(entity_id) if entity_id else None

    with patch("custom_components.microclimate_integration.api_client.fetch_data", new=AsyncMock()) as api:
        api.return_value = normalize_response(run["samples"][0]["payload"])
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        coordinator = hass.data[DOMAIN][entry.entry_id]
        channels = ["Yellow", "Red", "Blue"] if run["model"] == "Evo Connect 3" else ["Yellow", "Blue"]
        for sample in run["samples"]:
            assert sample["http_status"] == 200 and sample["ok"]
            data = sample["payload"]
            api.return_value = normalize_response(data)
            await coordinator.async_refresh()
            await hass.async_block_till_done()
            assert int(state("_reported_pin_count").state) == len(data)
            for channel in channels:
                temp, target, output, ramp, lower, upper = PINS[channel]
                prefix = "_" + channel
                assert float(state(prefix + "_measurement_output").state) == pytest.approx(data[output])
                schedule = state(prefix + "_schedule")
                assert schedule.state == "8"  # Reported slots, NOT active periods.
                assert len(schedule.attributes["periods"]) == 8
                mode = schedule.attributes["timing_type"]
                assert ("day_night" in schedule.attributes) == (mode == "Day Night")
                assert ("seasons" in schedule.attributes) == (mode == "Seasonal")
                assert ("daily_points" in schedule.attributes) == (mode == "Multi")
                if channel == "Blue":
                    assert state(prefix + "_configuration_output_type").state == "on_off"
                    assert "source_pin" not in state(prefix + "_configuration_output_type").attributes
                    assert state(prefix + "_measurement_ramp_time") is None
                    assert "ramp_time" not in schedule.attributes
                if run["model"] == "Evo Connect" and channel == "Blue":
                    assert state(prefix, "climate") is None
                    assert state(prefix + "_measurement_setpoint") is None
                    assert schedule.attributes["periods"]["period_1"]["setpoint_percentage"] == 0
                    assert state(prefix + "_measurement_ramp_time") is None
                    continue
                climate = state(prefix, "climate")
                assert climate.attributes["current_temperature"] == pytest.approx(data[temp], abs=0.06)
                target_value = float(data[target].removesuffix("C"))
                assert climate.attributes["observed_target_temperature"] == target_value
                for key, expected in (("temperature", data[temp]), ("setpoint", target_value),
                                      ("ramp_time", data[ramp]), ("lower_alarm", data[lower]), ("upper_alarm", data[upper])):
                    if key == "ramp_time" and channel == "Blue":
                        assert state(prefix + "_measurement_ramp_time") is None
                        assert "ramp_time" not in climate.attributes
                        assert "ramp_time" not in schedule.attributes
                        continue
                    # Native temperature conversion intentionally rounds to 0.1 C.
                    if key in ("temperature", "setpoint", "lower_alarm", "upper_alarm"):
                        expected = round(expected, 1)
                    assert float(state(prefix + "_measurement_" + key).state) == pytest.approx(expected)
            if run["model"] != "Evo Connect 3":
                assert not any(entity.unique_id.startswith(entry.entry_id + "_Red")
                               for entity in er.async_entries_for_config_entry(registry, entry.entry_id))
            if run["model"] == "Evo Connect 2":
                assert state("_Yellow_configuration_control_pin").state == "cooling"
                assert state("_Blue_configuration_control_pin").state == "heating"
                assert state("_Yellow_configuration_output_type").state == "dimming"
                assert state("_Blue_configuration_output_type").state == "on_off"
                assert state("_Yellow", "climate").attributes["hvac_action"] == ("cooling" if data["v4"] > 0 else "idle")
                assert state("_Blue", "climate").attributes["hvac_action"] == ("heating" if data["v6"] > 0 else "idle")
                # Capture-backed channel timing tables.
                current_decoder = {0: "Constant", 1: "Day Night", 2: "Multi", 3: "Periodic", 4: "Seasonal"}
                assert state("_Yellow_configuration_timing_type").state == {0: "Constant", 1: "Day Night", 2: "Multi", 3: "Seasonal"}[data["v53"]]
                assert state("_Blue_configuration_timing_type").state == current_decoder[data["v113"]]
                assert state("_metadata_season_1_start").state == "unknown"
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()


def test_later_evo_ii_preserves_all_eight_distinct_yellow_slots():
    run = next(run for run in RUNS if run["run_id"].startswith("20260923T155359"))
    for sample in run["samples"]:
        data = normalize_response(sample["payload"])
        periods = list(schedule_observation(data, "Yellow")["periods"].values())
        assert [p["start"]["time"] for p in periods] == ["02:00:00", "05:00:00", "08:00:00", "11:00:00", "13:00:00", "15:00:00", "20:00:00", "23:00:00"]
        assert [p["setpoint_celsius"] for p in periods] == [24.5, 25, 24, 26, 23.5, 27, 27.5, 28]
        assert schedule_observation(data, "Yellow")["ramp_time"]["minutes"] == 9
        blue = schedule_observation(data, "Blue")
        assert blue["periodic_interval"]["raw"] == 60
        assert blue["periodic_duration"]["raw"] == 0
        assert blue["periodic_interval"]["interpretation"] == "reported_unparsed"


def test_unchanging_previous_day_payload_does_not_establish_device_freshness():
    run = RUNS[0]
    assert run["run_id"].startswith("20260923T154209")
    baseline = normalize_response(run["samples"][0]["payload"])
    assert baseline["v26"] == "22/09/26"
    assert all(normalize_response(sample["payload"]) == baseline for sample in run["samples"])


def test_operator_labelled_timing_evidence():
    # Evidence assertion, not approval of the existing global enum decoder.
    for run in RUNS:
        label = run.get("operator_yellow_timing")
        if label is None:
            continue
        expected_code = {"Constant": 0, "Day Night": 1, "Multi": 2, "Seasonal": 3}[label]
        blue_code = {"Constant": 0, "Day Night": 1, "Multi": 2, "Periodic": 3, "Seasonal": 4}[run["operator_blue_timing"]]
        for sample in run["samples"]:
            assert sample["payload"]["v53"] == expected_code
            assert sample["payload"]["v113"] == blue_code
        assert len({sample["payload"]["v27"] for sample in run["samples"]}) > 1
