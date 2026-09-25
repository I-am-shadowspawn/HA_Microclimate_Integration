"""Shared Python/TypeScript vectors for observations and strict edits."""
import json
from pathlib import Path

import pytest

from custom_components.microclimate_integration import validation
from custom_components.microclimate_integration.card_model import input_value, value_of
from custom_components.microclimate_integration.const import CHANNELS
from custom_components.microclimate_integration.constraints import numeric_maximum
from custom_components.microclimate_integration.edit_plan import build_plan
from custom_components.microclimate_integration.schedule import observe_date, observe_time
from custom_components.microclimate_integration.write_contract import (
    WriteValidationError, applicable, control_mode, date_string, definition_for,
    numeric, ramp_minutes, serialize, validate_input, validate_season_sequence,
)

VECTORS = json.loads((Path(__file__).resolve().parents[1] / 'fixtures/validation_contract.json').read_text())


def decoded(value):
    if isinstance(value, dict) and 'special' in value:
        return {'nan': float('nan'), 'infinity': float('inf'), 'negative_infinity': -float('inf')}[value['special']]
    return value


def accepts(function, *args):
    try:
        function(*args)
    except WriteValidationError:
        return False
    return True


@pytest.mark.parametrize('row', VECTORS['numbers'])
def test_numeric_observation_and_edit_contract(row):
    value = decoded(row['value'])
    assert validation.safe_temperature(value) == row['observation_temperature']
    assert validation.nonnegative_number(value) == row['observation_ramp']
    assert validation.percentage(value) == row['observation_percentage']
    assert accepts(numeric, value) == row['numeric_write']
    assert accepts(ramp_minutes, value) == row['ramp_write']
    assert numeric_maximum('number') == 100
    assert numeric_maximum('ramp') == 240


@pytest.mark.parametrize('row', VECTORS['dates'])
def test_date_observation_and_edit_contract(row):
    assert observe_date(row['value'])['interpretation'] == row['observation']
    assert accepts(date_string, row['value']) == row['edit_valid']


@pytest.mark.parametrize('row', VECTORS['seconds'])
def test_json_time_contract(row):
    field = definition_for('Evo Connect 3', 'Yellow_period_1_time')
    assert accepts(input_value, field, decoded(row['value'])) == row['valid']


@pytest.mark.parametrize('row', VECTORS['annual_cycles'])
def test_season_cycle_contract(row):
    field = definition_for('Evo Connect 3', 'season_1_start_pin')
    data = dict(zip(('v20', 'v21', 'v22', 'v23'), row['dates']))
    assert accepts(validate_season_sequence, field, row['dates'][0], data) == row['valid']


@pytest.mark.parametrize('row', VECTORS['enums'])
def test_enum_family_contract(row):
    field = definition_for(row['model'], row['key'])
    assert [label for _, label in field.options] == row['options']
    assert value_of(field, {field.pin: decoded(row['raw'])}) == row['observed']
    for value, valid in row['edits']:
        assert accepts(validate_input, field, value) == valid


@pytest.mark.parametrize('row', VECTORS['schedules'])
def test_whole_schedule_contract(row):
    data = {'v52': 1, 'v53': {'Day Night': 1, 'Multi': 2, 'Seasonal': 3}[row['mode']]}
    for i in range(1, 9):
        for kind, value in [('time', f'{i*3600}\0{i*3600}\0Europe/London\x000'), ('setpoint', 20)]:
            field = definition_for('Evo Connect 3', f'Yellow_period_{i}_{kind}')
            data[field.pin] = value
    patch = {'kind': 'channel', 'fields': {}, 'schedule': {'mode': row['mode'], 'points': row['points']}}
    assert accepts(build_plan, 'Evo Connect 3', 'Yellow', data, patch) == row['valid']


@pytest.mark.parametrize('row', VECTORS['applicability'])
def test_schedule_applicability_and_native_unit(row):
    field = definition_for(row['model'], f"{row['channel']}_period_{row['slot']}_setpoint")
    pins = CHANNELS[row['channel']]
    data = {pins['control_pin']: row['control_code'], pins['timing_type']: row['mode_code']}
    if row['present']:
        data[field.pin] = 25
    assert applicable(field, data) == row['writable']
    assert ('°C' if control_mode(field, data) in ('heating', 'cooling') else '%') == row['unit']


@pytest.mark.parametrize('row', VECTORS['time_encoding'])
def test_opaque_time_contract(row):
    observation = observe_time(row['raw'])
    assert observation['raw'] == row['raw']
    assert observation.get('seconds') == row['observed_seconds']
    field = definition_for('Evo Connect 3', 'Yellow_period_1_time')
    if row['expected'] is None:
        with pytest.raises(WriteValidationError):
            serialize(field, input_value(field, row['seconds']), {field.pin: row['raw']})
    else:
        assert serialize(field, input_value(field, row['seconds']), {field.pin: row['raw']}) == row['expected']
