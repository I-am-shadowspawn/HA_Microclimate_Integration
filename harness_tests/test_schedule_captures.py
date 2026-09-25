"""F08/F12/F13: real captured payloads, conservative semantics and live HA setup."""
import importlib
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.microclimate_integration.const import CHANNEL_PINS, CHANNELS, DOMAIN
from custom_components.microclimate_integration.schedule import observe_time, observe_date, schedule_observation

FIXTURES=Path(__file__).parents[1]/'fixtures'


def capture(name):
    return json.loads((FIXTURES/name).read_text())['payload']


def test_corrected_blue_pins_and_no_semantic_collisions():
    assert {key:CHANNELS['Blue'][key] for key in ('ramp_time','lower_alarm','upper_alarm','output_type')} == {
        'ramp_time':'v108','lower_alarm':'v109','upper_alarm':'v110','output_type':'v114'}
    pins=[]
    def visit(group):
        for value in group.values():
            if isinstance(value,dict):visit(value)
            else:pins.append(value)
    visit(CHANNEL_PINS)
    assert len(pins)==len(set(pins)), 'Different channel roles must not silently share pins'


@pytest.mark.parametrize('filename,channel,start,temperature',[
    ('captured_evo_connect.json','Yellow','09:30:00',32.0),
    ('captured_controller_2.json','Yellow','09:00:00',32.0),
    ('captured_controller_2.json','Red','09:00:00',25.0),
    ('captured_controller_2.json','Blue','09:00:00',34.0),
])
def test_captured_schedule_periods(filename,channel,start,temperature):
    payload=capture(filename);result=schedule_observation(payload,channel)
    period=result['periods']['period_1']
    assert period['start']['time']==start
    assert period['start']['reported_timezone']=='Europe/London'
    assert period['start']['timezone_recognized'] is True
    assert period['start']['fields']==payload[period['start_pin']].split('\x00')
    assert period['setpoint_celsius']==temperature
    assert result['timing_type']=='Day Night'
    assert len(result['periods'])==8


def test_fixed_output_percentage_and_zero_retained():
    result=schedule_observation(capture('captured_evo_connect.json'),'Blue')
    assert result['control_mode']=='fixed'
    assert result['periods']['period_1']['setpoint_raw']==0
    assert result['periods']['period_1']['setpoint_percentage']==0
    assert 'setpoint_celsius' not in result['periods']['period_1']
    assert result['periods']['period_8']['start']['time']=='00:00:00'
    assert result['reported_period_count']==8  # Counts reported slots, not active slots.


@pytest.mark.parametrize('raw',[None,True,[],{},float('inf'),'bad\x01text','x'*1025])
def test_bad_schedule_values(raw):
    result=observe_time(raw)
    assert result['raw'] is None
    assert result['interpretation']=='missing_or_invalid'


@pytest.mark.parametrize('event,label',[('sr','sunrise'),('ss','sunset')])
def test_solar_unknown_fields_preserved(event,label):
    value=event+'\x000\x00Europe/London\x00\x000'
    result=observe_time(value)
    assert result['unsupported_token']==event
    assert result['status']=='unsupported'
    assert 'event' not in result and 'kind' not in result
    assert result['fields']==value.split('\x00')
    assert result['raw']==value
    assert 'time' not in result  # No fabricated solar time or offset.


@pytest.mark.parametrize('raw',['90000','-1','12.5','junk'])
def test_unsupported_time_is_not_coerced(raw):
    result=observe_time(raw)
    assert result['raw']==raw
    assert result['interpretation']=='reported_unparsed'
    assert 'time' not in result


def test_timezone_not_silently_replaced():
    result=observe_time('3600\x007200\x00Not/AZone\x001,3,5\x00120')
    assert result['reported_timezone']=='Not/AZone'
    assert result['timezone_recognized'] is False
    assert result['fields'][1:] == ['7200','Not/AZone','1,3,5','120']


@pytest.mark.parametrize('value,status',[('22/09/26','calendar_fields'),('01/03','calendar_fields'),
    ('29/02','calendar_fields'),('29/02/2025','invalid_date'),('00/00','zero_date'),('31/04','invalid_date'),
    ('2026-09-22','reported_unparsed'),(None,'missing_or_invalid')])
def test_metadata_date_formats(value,status):
    assert observe_date(value)['interpretation']==status


def test_captured_root_formats():
    payload=capture('captured_evo_connect.json')
    assert observe_time(payload['v27'])['time']=='20:16:24'
    date=observe_date(payload['v26'])
    assert (date['day'],date['month'],date['year_two_digits'])==(22,9,26)
    assert 'year' not in date
    assert observe_date(payload['v20'])['interpretation']=='zero_date'


