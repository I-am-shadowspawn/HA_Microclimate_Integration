"""Real HA controls and write lifecycle acceptance, without network/controller access."""
import asyncio
from datetime import time
from unittest.mock import AsyncMock, patch
import pytest
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry
from custom_components.microclimate_integration.const import DOMAIN, CHANNELS, MODEL_CHANNEL_OPTIONS
from custom_components.microclimate_integration import coordinator as module
from custom_components.microclimate_integration.write_contract import write_definitions
from custom_components.microclimate_integration.write_transport import UpdateResult
from custom_components.microclimate_integration.api_client import UnauthenticatedError


def payload(model='Evo Connect 3'):
    data={'v20':'01/01','v21':'00/00','v22':'00/00','v23':'00/00'}
    for field in write_definitions(model):
        if field.kind=='time':data[field.pin]='0\0'+'0\0Europe/London\0'+'0'
        elif field.kind in ('number','setpoint','ramp'):data[field.pin]=20
        elif field.kind=='enum':data[field.pin]=0
    for channel,features in MODEL_CHANNEL_OPTIONS[model].items():
        data[CHANNELS[channel]['control_pin']]=1 if features['hasTemperatureProbe'] else 0
        data[CHANNELS[channel]['timing_type']]=2
    return data


@pytest.fixture
async def runtime(hass):
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'writes','model':'Evo Connect 3','token':'fake'})
    entry.add_to_hass(hass)
    data=payload()
    async def read(*args,**kwargs):return dict(data)
    async def update(token,pin,value,**kwargs):
        data[pin]=value
        return UpdateResult('acknowledged')
    with patch('custom_components.microclimate_integration.api_client.fetch_data',side_effect=read) as reader, \
         patch('custom_components.microclimate_integration.write_transport.update_pin',side_effect=update) as writer, \
         patch.object(module,'READBACK_DELAYS',(0,0,0,0)):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        yield entry,hass.data[DOMAIN][entry.entry_id],data,reader,writer
        if entry.entry_id in hass.data[DOMAIN]:
            await hass.config_entries.async_unload(entry.entry_id)
            await hass.async_block_till_done()


def entity_id(hass,entry,platform,key):
    return er.async_get(hass).async_get_entity_id(platform,DOMAIN,f'{entry.entry_id}_write_{key}')


@pytest.mark.parametrize('platform,service,key,param,value,pin,wire',[
    ('select','select_option','Yellow_control_pin','option','cooling','v52','2'),
    ('select','select_option','Red_output_type','option','dimming','v84','1'),
    ('select','select_option','Blue_timing_type','option','Periodic','v113','3'),
    ('number','set_value','Red_lower_alarm','value',100,'v79','100'),
    ('text','set_value','season_1_start_pin','value','09/02','v20','09/02'),
])
async def test_real_services_confirm_exact_pin(hass,runtime,platform,service,key,param,value,pin,wire):
    entry,c,data,reader,writer=runtime
    eid=entity_id(hass,entry,platform,key)
    before=dict(data)
    await hass.services.async_call(platform,service,{'entity_id':eid,param:value},blocking=True)
    await hass.async_block_till_done()
    assert writer.await_count==1
    assert writer.call_args.args==('fake',pin,wire)
    assert {k for k in data if data[k]!=before[k]}=={pin}
    assert reader.await_count==3  # startup, baseline, readback
    assert c.last_write['status']=='confirmed'
    assert hass.states.get(eid).state not in ('unknown','unavailable')
    assert c.data[pin]==wire


