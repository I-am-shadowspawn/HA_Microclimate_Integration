"""Fresh-install compact exposure and aggregate card contract."""
from datetime import time
from unittest.mock import patch
import pytest
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry
from custom_components.microclimate_integration.const import DOMAIN, MODEL_CHANNEL_OPTIONS
from test_write_runtime import payload

@pytest.mark.parametrize('model', MODEL_CHANNEL_OPTIONS)
async def test_inventory(hass,model):
    entry=MockConfigEntry(domain=DOMAIN,data={'model':model,'evo_device':'inventory','token':'fake'})
    entry.add_to_hass(hass)
    with patch('custom_components.microclimate_integration.api_client.fetch_data',return_value=payload(model)) as reader:
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        rows=er.async_entries_for_config_entry(er.async_get(hass),entry.entry_id)
        expected={'Evo Connect':59,'Evo Connect 2':66,'Evo Connect 3':93}[model]
        assert len(rows)==expected
        assert sum(hass.states.get(e.entity_id) is not None for e in rows)==expected
        assert not any('_schedule_period_' in e.unique_id or ('_write_' in e.unique_id and '_period_' in e.unique_id) for e in rows)
        assert not any(e.domain=='time' for e in rows)
        assert reader.call_count==1
        await hass.config_entries.async_unload(entry.entry_id)

from unittest.mock import Mock
from custom_components.microclimate_integration.card_model import snapshot, binding, field_access, resolve
from custom_components.microclimate_integration.card_api import CardAPI
from custom_components.microclimate_integration.write_contract import definition_for, WriteValidationError
from test_card_contract import context, wait_job
from test_write_runtime import runtime

async def test_anchor_only_permission_and_rename(hass,runtime,hass_admin_user):
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    anchor=next(f['entity_id'] for f in view['fields'] if f['index'])
    user=Mock(id='schedule-user')
    user.permissions.check_entity.side_effect=lambda eid,policy:eid==anchor
    projection=snapshot(hass,c,'Yellow',device,user)
    assert len(projection['fields'])==16
    assert all(f['entity_id']==anchor and f['writable'] and f['authorization_scope']=='channel_schedule' for f in projection['fields'])
    assert not projection['observations']
    api=CardAPI(hass);job=await wait_job(hass,api,await api.save(msg,user))
    assert job['status']=='succeeded'
    registry=er.async_get(hass)
    registry.async_update_entity(anchor,new_entity_id='sensor.renamed_schedule')
    user.permissions.check_entity.side_effect=lambda eid,policy:eid=='sensor.renamed_schedule'
    assert all(f['entity_id']=='sensor.renamed_schedule' for f in snapshot(hass,c,'Yellow',device,user)['fields'])
    assert api.find_job({'operation_id':job['operation_id']},user)['status']=='succeeded'

async def test_read_only_anchor_cannot_save(hass,runtime,hass_admin_user):
    from homeassistant.auth.permissions.const import POLICY_READ
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    user=Mock(id='readonly');user.permissions.check_entity.side_effect=lambda eid,policy:policy==POLICY_READ
    assert all(not f['writable'] for f in snapshot(hass,c,'Yellow',device,user)['fields'])
    with pytest.raises(WriteValidationError,match='control_denied'):await CardAPI(hass).save(msg,user)
    assert writer.await_count==0

@pytest.mark.parametrize('damage',['missing','disabled','foreign','foreign_entry','device_disabled'])
async def test_invalid_schedule_anchor_fails_closed(hass,runtime,hass_admin_user,damage):
    from homeassistant.helpers import device_registry as dr
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    field=definition_for('Evo Connect 3','Yellow_period_1_time')
    anchor=binding(hass,c,field)
    registry=er.async_get(hass)
    if damage=='missing':registry.async_remove(anchor.entity_id)
    elif damage=='disabled':registry.async_update_entity(anchor.entity_id,disabled_by=er.RegistryEntryDisabler.USER)
    elif damage=='foreign':
        other=dr.async_get(hass).async_get_device_by_identifier((DOMAIN,f'{c.entry.entry_id}_Blue'),c.entry.entry_id)
        registry.async_update_entity(anchor.entity_id,device_id=other.id)
    elif damage=='foreign_entry':
        other_entry=MockConfigEntry(domain=DOMAIN,data={'model':'Evo Connect','evo_device':'other','token':'different-fake'})
        other_entry.add_to_hass(hass)
        other=dr.async_get(hass).async_get_or_create(config_entry_id=other_entry.entry_id,identifiers={(DOMAIN,f'{other_entry.entry_id}_Yellow')})
        registry.async_update_entity(anchor.entity_id,device_id=other.id)
    else:dr.async_get(hass).async_update_device(device.id,disabled_by=dr.DeviceEntryDisabler.USER)
    assert not field_access(hass,c,field,hass_admin_user,control=True)
    with pytest.raises(WriteValidationError):await CardAPI(hass).save(msg,hass_admin_user)
    assert writer.await_count==0

