"""Canonical mapping, corrected Red, and controller metadata regression tests."""
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.helpers import entity_registry as er, device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.microclimate_integration import const
from custom_components.microclimate_integration.const_helpers import get_device_channels, get_pin_data, enum_value
from custom_components.microclimate_integration.transformation import convert_setpoint, format_sensor_value
from custom_components.microclimate_integration.validation import safe_scalar


def test_single_source_and_preserved_schedule():
    assert const.CHANNELS['Red'] == dict(temp_pin='v1',setpoint_pin='v9',control_pin='v82',
        ramp_time='v78',lower_alarm='v79',upper_alarm='v80',timing_type='v83',output_type='v84',
        channel_name='v17',current_power='v5')
    for channel, first in [('Yellow',32),('Red',62),('Blue',92)]:
        schedule=const.CHANNEL_PINS[channel]['schedule']
        for period in range(1,9):
            expected=f'v{first+2*(period-1)}'
            assert schedule[f'period_{period}']['schedule_start_time_pin']==expected
            assert get_pin_data(get_device_channels('Evo Connect 3'),channel,
                f'schedule.period_{period}.schedule_start_time_pin')['pin']==expected
        assert get_pin_data(get_device_channels('Evo Connect 3'),channel,'schedule_start_time_pin') is None
        assert const.CHANNEL_PINS[channel]['metadata']['control_pin']==const.CHANNELS[channel]['control_pin']
        assert const.CHANNELS[channel]['control_pin'] != const.CHANNELS[channel]['output_type']
    assert const.CHANNEL_PINS['Red']['schedule']['periodic_interval_pin']=='v85'
    assert const.CHANNEL_PINS['Blue']['schedule']['periodic_duration_pin']=='v116'
    assert convert_setpoint('20.0',{'v82':'1.0','v111':'0.0'},'Red')==20


@pytest.mark.parametrize('raw,expected',[(0,'fixed'),('1.0','heating'),(2.0,'cooling'),('2.5',None),
    (True,None),('nan',None),('inf',None),(None,None),({},None),(9,None)])
def test_enum_normalization(raw,expected):
    assert enum_value(raw,const.CONTROL_TYPE_MAPPING)==expected


@pytest.mark.parametrize('kind,raw,expected',[('control_type','1.0','heating'),('timing_type','1.0','Day Night'),
    ('output_type',0.0,'pulse'),('time','3600','01:00'),('temperature','20°F',20)])
def test_shared_transformation_dispatch(kind,raw,expected):
    assert format_sensor_value('v1',raw,kind,{},'Red')==expected


@pytest.mark.parametrize('raw',[None,True,{},[],float('inf'),'','\x00bad','x'*256])
def test_metadata_rejects_unsafe_states(raw):
    assert safe_scalar(raw) is None


async def test_red_and_root_metadata_real_setup_refresh_reload(hass):
    entry=MockConfigEntry(domain=const.DOMAIN,data={'evo_device':'controller','token':'fake','model':'Evo Connect 3'})
    entry.add_to_hass(hass)
    metadata={'v20':'01/03','v21':'01/06','v22':'01/09','v23':'01/12','v24':'12.5',
              'v25':'F','v26':'22/09/2026','v27':'12:34','v29':'My controller'}
    payload={**metadata,'v1':'21°F','v9':'20.0','v82':'1.0','v83':'1.0','v84':'0.0',
             'v5':'40','v111':'0.0','v112':'2.0'}
    registry=er.async_get(hass)
    def state(suffix):
        entity_id=registry.async_get_entity_id('sensor',const.DOMAIN,entry.entry_id+suffix)
        return hass.states.get(entity_id)
    with patch('custom_components.microclimate_integration.api_client.fetch_data',new=AsyncMock(return_value=payload)) as api:
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        assert state('_Red_measurement_setpoint').state=='20.0'
        assert state('_Red_measurement_temperature').state=='21.0'
        assert state('_Red_measurement_output').state=='40.0'
        assert state('_Red_configuration_control_pin').state=='heating'
        assert state('_Red_configuration_output_type').state=='pulse'
        assert state('_Red_configuration_timing_type').state=='Day Night'
        root=dr.async_get(hass).async_get_device_by_identifier((const.DOMAIN,entry.entry_id),entry.entry_id)
        for key,definition in const.DEVICE_METADATA_PINS.items():
            s=state('_metadata_'+key.removesuffix('_pin'))
            assert s.state==metadata[definition['pin']]
            assert registry.async_get(s.entity_id).device_id==root.id
            assert 'unit_of_measurement' not in s.attributes
            assert 'device_class' not in s.attributes
        entries=er.async_entries_for_config_entry(registry,entry.entry_id)
        ids={e.unique_id for e in entries}
        assert sum('_schedule_period_' in uid for uid in ids) == 0
        assert api.await_count==1
        coordinator=hass.data[const.DOMAIN][entry.entry_id]
        api.return_value={'v82':0,'v9':20,'v83':999,'v84':False,'v29':'Renamed controller'}
        await coordinator.async_refresh();await hass.async_block_till_done()
        assert state('_Red_measurement_setpoint').state=='unknown'
        assert state('_Red_configuration_timing_type').state=='unknown'
        assert state('_Red_configuration_output_type').state=='unknown'
        assert state('_metadata_system_date').state=='unknown'
        assert state('_metadata_system_name').state=='Renamed controller'
        assert api.await_count==2
        assert await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()
        assert ids=={e.unique_id for e in er.async_entries_for_config_entry(registry,entry.entry_id)}
        assert api.await_count==3
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()