@pytest.mark.parametrize('model',list(MODEL_CHANNEL_OPTIONS))
async def test_profile_controls_devices_defaults(hass,model):
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'profile','model':model,'token':'fake'})
    entry.add_to_hass(hass)
    with patch('custom_components.microclimate_integration.api_client.fetch_data',return_value=payload(model)):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        registry=er.async_get(hass)
        for field in write_definitions(model):
            eid=entity_id(hass,entry,field.platform,field.key)
            if field.index is not None:
                assert eid is None
                continue
            registered=registry.async_get(eid)
            assert registered.disabled_by is None
            reference=(f'{entry.entry_id}_{field.channel}_schedule' if field.channel else f'{entry.entry_id}_reported_pin_count')
            # Device grouping matches an existing observation on the same device.
            device_ids={r.device_id for r in er.async_entries_for_config_entry(registry,entry.entry_id)
                        if r.domain=='sensor' and r.unique_id.startswith(f'{entry.entry_id}_{field.channel}_' if field.channel else f'{entry.entry_id}_metadata_')}
            assert registered.device_id in device_ids
        c=hass.data[DOMAIN][entry.entry_id]
        assert c.writes_enabled
        assert await hass.config_entries.async_unload(entry.entry_id)


@pytest.mark.parametrize('key,value,code',[
    ('Yellow_period_1_setpoint',101,'invalid_number'),('Yellow_lower_alarm',float('nan'),'invalid_number'),
    ('season_1_start_pin','29/02','invalid_date'),('season_1_start_pin','00/00','invalid_date'),
    ('Yellow_period_1_time','sr','invalid_time'),('Blue_output_type','pulse','unsupported_capability'),
    ('v8',25,'unsupported_capability'),('Yellow_control_pin','bogus','invalid_option')])
async def test_invalid_no_io(runtime,key,value,code):
    _,c,_,reader,writer=runtime
    reads=reader.await_count
    with pytest.raises(HomeAssistantError) as caught:await c.async_write(key,value)
    assert caught.value.translation_key==code
    assert reader.await_count==reads and writer.await_count==0


async def test_no_change_and_live_disabled_option(hass,runtime):
    entry,c,data,reader,writer=runtime
    await c.async_write('Yellow_period_1_setpoint',20)
    assert c.last_write['status']=='confirmed_no_change' and writer.await_count==0
    hass.config_entries.async_update_entry(entry,options={'enable_writes':False})
    await hass.async_block_till_done()
    with pytest.raises(HomeAssistantError) as err:await c.async_write('Yellow_period_1_setpoint',25)
    assert err.value.translation_key=='writes_disabled'
    assert writer.await_count==0
    assert entity_id(hass,entry,'number','Yellow_period_1_setpoint') is None
    observed=er.async_get(hass).async_get_entity_id('sensor',DOMAIN,f'{entry.entry_id}_Yellow_schedule')
    assert hass.states.get(observed).state not in ('unavailable','unknown')


@pytest.mark.parametrize('outcome',['acknowledged','uncertain','rate_limited'])
async def test_ack_delayed_readback_and_uncertain_success(runtime,outcome):
    _,c,data,reader,writer=runtime
    writer.side_effect=None;writer.return_value=UpdateResult(outcome)
    count=0
    async def read(*args,**kwargs):
        nonlocal count
        count+=1
        if count==3:data['v33']=25
        return dict(data)
    reader.side_effect=read
    await c.async_write('Yellow_period_1_setpoint',25)
    assert writer.await_count==1 and count==3 and c.last_write['status']=='confirmed'


@pytest.mark.parametrize('outcome,read_fails,expected',[
    ('rejected',False,'rejected'),('acknowledged',False,'mismatch'),('uncertain',True,'uncertain'),
    ('rate_limited',False,'rate_limited')])
async def test_failure_never_optimistic_or_retried(runtime,outcome,read_fails,expected):
    _,c,data,reader,writer=runtime
    writer.side_effect=None;writer.return_value=UpdateResult(outcome)
    calls=0
    async def read(*args,**kwargs):
        nonlocal calls
        calls+=1
        if read_fails and calls>1:raise TimeoutError('fake-secret-url')
        return dict(data)
    reader.side_effect=read
    with pytest.raises(HomeAssistantError) as caught:await c.async_write('Yellow_period_1_setpoint',25)
    assert caught.value.translation_key==expected
    assert writer.await_count==1 and c.data['v33']==20
    assert 'fake-secret' not in str(caught.value)


