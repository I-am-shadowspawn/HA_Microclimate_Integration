"""Test the registered measurement implementation, not obsolete alternatives."""
import logging
import pytest
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from pytest_homeassistant_custom_component.common import MockConfigEntry
from custom_components.microclimate_integration.const import DOMAIN
from custom_components.microclimate_integration.sensor import MicroclimateMeasurement
from custom_components.microclimate_integration.sensor_contract import VERIFIED_MEASUREMENTS


@pytest.mark.parametrize('channel,pin', [('Yellow','v4'),('Red','v5'),('Blue','v6')])
@pytest.mark.parametrize('value,expected', [(50,50),(0,0),(100,100),(None,None),([],None),({},None),
                                         (True,None),('nan',None),('inf',None),('bad',None)])
async def test_registered_output(hass,channel,pin,value,expected):
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'test','model':'Evo Connect 3','token':'fake'})
    coordinator=DataUpdateCoordinator(hass,logging.getLogger(__name__),name='test',config_entry=entry)
    coordinator.async_set_updated_data({pin:value})
    definition=next(d for d in VERIFIED_MEASUREMENTS['Evo Connect 3'] if d.channel==channel and d.key=='output')
    assert definition.pin==pin
    assert MicroclimateMeasurement(coordinator,entry,definition).native_value==expected


@pytest.mark.parametrize('channel',['Yellow','Red','Blue'])
async def test_registered_alarm_threshold_missing_is_unknown(hass,channel):
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'test','model':'Evo Connect 3','token':'fake'})
    coordinator=DataUpdateCoordinator(hass,logging.getLogger(__name__),name='test',config_entry=entry)
    coordinator.async_set_updated_data({})
    definition=next(d for d in VERIFIED_MEASUREMENTS['Evo Connect 3'] if d.channel==channel and d.key=='lower_alarm')
    assert MicroclimateMeasurement(coordinator,entry,definition).native_value is None
