"""Whole-schedule shifts, conflicts and permission boundaries; no device traffic."""
import asyncio
from unittest.mock import Mock
from uuid import uuid4
import pytest
from homeassistant.helpers import device_registry as dr, entity_registry as er
from custom_components.microclimate_integration.const import DOMAIN
from custom_components.microclimate_integration.card_api import CardAPI
from custom_components.microclimate_integration.card_model import snapshot, revision, value_of, resolve
from custom_components.microclimate_integration.edit_plan import build_plan
from custom_components.microclimate_integration.write_contract import definition_for, WriteValidationError
from test_write_runtime import runtime, payload


def populate(data, count=8, channel='Yellow'):
    for i in range(1,9):
        t=definition_for('Evo Connect 3',f'{channel}_period_{i}_time')
        v=definition_for('Evo Connect 3',f'{channel}_period_{i}_setpoint')
        seconds=i*3600 if i<=count else 0
        data[t.pin]=f'{seconds}\0{seconds}\0Europe/London\0'+'0'
        data[v.pin]=20+i if i<=count else 0


def points(count):
    return [{'seconds':i*3600,'target_native':20+i} for i in range(1,count+1)]


def patch(points):
    return {'kind':'channel','fields':{},'schedule':{'mode':'Multi','points':points}}


@pytest.mark.parametrize('count',range(3,9))
def test_all_delete_positions(count):
    data=payload();populate(data,count)
    for k in range(count):
        desired=points(count);desired.pop(k)
        plan=build_plan('Evo Connect 3','Yellow',data,patch(desired))
        for i,p in enumerate(desired,1):
            assert value_of(definition_for('Evo Connect 3',f'Yellow_period_{i}_setpoint'),plan.expected)==p['target_native']
        assert value_of(definition_for('Evo Connect 3',f'Yellow_period_{count}_setpoint'),plan.expected)==0
        assert list(dict.fromkeys(s.field.index for s in plan.steps))==list(range(k+1,count+1))


@pytest.mark.parametrize('count',range(2,8))
def test_all_insert_positions(count):
    data=payload();populate(data,count)
    for k in range(count+1):
        desired=points(count);desired.insert(k,{'seconds':k*3600+1800,'target_native':45})
        plan=build_plan('Evo Connect 3','Yellow',data,patch(desired))
        assert list(dict.fromkeys(s.field.index for s in plan.steps))==list(range(count+1,k+1,-1))+[k+1]
        assert value_of(definition_for('Evo Connect 3',f'Yellow_period_{k+1}_setpoint'),plan.expected)==45


@pytest.mark.parametrize('desired',[points(1),points(9),[{'seconds':0,'target_native':0},*points(2)],points(2)[::-1],[{'seconds':3600,'target_native':float('nan')},points(2)[1]]])
def test_invalid_multi_rejected(desired):
    data=payload();populate(data)
    with pytest.raises(WriteValidationError):build_plan('Evo Connect 3','Yellow',data,patch(desired))


def test_time_templates_cannot_move_opaque_flags():
    data=payload();populate(data,3);data['v34']=data['v34']+'\0extra'
    with pytest.raises(WriteValidationError,match='incompatible_time_templates'):
        build_plan('Evo Connect 3','Yellow',data,patch(points(2)))


def test_root_date_path():
    data=payload();data.update(v20='09/10',v21='01/01',v22='01/06',v23='01/07')
    plan=build_plan('Evo Connect 3',None,data,{'kind':'season_dates','fields':{'season_1_start_pin':'10/10','season_2_start_pin':'02/01'}})
    assert len(plan.steps)==2
    with pytest.raises(WriteValidationError):build_plan('Evo Connect 3',None,data,{'kind':'season_dates','fields':{'season_2_start_pin':'01/13'}})


async def context(hass,runtime,user):
    entry,c,data,reader,writer=runtime
    populate(data,4);c._publish(dict(data))
    device=dr.async_get(hass).async_get_device_by_identifier((DOMAIN,f'{entry.entry_id}_Yellow'),entry.entry_id)
    view=snapshot(hass,c,'Yellow',device,user)
    msg={'device_id':device.id,'schema_version':1,'base_revision':view['revision'],
         'runtime_generation':view['runtime_generation'],'request_id':str(uuid4()),'patch':patch(points(3))}
    return c,data,writer,device,view,msg


async def wait_job(hass,api,result):
    for _ in range(500):
        await asyncio.sleep(0)
        job=api.jobs[result['operation_id']]
        if job['status'] in ('succeeded','failed','partial','uncertain','stopped'):return job
    pytest.fail('job did not finish')


async def test_save_full_prefix_and_idempotency(hass,runtime,hass_admin_user):
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    api=CardAPI(hass);result=await api.save(msg,hass_admin_user)
    assert await api.save(msg,hass_admin_user)==result
    job=await wait_job(hass,api,result)
    assert job['status']=='succeeded',job
    assert job['confirmed']==2 and data['v39']=='0' and data['v38'].startswith('0\0')
    count=writer.await_count
    assert await api.save(msg,hass_admin_user)==result and writer.await_count==count
    msg['patch']={'kind':'channel','fields':{'Yellow_lower_alarm':40}}
    with pytest.raises(WriteValidationError,match='request_id_reused'):await api.save(msg,hass_admin_user)