@pytest.mark.parametrize('phase',['baseline','update','readback'])
async def test_authentication_recovery(runtime,phase):
    entry,c,data,reader,writer=runtime
    if phase=='update':writer.side_effect=None;writer.return_value=UpdateResult('invalid_auth')
    elif phase=='baseline':reader.side_effect=UnauthenticatedError()
    else:reader.side_effect=[dict(data),UnauthenticatedError()]
    with patch.object(entry,'async_start_reauth') as reauth:
        with pytest.raises(HomeAssistantError) as err:await c.async_write('Yellow_period_1_setpoint',25)
        assert err.value.translation_key=='invalid_auth'
        reauth.assert_called_once()
    assert writer.await_count==(0 if phase=='baseline' else 1)


async def test_external_context_change_rejected(runtime):
    _,c,data,reader,writer=runtime
    data['v52']=0
    with pytest.raises(HomeAssistantError) as err:await c.async_write('Yellow_period_1_setpoint',25)
    assert err.value.translation_key=='stale_context'
    assert writer.await_count==0 and c.data['v52']==0


async def test_serialization_polling_and_latest_credential(hass,runtime):
    entry,c,data,reader,writer=runtime
    entered=asyncio.Event();release=asyncio.Event()
    async def update(token,pin,value,**kwargs):
        if pin=='v33':entered.set();await release.wait()
        data[pin]=value
        return UpdateResult('acknowledged')
    writer.side_effect=update
    first=asyncio.create_task(c.async_write('Yellow_period_1_setpoint',25))
    await entered.wait()
    second=asyncio.create_task(c.async_write('Red_lower_alarm',30))
    poll=asyncio.create_task(c.async_refresh())
    await asyncio.sleep(0)
    assert writer.await_count==1 and reader.await_count==2
    release.set();await asyncio.gather(first,second,poll)
    assert writer.await_count==2 and c.data['v33']=='25' and c.data['v79']=='30'
    assert not c._write_tasks
    # A queued command takes the current entry credential; no stale token closure.
    await c._write_lock.acquire()
    queued=asyncio.create_task(c.async_write('Red_lower_alarm',31));await asyncio.sleep(0)
    hass.config_entries.async_update_entry(entry,data={**entry.data,'token':'newfake'})
    c._write_lock.release();await queued
    assert writer.call_args.args[0]=='newfake'


async def test_queued_disable_and_unload_cancel(hass,runtime):
    entry,c,data,reader,writer=runtime
    await c._write_lock.acquire()
    queued=asyncio.create_task(c.async_write('Yellow_period_1_setpoint',25));await asyncio.sleep(0)
    hass.config_entries.async_update_entry(entry,options={'enable_writes':False})
    c._write_lock.release()
    with pytest.raises(HomeAssistantError) as err:await queued
    assert err.value.translation_key=='writes_disabled' and writer.await_count==0
    hass.config_entries.async_update_entry(entry,options={'enable_writes':True})
    entered=asyncio.Event()
    async def slow(*args,**kwargs):entered.set();await asyncio.Event().wait()
    writer.side_effect=slow
    active=asyncio.create_task(c.async_write('Yellow_period_1_setpoint',25));await entered.wait()
    queued=asyncio.create_task(c.async_write('Red_lower_alarm',30));await asyncio.sleep(0)
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert active.cancelled() and queued.cancelled() and not c._write_tasks
    assert writer.await_count==1 and c.closed
    assert c.last_write["status"]=="uncertain"
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert writer.await_count==1  # No replay on reload.