async def test_revocation_stops_next_pin_and_hides_recovery(hass,runtime,hass_admin_user):
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    user=Mock(id='revoked');permitted=True
    anchor=next(f['entity_id'] for f in view['fields'] if f['index'])
    user.permissions.check_entity.side_effect=lambda eid,policy:permitted or eid!=anchor
    original=writer.side_effect
    async def update(*args,**kwargs):
        nonlocal permitted
        result=await original(*args,**kwargs);permitted=False
        return result
    writer.side_effect=update
    api=CardAPI(hass);result=await api.save(msg,user);job=await wait_job(hass,api,result)
    assert job['status']=='partial' and job['reason']=='control_denied' and writer.await_count==1
    with pytest.raises(WriteValidationError,match='control_denied'):api.find_job(result,user)
    connection=Mock(user=user,subscriptions={})
    await api.handle(connection,{'id':1,'device_id':device.id,'request_id':msg['request_id']},'request')
    connection.send_error.assert_called_once()
    connection.send_result.assert_not_called()

async def test_non_schedule_permissions_remain_independent(hass,runtime,hass_admin_user):
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    anchor=next(f['entity_id'] for f in view['fields'] if f['index'])
    user=Mock(id='schedule-only');user.permissions.check_entity.side_effect=lambda eid,policy:eid==anchor
    for key in ('Yellow_lower_alarm','season_1_start_pin'):
        assert not field_access(hass,c,definition_for('Evo Connect 3',key),user,control=True)
    msg['patch']={'kind':'channel','fields':{'Yellow_lower_alarm':30}}
    with pytest.raises(WriteValidationError,match='control_denied'):await CardAPI(hass).save(msg,user)
    assert writer.await_count==0

async def test_hidden_anchor_is_usable_but_disabled_completed_job_is_not(hass,runtime,hass_admin_user):
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    anchor=next(f['entity_id'] for f in view['fields'] if f['index'])
    registry=er.async_get(hass);registry.async_update_entity(anchor,hidden_by=er.RegistryEntryHider.USER)
    api=CardAPI(hass);result=await api.save(msg,hass_admin_user)
    assert (await wait_job(hass,api,result))['status']=='succeeded'
    registry.async_update_entity(anchor,disabled_by=er.RegistryEntryDisabler.USER)
    with pytest.raises(WriteValidationError,match='control_denied'):api.find_job(result,hass_admin_user)

@pytest.mark.parametrize('key,value,pin,wire',[
    ('Yellow_period_1_setpoint',25.125,'v33','25.125'),
    ('Blue_period_1_time',time(23,59,59),'v92','86399\0'+'86399\0Europe/London\0'+'0'),
])
async def test_internal_schedule_writes_keep_exact_wire_without_entities(runtime,key,value,pin,wire):
    entry,c,data,reader,writer=runtime
    await c.async_write(key,value)
    assert writer.call_args.args==('fake',pin,wire)
    assert c.data[pin]==wire and reader.await_count==3

async def test_supplied_day_night_capture_keeps_stored_slots_without_activation(hass,hass_admin_user):
    import json
    from pathlib import Path
    from homeassistant.helpers import device_registry as dr
    raw=json.loads((Path(__file__).parents[1]/'fixtures/compact-day-night-evo-ii.json').read_text())
    entry=MockConfigEntry(domain=DOMAIN,data={'model':'Evo Connect 2','evo_device':'capture','token':'fake'})
    entry.add_to_hass(hass)
    with patch('custom_components.microclimate_integration.api_client.fetch_data',return_value=raw):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        c=hass.data[DOMAIN][entry.entry_id]
        device=dr.async_get(hass).async_get_device_by_identifier((DOMAIN,f'{entry.entry_id}_Blue'),entry.entry_id)
        view=snapshot(hass,c,'Blue',device,hass_admin_user)
        fields={f['key']:f for f in view['fields']}
        assert fields['Blue_period_1_time']['value']==26700
        assert fields['Blue_period_1_setpoint']['value']==31.5
        assert fields['Blue_period_2_time']['value']==56700
        assert fields['Blue_period_2_setpoint']['value']==25
        assert all(not fields[f'Blue_period_{i}_time']['writable'] for i in range(3,9))
        eid=er.async_get(hass).async_get_entity_id('sensor',DOMAIN,f'{entry.entry_id}_Blue_schedule')
        state=hass.states.get(eid)
        assert len(state.attributes['periods'])==8
        assert state.attributes['interpretation']=='reported_configuration_not_active_schedule'
        assert state.attributes['activation']=='unverified'
        await hass.config_entries.async_unload(entry.entry_id)

async def test_permission_revoked_during_final_baseline_prevents_dispatch(hass,runtime,hass_admin_user):
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    reader=runtime[3];user=Mock(id='revoked-before-dispatch');permitted=True
    user.permissions.check_entity.side_effect=lambda eid,policy:permitted
    original=reader.side_effect
    async def read(*args,**kwargs):
        nonlocal permitted
        if reader.await_count==4:permitted=False
        return await original(*args,**kwargs)
    reader.side_effect=read
    api=CardAPI(hass);job=await wait_job(hass,api,await api.save(msg,user))
    assert job['status']=='failed' and job['reason']=='control_denied'
    assert writer.await_count==0 and reader.await_count==4