@pytest.mark.parametrize('filename,model,channels',[
    ('captured_evo_connect.json','Evo Connect',['Yellow','Blue']),
    # Model identified by the maintainer.
    ('captured_controller_2.json','Evo Connect 3',['Yellow','Red','Blue']),
])
async def test_captured_entities_refresh_reload_and_unload(hass,filename,model,channels):
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'capture','model':model,'token':'fake'})
    entry.add_to_hass(hass);payload=capture(filename);registry=er.async_get(hass)
    def state(suffix):
        return hass.states.get(registry.async_get_entity_id('sensor',DOMAIN,entry.entry_id+suffix))
    with patch('custom_components.microclimate_integration.api_client.fetch_data',new=AsyncMock(return_value=payload)) as api:
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        for channel in channels:
            s=state('_'+channel+'_schedule')
            assert s.state=='8'
            assert s.attributes['periods']['period_1']['start']['reported_timezone']=='Europe/London'
        assert state('_metadata_system_time').state==('20:16:24' if model=='Evo Connect' else '20:10:00')
        assert state('_metadata_season_1_start').state=='unknown'
        assert state('_metadata_season_1_start').attributes['raw']=='00/00'
        if model=='Evo Connect 3':
            assert float(state('_Blue_measurement_lower_alarm').state)==0
            assert float(state('_Blue_measurement_upper_alarm').state)==50
            assert state('_Blue_configuration_output_type').state=='on_off'
            assert 'ramp_time' not in state('_Blue_schedule').attributes
        assert float(state('_Yellow_measurement_ramp_time').state)==(120 if model=='Evo Connect' else 60)
        assert state('_Yellow_measurement_ramp_time').attributes['unit_of_measurement']=='min'
        assert api.await_count==1
        ids={e.unique_id for e in er.async_entries_for_config_entry(registry,entry.entry_id)}
        coordinator=hass.data[DOMAIN][entry.entry_id]
        api.return_value={}
        await coordinator.async_refresh();await hass.async_block_till_done()
        assert state('_Blue_schedule').state=='unknown'
        assert state('_metadata_system_time').state=='unknown'
        api.return_value=payload
        assert await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()
        assert ids=={e.unique_id for e in er.async_entries_for_config_entry(registry,entry.entry_id)}
        assert api.await_count==3
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
        assert coordinator._unsub_refresh is None


def test_all_retained_modules_import_and_no_dormant_platforms():
    directory=Path(__file__).parents[1]/'custom_components'/DOMAIN
    for path in directory.glob('*.py'):
        importlib.import_module('custom_components.'+DOMAIN+'.'+path.stem)
    for name in ('alt_climate','alt_sensor','schedual_sensor','support_testing'):
        assert not (directory/(name+'.py')).exists()


@pytest.mark.parametrize('value,expected',[(50,50),(0,0),(100,100),('50.5',50.5),(-1,None),(101,None),(True,None),('nan',None)])
def test_fixed_schedule_percentage_boundaries(value,expected):
    period=schedule_observation({'v112':0,'v93':value},'Blue')['periods']['period_1']
    assert period.get('setpoint_percentage')==expected
    assert 'setpoint_celsius' not in period


@pytest.mark.parametrize('value,expected',[(120,120),('60',60),(0,0),(-1,None),('nan',None),(None,None),(True,None)])
def test_ramp_minutes(value,expected):
    result=schedule_observation({'v48':value},'Yellow')
    assert result['ramp_time']['minutes']==expected
    assert result['ramp_time']['unit']=='min'


@pytest.mark.parametrize('value,expected',[(120,120),('60',60),(0,0),(60.5,60.5)])
def test_duration_transformation_uses_minutes(value,expected):
    from custom_components.microclimate_integration.transformation import format_sensor_value
    assert format_sensor_value('v48',value,'duration_minutes',{},'Yellow')==expected


@pytest.mark.parametrize('value',[None,True,-1,'nan'])
def test_duration_transformation_rejects_invalid_values(value):
    from custom_components.microclimate_integration.transformation import convert_duration_minutes
    with pytest.raises(ValueError):
        convert_duration_minutes(value)


def test_captured_model_probe_profiles():
    from custom_components.microclimate_integration.const import MODEL_CHANNEL_OPTIONS
    for model,filename,expected in [
        ('Evo Connect','captured_evo_connect.json',{'Yellow'}),
        ('Evo Connect 3','captured_controller_2.json',{'Yellow','Red','Blue'}),
    ]:
        profile=MODEL_CHANNEL_OPTIONS[model]
        assert {channel for channel,features in profile.items() if features['hasTemperatureProbe']}==expected
        data=capture(filename)
        assert {channel for channel in profile if CHANNELS[channel]['temp_pin'] in data}==expected