async def test_diagnostic_registry_choices_survive_setup_and_reload(hass):
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'diagnostics','model':'Evo Connect','token':'fake'})
    entry.add_to_hass(hass);reg=er.async_get(hass)
    for pin,disabler in [('v0',er.RegistryEntryDisabler.INTEGRATION),('v4',er.RegistryEntryDisabler.USER),('v8',None)]:
        reg.async_get_or_create('sensor',DOMAIN,f'{entry.entry_id}_Yellow_raw_{pin}',config_entry=entry,
                               entity_category=EntityCategory.DIAGNOSTIC,disabled_by=disabler)
    with patch('custom_components.microclimate_integration.api_client.fetch_data',return_value=payload('Evo Connect')):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        for _ in range(2):
            for pin,disabled in [('v0',er.RegistryEntryDisabler.INTEGRATION),('v4',er.RegistryEntryDisabler.USER),('v8',None)]:
                eid=reg.async_get_entity_id('sensor',DOMAIN,f'{entry.entry_id}_Yellow_raw_{pin}')
                assert reg.async_get(eid).disabled_by==disabled
            assert await hass.config_entries.async_reload(entry.entry_id)
            await hass.async_block_till_done()
        await hass.config_entries.async_unload(entry.entry_id)


@pytest.mark.parametrize('phase',['baseline','dispatch','readback'])
async def test_deadline_and_no_retry(runtime,phase):
    _,c,data,reader,writer=runtime
    async def stalled(*args,**kwargs):await asyncio.Event().wait()
    if phase=='baseline':reader.side_effect=stalled
    elif phase=='dispatch':writer.side_effect=stalled
    else:
        first=True
        async def read(*args,**kwargs):
            nonlocal first
            if first:first=False;return dict(data)
            await asyncio.Event().wait()
        reader.side_effect=read
    with patch.object(module,'OPERATION_TIMEOUT',0.02):
        with pytest.raises(HomeAssistantError) as err:await c.async_write('Yellow_period_1_setpoint',25)
    assert err.value.translation_key==('read_failed' if phase=='baseline' else 'uncertain')
    assert writer.await_count==(0 if phase=='baseline' else 1)
    assert not c._write_tasks and not c._io_lock.locked()


async def test_poll_started_first_cannot_overwrite_newer_write(runtime):
    _,c,data,reader,writer=runtime
    entered=asyncio.Event();release=asyncio.Event();old=dict(data)
    async def slow_poll(*args,**kwargs):
        reader.side_effect=lambda *a,**kw:dict(data)
        entered.set();await release.wait();return old
    reader.side_effect=slow_poll
    poll=asyncio.create_task(c.async_refresh());await entered.wait()
    edit=asyncio.create_task(c.async_write('Yellow_period_1_setpoint',25));await asyncio.sleep(0)
    assert writer.await_count==0
    release.set();await asyncio.gather(poll,edit)
    assert c.data['v33']=='25' and c.last_write['status']=='confirmed'


async def test_token_or_mode_changed_during_request(hass,runtime):
    entry,c,data,reader,writer=runtime
    async def changed(*args,**kwargs):
        hass.config_entries.async_update_entry(entry,data={**entry.data,'token':'changed'})
        return dict(data)
    reader.side_effect=changed
    with pytest.raises(HomeAssistantError) as err:await c.async_write('Yellow_period_1_setpoint',25)
    assert err.value.translation_key=='stale_context' and writer.await_count==0
    reader.side_effect=lambda *a,**kw:dict(data)
    async def update(*args,**kwargs):
        data['v52']=0;data['v33']=25
        return UpdateResult('acknowledged')
    writer.side_effect=update
    with pytest.raises(HomeAssistantError) as err:await c.async_write('Yellow_period_1_setpoint',25)
    assert err.value.translation_key=='stale_context' and writer.await_count==1
    assert c.data['v33']==25 and c.data['v52']==0


