"""Typed observations, lossless supported fields and conservative schedule semantics."""
import json
import pytest
from custom_components.microclimate_integration.api_client import normalize_response
from custom_components.microclimate_integration.schedule import observe_field, observe_time, schedule_observation


@pytest.mark.parametrize('payload,status', [({},'absent'),({'v32':None},'invalid'),({'v32':0},'valid'),
    ({'v32':'-1'},'invalid'),({'v32':'86400'},'invalid'),({'v32':'3600.5'},'invalid'),
    ({'v32':'nan'},'invalid'),({'v32':'new_vendor_token'},'unsupported')])
def test_time_status_and_presence(payload,status):
    result=observe_field(normalize_response(payload),'v32',observe_time)
    assert result['status']==status
    if status=='valid':assert result['time']=='00:00:00'


@pytest.mark.parametrize('token', ['sr','ss','3600'])
def test_unknown_fields_and_timezone_roundtrip(token):
    raw=token+'\x007200\x00Unknown/Zone\x001,3,5\x00-300\x00future\x00'
    result=observe_time(raw)
    assert result['raw']==raw
    assert '\x00'.join(result['fields'])==raw
    assert result['timezone_status']=='unrecognized'
    assert result['opaque_fields']==[{'index':i,'value':result['fields'][i]} for i in (1,3,4,5,6)]
    assert json.loads(json.dumps(result))==result
    assert not any(key in result for key in ('offset','days','active','enabled'))


@pytest.mark.parametrize('channel,modepin,controlpin,start', [('Yellow','v53','v52',32),('Red','v83','v82',62),('Blue','v113','v112',92)])
def test_day_night_first_two_pairs_only_and_mode_transition(channel,modepin,controlpin,start):
    base={controlpin:1}
    for i in range(8):
        base[f'v{start+2*i}']=str((23 if i==0 else i)*3600)
        base[f'v{start+2*i+1}']=20+i
    data=normalize_response({**base,modepin:1})
    result=schedule_observation(data,channel)
    assert result['day_night']['day']['start_pin']==f'v{start}'
    assert result['day_night']['night']['setpoint_pin']==f'v{start+3}'
    assert result['day_night']['day']['start']['time']=='23:00:00'
    assert result['day_night']['night']['start']['time']=='01:00:00'
    assert len(result['periods'])==8  # Extra reported fields aren't silently discarded.
    assert not any(k in result for k in ('active_period','next_transition','daily_points'))
    multi=schedule_observation(normalize_response({**base,modepin:2}),channel)
    assert 'day_night' not in multi
    assert list(multi['daily_points'])==[f'period_{i}' for i in range(1,9)]
    assert list(multi['daily_points'].values())[0]['start']['time']=='23:00:00'  # No sorting.
    assert schedule_observation(data,channel) is result  # One memoized observation per snapshot.


@pytest.mark.parametrize('time,value,mode,activation', [('0',0,1,'likely_unused'),('0',0,0,'likely_unused'),
    ('0',25,1,'unverified'),('3600',0,0,'unverified'),('sr',0,1,'unverified'),('0',None,1,'unverified')])
def test_multi_unused_default_is_inference_not_disabled(time,value,mode,activation):
    result=schedule_observation(normalize_response({'v53':2,'v52':mode,'v32':time,'v33':value}),'Yellow')
    period=result['daily_points']['period_1']
    assert period['activation']==activation
    assert period['setpoint_raw']==value
    assert 'enabled' not in period and 'disabled' not in period
    assert len(result['daily_points'])==8
    if activation=='likely_unused':assert period['activation_evidence']=='maintainer_inference_not_explicit_enable_flag'


def test_duplicate_times_reported_without_precedence():
    result=schedule_observation({'v53':2,'v52':1,'v32':'3600','v33':20,'v34':'3600','v35':30},'Yellow')
    assert result['duplicate_clock_times']=={'01:00:00':['period_1','period_2']}
    assert result['daily_points']['period_1']['setpoint_celsius']==20
    assert result['daily_points']['period_2']['setpoint_celsius']==30
    assert 'active_period' not in result


def test_partial_invalid_unsupported_and_zero_setpoints():
    data={'v53':2,'v52':0,'v32':'0','v33':0,'v34':'3600','v35':101,'v36':'0','v37':None}
    result=schedule_observation(normalize_response(data),'Yellow')
    assert result['periods']['period_1']['setpoint_status']=='valid'
    assert result['periods']['period_1']['setpoint_percentage']==0
    assert result['periods']['period_2']['setpoint_status']=='invalid'
    assert result['periods']['period_2']['setpoint_raw']==101
    assert result['periods']['period_3']['setpoint_status']=='invalid'
    assert result['periods']['period_4']['setpoint_status']=='absent'
    result=schedule_observation(normalize_response({**data,'v52':99,'v53':99}),'Yellow')
    assert result['control']['status']==result['timing']['status']=='unsupported'
    assert result['periods']['period_1']['setpoint_status']=='unsupported'
    assert 'daily_points' not in result