async def test_revision_rename_and_fresh_conflict(hass,runtime,hass_admin_user):
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    previous=revision(c,'Yellow');c.data['v0']=99;c.data['v4']=66
    assert revision(c,'Yellow')==previous and resolve(hass,device.id)[1]=='Yellow'
    registry=er.async_get(hass);entity=view['fields'][0]['entity_id']
    registry.async_update_entity(entity,new_entity_id='text.my_renamed_season')
    assert snapshot(hass,c,'Yellow',device,hass_admin_user)['fields'][0]['entity_id']=='text.my_renamed_season'
    data['v49']=99
    api=CardAPI(hass);job=await wait_job(hass,api,await api.save(msg,hass_admin_user))
    assert job['reason']=='conflict' and writer.await_count==0


async def test_permissions_and_forged_fields(hass,runtime,hass_admin_user):
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    denied=Mock(id='restricted');denied.permissions.check_entity.return_value=False
    with pytest.raises(WriteValidationError,match='read_denied'):snapshot(hass,c,'Yellow',device,denied)
    with pytest.raises(WriteValidationError,match='control_denied'):await CardAPI(hass).save(msg,denied)
    msg['patch']={'kind':'channel','fields':{'Blue_lower_alarm':22}}
    with pytest.raises(WriteValidationError):await CardAPI(hass).save(msg,hass_admin_user)
    assert writer.await_count==0


async def test_partial_failure_stops(hass,runtime,hass_admin_user):
    from custom_components.microclimate_integration.write_transport import UpdateResult
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    original=writer.side_effect
    async def update(*args,**kwargs):
        if writer.await_count==2:return UpdateResult('rejected')
        return await original(*args,**kwargs)
    writer.side_effect=update
    api=CardAPI(hass);job=await wait_job(hass,api,await api.save(msg,hass_admin_user))
    assert job['status']=='partial' and job['confirmed']==1 and writer.await_count==2
    assert job['fields'][1]['status']=='failed'


async def test_websocket_projection_subscription_and_schema(hass,runtime,hass_ws_client,hass_admin_user):
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    client=await hass_ws_client(hass)
    await client.send_json({'id':1,'type':'microclimate_integration/card/list'})
    result=await client.receive_json()
    assert result['success'] and any(d['device_id']==device.id for d in result['result'])
    await client.send_json({'id':2,'type':'microclimate_integration/card/subscribe','device_id':device.id})
    assert (await client.receive_json())['success']
    event=await client.receive_json()
    assert event['event']['device_id']==device.id and 'fake' not in str(event)
    await client.send_json({'id':3,'type':'unsubscribe_events','subscription':2})
    assert (await client.receive_json())['success']
    await client.send_json({'id':4,'type':'microclimate_integration/card/save',**msg,'extra':True})
    assert not (await client.receive_json())['success']
    assert writer.await_count==0


async def test_stop_between_pairs_and_service_lock(hass,runtime,hass_admin_user):
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    api=CardAPI(hass)
    original=writer.side_effect
    async def update(*args,**kwargs):
        for job in api.jobs.values():job['stop']=True
        return await original(*args,**kwargs)
    writer.side_effect=update
    result=await api.save(msg,hass_admin_user)
    with pytest.raises(WriteValidationError,match='busy'):
        await api.save({**msg,'request_id':str(uuid4())},hass_admin_user)
    job=await wait_job(hass,api,result)
    assert job['status']=='stopped' and writer.await_count==1
    assert not c._write_lock.locked() and not c._io_lock.locked()


async def test_unload_cancels_during_second_pin(hass,runtime,hass_admin_user):
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    original=writer.side_effect;started=asyncio.Event();blocked=asyncio.Event()
    async def update(*args,**kwargs):
        if writer.await_count==2:
            started.set();await blocked.wait()
        return await original(*args,**kwargs)
    writer.side_effect=update
    api=CardAPI(hass);result=await api.save(msg,hass_admin_user)
    await asyncio.wait_for(started.wait(),2)
    await c.async_stop_writes()
    job=api.jobs[result['operation_id']]
    assert job['status']=='uncertain' and writer.await_count==2
    assert not c._write_lock.locked()


async def test_reload_rebinds_subscription_and_request_lookup(hass,runtime,hass_admin_user):
    from custom_components.microclimate_integration.card_api import KEY, PREFIX
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    api=hass.data[KEY]
    connection=Mock(user=hass_admin_user,subscriptions={})
    await api.handle(connection,{'id':1,'device_id':device.id},'subscribe')
    old_generation=connection.send_event.call_args.args[1]['runtime_generation']
    await hass.config_entries.async_reload(c.entry.entry_id)
    await hass.async_block_till_done()
    latest=connection.send_event.call_args.args[1]
    assert latest['runtime_generation']!=old_generation and latest['online']
    connection.subscriptions[1]()
    assert not c._listeners
    await api.handle(connection,{'id':2,'device_id':device.id,'request_id':str(uuid4())},'request')
    assert connection.send_result.call_args.args==(2,None)