async def test_missing_readback_pin_and_clamping(runtime):
    _,c,data,reader,writer=runtime
    async def update(*args,**kwargs):
        data.pop('v33');return UpdateResult('acknowledged')
    writer.side_effect=update
    with pytest.raises(HomeAssistantError) as err:await c.async_write('Yellow_period_1_setpoint',25)
    assert err.value.translation_key=='mismatch' and 'v33' not in c.data
    data['v33']=20;await c.async_refresh()
    async def clamp(*args,**kwargs):
        data['v33']=24.9;return UpdateResult('acknowledged')
    writer.side_effect=clamp
    with pytest.raises(HomeAssistantError) as err:await c.async_write('Yellow_period_1_setpoint',25)
    assert err.value.translation_key=='mismatch' and c.data['v33']==24.9


async def test_separate_entries_independent(hass,runtime):
    entry,c,data,reader,writer=runtime
    other=MockConfigEntry(domain=DOMAIN,data={'evo_device':'other','model':'Evo Connect 3','token':'other'})
    other.add_to_hass(hass)
    assert await hass.config_entries.async_setup(other.entry_id);await hass.async_block_till_done()
    entered=asyncio.Event();release=asyncio.Event()
    async def update(token,pin,value,**kwargs):
        if token=='fake':entered.set();await release.wait()
        data[pin]=value;return UpdateResult('acknowledged')
    writer.side_effect=update
    first=asyncio.create_task(c.async_write('Yellow_period_1_setpoint',25));await entered.wait()
    await hass.data[DOMAIN][other.entry_id].async_write('Red_lower_alarm',30)
    assert not first.done() and writer.await_count==2
    release.set();await first
    await hass.config_entries.async_unload(other.entry_id)


async def test_startup_platform_failure_cleans_up(hass):
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'fail','model':'Evo Connect','token':'fake'})
    entry.add_to_hass(hass)
    created=[]
    original=module.MicroclimateCoordinator
    def factory(*args):
        c=original(*args);created.append(c);return c
    forward=hass.config_entries.async_forward_entry_setups
    async def fail_after_setup(entry,platforms):
        await forward(entry,platforms)
        raise RuntimeError('simulated platform forwarding failure')
    with patch('custom_components.microclimate_integration.api_client.fetch_data',return_value=payload('Evo Connect')), \
         patch('custom_components.microclimate_integration.MicroclimateCoordinator',side_effect=factory), \
         patch.object(hass.config_entries,'async_forward_entry_setups',side_effect=fail_after_setup):
        assert not await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    assert entry.entry_id not in hass.data[DOMAIN]
    assert created[0].closed and not created[0]._listeners and created[0]._unsub_refresh is None


@pytest.mark.parametrize('model',list(MODEL_CHANNEL_OPTIONS))
async def test_every_field_dispatch_and_readback(hass,model):
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'allfields','model':model,'token':'fake'})
    entry.add_to_hass(hass)
    data=payload(model)
    async def update(token,pin,value,**kwargs):data[pin]=value;return UpdateResult('acknowledged')
    with patch('custom_components.microclimate_integration.api_client.fetch_data',side_effect=lambda *a,**k:dict(data)), \
         patch('custom_components.microclimate_integration.write_transport.update_pin',side_effect=update) as writer:
        assert await hass.config_entries.async_setup(entry.entry_id);await hass.async_block_till_done()
        c=hass.data[DOMAIN][entry.entry_id]
        for field in write_definitions(model):
            data.clear();data.update(payload(model));await c.async_refresh();writer.reset_mock()
            if field.kind=='enum':
                candidates=[label for code,label in field.options if int(code)!=data[field.pin]]
                if not candidates:continue  # Evo I Blue fixed-only selector is a no-op.
                value=candidates[0]
            elif field.kind=='time':value=time(1,2,3)
            elif field.kind=='date':value='09/02'
            elif field.kind=='ramp':value=45
            else:value=24.125
            await c.async_write(field.key,value)
            assert writer.await_count==1 and writer.call_args.args[1]==field.pin
            assert c.last_write['status']=='confirmed'
        await hass.config_entries.async_unload(entry.entry_id)


