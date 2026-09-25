"""F10/F04/F11 contracts using real HA forms and measurement registration."""
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.helpers import entity_registry as er, device_registry as dr
from homeassistant.helpers.translation import async_get_translations
from homeassistant.util.unit_system import METRIC_SYSTEM, US_CUSTOMARY_SYSTEM
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.microclimate_integration.const import DOMAIN, MODEL_OPTIONS, DEFAULT_MODEL
from custom_components.microclimate_integration.config_flow import MicroclimateConfigFlow
from custom_components.microclimate_integration.identity import channel_identity
from custom_components.microclimate_integration.transformation import convert_temperature


def test_ordered_model_default():
    assert MODEL_OPTIONS == ('Evo Connect','Evo Connect 2','Evo Connect 3')
    assert DEFAULT_MODEL == 'Evo Connect'
    schema=MicroclimateConfigFlow()._get_data_schema()
    assert schema({'evo_device':'test','token':'token'})['model']=='Evo Connect'
    assert list(schema.schema['model'].container)==list(MODEL_OPTIONS)


@pytest.mark.parametrize('field', ['evo_device','token','model'])
@pytest.mark.parametrize('blank', ['', '   ', '\t'])
async def test_blank_onboarding_has_translated_error(hass,field,blank):
    flow=MicroclimateConfigFlow();flow.hass=hass;flow.context={'source':'user'}
    data={'evo_device':'test','token':'token','model':'Evo Connect',field:blank}
    with patch('custom_components.microclimate_integration.api_client.fetch_data') as api:
        result=await flow.async_step_user(data)
        api.assert_not_called()
    assert result['errors']=={'base':'required'}
    translations=await async_get_translations(hass,'en','config',{DOMAIN},config_flow=True)
    assert translations[f'component.{DOMAIN}.config.error.required']
    assert translations[f'component.{DOMAIN}.config.step.user.data.{field}']


async def test_all_flow_labels_errors_and_aborts_resolve(hass):
    translations=await async_get_translations(hass,'en','config',{DOMAIN},config_flow=True)
    strings=json.loads((Path(__file__).parents[1]/'custom_components'/DOMAIN/'strings.json').read_text())['config']
    for step,definition in strings['step'].items():
        assert translations[f'component.{DOMAIN}.config.step.{step}.title']==definition['title']
        for field,text in definition['data'].items():
            assert translations[f'component.{DOMAIN}.config.step.{step}.data.{field}']==text
    for group in ('error','abort'):
        for key,text in strings[group].items():
            assert translations[f'component.{DOMAIN}.config.{group}.{key}']==text


CONTRACT=json.loads((Path(__file__).parents[1]/'fixtures/temperature_contract.json').read_text())
@pytest.mark.parametrize('example',CONTRACT['examples'])
def test_upstream_celsius_label_contract(example):
    assert convert_temperature(example['raw'],{'v25':example['v25']})==example['expected_celsius']


@pytest.mark.parametrize('value',['2F5','C25','25CF','1C2','nan°F','inf','1e999F',True,{},None])
def test_temperature_rejects_corrupt_or_nonfinite_values(value):
    with pytest.raises(ValueError):
        convert_temperature(value,{})


@pytest.mark.parametrize('units,expected',[(METRIC_SYSTEM,25),(US_CUSTOMARY_SYSTEM,77)])
async def test_typed_sensor_units_parentage_and_live_values(hass,units,expected):
    hass.config.units=units
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'verified','token':'fake','model':'Evo Connect'})
    entry.add_to_hass(hass)
    payload={'v0':'25°F','v8':'27°F','v49':'20°F','v50':'30°F','v52':'1','v4':'50'}
    with patch('custom_components.microclimate_integration.api_client.fetch_data',new=AsyncMock(return_value=payload)) as api:
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        registry=er.async_get(hass);devices=dr.async_get(hass)
        prefix=channel_identity(entry,'Yellow')
        temp_id=registry.async_get_entity_id('sensor',DOMAIN,prefix+'_measurement_temperature')
        setpoint_id=registry.async_get_entity_id('sensor',DOMAIN,prefix+'_measurement_setpoint')
        output_id=registry.async_get_entity_id('sensor',DOMAIN,prefix+'_measurement_output')
        lower_id=registry.async_get_entity_id('sensor',DOMAIN,prefix+'_measurement_lower_alarm')
        state=hass.states.get(temp_id)
        assert float(state.state)==expected
        assert state.attributes['device_class']=='temperature'
        assert state.attributes['unit_of_measurement']==units.temperature_unit
        assert state.attributes['state_class']=='measurement'
        assert float(hass.states.get(lower_id).state)==(20 if units is METRIC_SYSTEM else 68)
        assert float(hass.states.get(output_id).state)==50
        assert hass.states.get(output_id).attributes['unit_of_measurement']=='%'
        assert 'device_class' not in hass.states.get(output_id).attributes
        climate_id=registry.async_get_entity_id('climate',DOMAIN,prefix)
        channel_device=devices.async_get(registry.async_get(temp_id).device_id)
        assert registry.async_get(climate_id).device_id==channel_device.id
        controller=devices.async_get_device_by_identifier((DOMAIN,entry.entry_id),entry.entry_id)
        assert channel_device.via_device_id==controller.id
        assert api.await_count==1
        coordinator=hass.data[DOMAIN][entry.entry_id]
        api.return_value={'v0':'nan','v52':0,'v8':1}
        await coordinator.async_refresh();await hass.async_block_till_done()
        for entity_id in (temp_id,setpoint_id,output_id,lower_id):
            assert hass.states.get(entity_id).state=='unknown'
        api.return_value=payload
        await coordinator.async_refresh();await hass.async_block_till_done()
        assert float(hass.states.get(temp_id).state)==expected
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()


@pytest.mark.parametrize('value,expected',[('0',0),('50.5',50.5),(100,100),(-1,None),(101,None),(True,None),('nan',None),(None,None)])
async def test_output_percentage_native_value(hass,value,expected):
    import logging
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
    from custom_components.microclimate_integration.sensor import MicroclimateMeasurement
    from custom_components.microclimate_integration.sensor_contract import VERIFIED_MEASUREMENTS
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'test','token':'fake','model':'Evo Connect'})
    coordinator=DataUpdateCoordinator(hass,logging.getLogger(__name__),name='test',config_entry=entry)
    coordinator.async_set_updated_data({'v4':value})
    definition=next(d for d in VERIFIED_MEASUREMENTS['Evo Connect'] if d.channel=='Yellow' and d.key=='output')
    entity=MicroclimateMeasurement(coordinator,entry,definition)
    assert entity.native_value==expected
    assert entity.native_unit_of_measurement=='%'
    assert entity.device_class is None


def test_confirmed_red_output_and_no_invented_alarm_status():
    from custom_components.microclimate_integration.sensor_contract import VERIFIED_MEASUREMENTS
    definitions=VERIFIED_MEASUREMENTS['Evo Connect 3']
    assert [d.pin for d in definitions if d.channel=='Red' and d.key=='output'] == ['v5']
    assert not [d for d in definitions if d.kind=='alarm']
    assert all(d.evidence for d in definitions)