async def test_disabled_registry_and_token_generation(hass,runtime,hass_admin_user):
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    entity=next(f['entity_id'] for f in view['fields'] if f['key']=='Yellow_period_4_time')
    er.async_get(hass).async_update_entity(entity,disabled_by=er.RegistryEntryDisabler.USER)
    await hass.async_block_till_done()
    with pytest.raises(WriteValidationError,match='control_denied'):await CardAPI(hass).save(msg,hass_admin_user)
    hass.config_entries.async_update_entry(c.entry,data={**c.entry.data,'token':'rotated-dummy'})
    with pytest.raises(WriteValidationError,match='version_changed'):await CardAPI(hass).save(msg,hass_admin_user)
    assert writer.await_count==0


async def test_completed_job_scope_expiry_and_noop(hass,runtime,hass_admin_user):
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    msg['patch']=patch(points(4));api=CardAPI(hass)
    result=await api.save(msg,hass_admin_user);job=await wait_job(hass,api,result)
    assert job['status']=='succeeded' and job['total']==0 and writer.await_count==0
    stranger=Mock(id='another-user')
    with pytest.raises(WriteValidationError):api.find_job(result,stranger)
    job['finished']-=3601
    with pytest.raises(WriteValidationError):api.find_job(result,hass_admin_user)
    assert not api.jobs


@pytest.mark.parametrize('channel,model,control',[('Yellow','Evo Connect',1),('Blue','Evo Connect',0),('Yellow','Evo Connect 2',2),('Blue','Evo Connect 2',1),('Red','Evo Connect 3',1)])
def test_profile_final_multi_table(channel,model,control):
    from custom_components.microclimate_integration.const import CHANNELS
    data=payload(model);populate(data,8,channel);data[CHANNELS[channel]['control_pin']]=control
    desired=points(8);desired.pop(2)
    plan=build_plan(model,channel,data,patch(desired))
    assert [value_of(definition_for(model,f'{channel}_period_{i}_setpoint'),plan.expected) for i in range(1,9)]==[21,22,24,25,26,27,28,0]


async def test_static_bundle_served_and_request_recovery(hass,runtime,hass_admin_user,hass_client):
    from custom_components.microclimate_integration.card_api import KEY
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    client=await hass_client()
    response=await client.get('/microclimate_integration/microclimate-cards.js?v=1.2.0')
    assert response.status==200 and 'microclimate-channel-card' in await response.text()
    api=hass.data[KEY];result=await api.save(msg,hass_admin_user);await wait_job(hass,api,result)
    connection=Mock(user=hass_admin_user,subscriptions={})
    await api.handle(connection,{'id':1,'device_id':device.id,'request_id':msg['request_id']},'request')
    assert connection.send_result.call_args.args==(1,result)


async def test_job_results_still_readable_when_writes_disabled(hass,runtime,hass_admin_user):
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    api=CardAPI(hass);result=await api.save(msg,hass_admin_user);await wait_job(hass,api,result)
    hass.config_entries.async_update_entry(c.entry,options={'enable_writes':False})
    assert api.find_job(result,hass_admin_user)['status']=='succeeded'


async def test_websocket_save_operation_and_recovery(hass,runtime,hass_ws_client,hass_admin_user):
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    client=await hass_ws_client(hass)
    await client.send_json({'id':1,'type':'microclimate_integration/card/save',**msg})
    response=await client.receive_json()
    assert response['success'],response
    operation=response['result']['operation_id']
    await client.send_json({'id':2,'type':'microclimate_integration/card/operation','operation_id':operation})
    assert (await client.receive_json())['success']
    while True:
        event=await client.receive_json()
        assert 'error' not in event['event']
        if event['event']['status'] in ('succeeded','partial','failed','uncertain'):
            assert event['event']['status']=='succeeded',event
            break
    await client.send_json({'id':3,'type':'unsubscribe_events','subscription':2})
    assert (await client.receive_json())['success']
    await client.send_json({'id':4,'type':'microclimate_integration/card/request','device_id':device.id,'request_id':msg['request_id']})
    assert (await client.receive_json())['result']=={'operation_id':operation}
    assert writer.await_count==2


async def test_observation_tiles_are_registry_bound_and_read_only(hass,runtime,hass_admin_user):
    c,data,writer,device,view,msg=await context(hass,runtime,hass_admin_user)
    data.update(v0=24,v8=25,v4=70);c._publish(dict(data))
    await hass.async_block_till_done()
    values={o['name']:o['value'] for o in snapshot(hass,c,'Yellow',device,hass_admin_user)['observations']}
    assert {'Temperature','Observed setpoint','Output percentage'} <= set(values)
    assert values['Observed setpoint']=='25.0' and values['Output percentage']=='70.0'
    assert all(f['key']!='Yellow_setpoint_pin' for f in view['fields'])