async def test_units_switch_and_unrounded_observation(hass,runtime,hass_admin_user):
    from homeassistant.helpers import device_registry as dr
    from custom_components.microclimate_integration.card_model import snapshot
    entry,c,data,reader,writer=runtime
    device=dr.async_get(hass).async_get_device_by_identifier((DOMAIN,f'{entry.entry_id}_Yellow'),entry.entry_id)
    def field():
        return next(f for f in snapshot(hass,c,'Yellow',device,hass_admin_user)['fields'] if f['key']=='Yellow_period_1_setpoint')
    data['v33']='25.125°F';await c.async_refresh()
    assert field()['value']==25.125 and field()['unit']=='°C'
    data['v52']=0;data['v33']=33.375;await c.async_refresh()
    assert field()['unit']=='%' and field()['value']==33.375
    await c.async_write('Yellow_period_1_setpoint',45.125)
    assert writer.call_args.args[1:]==('v33','45.125')
    data['v33']=100.04;await c.async_refresh()
    assert field()['value'] is None


async def test_us_display_converts_once(hass):
    from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM
    hass.config.units=US_CUSTOMARY_SYSTEM
    entry=MockConfigEntry(domain=DOMAIN,data={'evo_device':'units','model':'Evo Connect 2','token':'fake'})
    entry.add_to_hass(hass);data=payload('Evo Connect 2')
    async def update(token,pin,value,**kwargs):data[pin]=value;return UpdateResult('acknowledged')
    with patch('custom_components.microclimate_integration.api_client.fetch_data',side_effect=lambda *a,**k:dict(data)), \
         patch('custom_components.microclimate_integration.write_transport.update_pin',side_effect=update) as writer:
        assert await hass.config_entries.async_setup(entry.entry_id);await hass.async_block_till_done()
        eid=entity_id(hass,entry,'number','Yellow_lower_alarm')
        assert hass.states.get(eid).attributes['unit_of_measurement']=='°F'
        assert float(hass.states.get(eid).state)==68
        await hass.services.async_call('number','set_value',{'entity_id':eid,'value':77},blocking=True)
        assert writer.call_args.args[1:]==('v49','25')
        await hass.config_entries.async_unload(entry.entry_id)


async def test_failed_unload_restores_working_poll_and_controls(hass,runtime):
    entry,c,data,reader,writer=runtime
    from custom_components.microclimate_integration import async_unload_entry
    with patch.object(hass.config_entries,'async_unload_platforms',return_value=False):
        assert not await async_unload_entry(hass,entry)
    assert not c.closed
    await c.async_write('Yellow_period_1_setpoint',25)
    assert c.data['v33']=='25'
    data['v33']=26;await c.async_request_refresh()
    assert c.data['v33']==26


async def test_unload_cancels_inflight_poll_without_late_publication(hass,runtime):
    entry,c,data,reader,writer=runtime
    entered=asyncio.Event()
    async def slow(*args,**kwargs):
        entered.set();await asyncio.Event().wait()
        return {**data,'v33':99}
    reader.side_effect=slow
    poll=asyncio.create_task(c.async_refresh());await entered.wait()
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert poll.cancelled() and not c._refresh_tasks
    assert c.data['v33']==20 and not c._listeners
    assert c._unsub_refresh is None and writer.await_count==0


async def test_reauth_during_readback_cannot_publish_old_credential_snapshot(hass,runtime):
    entry,c,data,reader,writer=runtime
    reads=0
    async def read(*args,**kwargs):
        nonlocal reads
        reads+=1
        if reads==2:
            hass.config_entries.async_update_entry(entry,data={**entry.data,'token':'newtoken'})
        return dict(data)
    reader.side_effect=read
    with pytest.raises(HomeAssistantError) as err:await c.async_write('Yellow_period_1_setpoint',25)
    assert err.value.translation_key=='uncertain'
    assert writer.await_count==1 and c.data['v33']==20


@pytest.mark.parametrize('channel,pin',[('Yellow','v48'),('Red','v78')])
async def test_ramp_entity_and_service(hass,runtime,channel,pin):
    entry,c,data,reader,writer=runtime
    eid=entity_id(hass,entry,'number',f'{channel}_ramp_time')
    state=hass.states.get(eid)
    assert state.attributes['unit_of_measurement']=='min'
    assert state.attributes['device_class']=='duration'
    assert (state.attributes['min'],state.attributes['max'],state.attributes['step'])==(0,240,1)
    for value in (240,0):
        await hass.services.async_call('number','set_value',{'entity_id':eid,'value':value},blocking=True)
        assert writer.call_args.args[1:]==(pin,str(value))
        assert c.data[pin]==str(value)
    count=writer.await_count
    with pytest.raises(HomeAssistantError) as err:await c.async_write(f'{channel}_ramp_time',1.5)
    assert err.value.translation_key=='invalid_ramp' and writer.await_count==count


async def test_season_order_fresh_baseline_and_readback(hass,runtime):
    entry,c,data,reader,writer=runtime
    data.update(dict(zip(('v20','v21','v22','v23'),('09/10','01/01','01/06','01/07'))))
    await c.async_refresh()
    await c.async_write('season_1_start_pin','10/10')
    assert writer.call_args.args[1:]==('v20','10/10')
    writes=writer.await_count
    with pytest.raises(HomeAssistantError) as err:await c.async_write('season_2_start_pin','10/06')
    assert err.value.translation_key=='invalid_season_order' and writer.await_count==writes
    # A sibling changes after the UI snapshot: fresh-baseline validation stops the edit.
    data['v21']='10/06'
    with pytest.raises(HomeAssistantError) as err:await c.async_write('season_1_start_pin','11/10')
    assert err.value.translation_key=='invalid_season_order' and writer.await_count==writes
    data['v21']='01/01';await c.async_refresh()
    async def concurrent_app(token,pin,value,**kwargs):
        data[pin]=value;data['v21']='10/06'
        return UpdateResult('acknowledged')
    writer.side_effect=concurrent_app
    with pytest.raises(HomeAssistantError) as err:await c.async_write('season_1_start_pin','12/10')
    assert err.value.translation_key=='invalid_season_order'
    assert c.data['v20']=='12/10' and c.data['v21']=='10/06'  # Observed, never rolled back.


async def test_time_component_edits_are_two_complete_serialized_updates(runtime):
    _,c,data,reader,writer=runtime
    await c.async_write('Yellow_period_1_time',time(7,0))
    await c.async_write('Yellow_period_1_time',time(7,30))
    assert writer.await_count==2
    assert [call.args[2].split('\0')[0] for call in writer.call_args_list]==['25200','27000']
    assert all(call.args[1]=='v32' for call in writer.call_args_list)
    # Already equal final times incur no third update.
    await c.async_write('Yellow_period_1_time',time(7,30))
    assert writer.await_count==2


async def test_queued_season_edits_revalidate_combined_calendar(runtime):
    _,c,data,reader,writer=runtime
    data.update(dict(zip(('v20','v21','v22','v23'),('01/01','01/04','01/07','01/10'))))
    await c.async_refresh()
    entered=asyncio.Event();release=asyncio.Event()
    async def slow(token,pin,value,**kwargs):
        entered.set();await release.wait();data[pin]=value
        return UpdateResult('acknowledged')
    writer.side_effect=slow
    first=asyncio.create_task(c.async_write('season_2_start_pin','01/06'))
    await entered.wait()
    # This is valid against the invocation snapshot, but not after the first edit.
    second=asyncio.create_task(c.async_write('season_3_start_pin','01/05'))
    await asyncio.sleep(0);release.set();await first
    with pytest.raises(HomeAssistantError) as err:await second
    assert err.value.translation_key=='invalid_season_order'
    assert writer.await_count==1 and data['v21']=='01/06' and data['v22']=='01/07'
