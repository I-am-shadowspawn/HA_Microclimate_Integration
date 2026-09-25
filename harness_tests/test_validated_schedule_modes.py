"""Maintainer-validated timing, schedule grouping and output capabilities."""
import pytest
from custom_components.microclimate_integration.api_client import normalize_response
from custom_components.microclimate_integration.const import timing_type_mapping, CHANNEL_CAPABILITIES
from custom_components.microclimate_integration.schedule import schedule_observation
from custom_components.microclimate_integration.sensor_contract import VERIFIED_MEASUREMENTS
from custom_components.microclimate_integration.const_helpers import enum_value


@pytest.mark.parametrize('channel,timing_pin,first_pin,season_code', [
    ('Yellow','v53',32,3), ('Red','v83',62,3), ('Blue','v113',92,4),
])
def test_same_slots_have_mode_specific_meaning(channel,timing_pin,first_pin,season_code):
    control={'Yellow':'v52','Red':'v82','Blue':'v112'}[channel]
    payload={control:1, 'v20':'09/02','v21':'00/00','v22':'01/08','v23':'01/11', 'v48':9,'v78':7,'v108':99}
    for index in range(8):
        payload[f'v{first_pin+2*index}']=f'{index*3600}\x00{index*3600}\x00Europe/London\x000'
        payload[f'v{first_pin+2*index+1}']=20+index/2
    seasonal=schedule_observation(normalize_response({**payload,timing_pin:season_code}),channel)
    assert seasonal['timing_type']=='Seasonal'
    assert 'daily_points' not in seasonal
    for season in range(1,5):
        group=seasonal['seasons'][f'season_{season}']
        assert group['day']['start_pin']==f'v{first_pin+4*(season-1)}'
        assert group['night']['setpoint_pin']==f'v{first_pin+4*(season-1)+3}'
        assert group['day']['setpoint_celsius']==20+(season-1)
        assert group['night']['setpoint_celsius']==20.5+(season-1)
        assert group['start_date']['source_pin']==f'v{19+season}'
    assert seasonal['seasons']['season_1']['start_date']['day']==9
    assert seasonal['seasons']['season_1']['start_date']['month']==2
    assert seasonal['seasons']['season_2']['start_date']['interpretation']=='zero_date'
    assert seasonal['seasons']['season_1']['day']['start']['time']=='00:00:00'
    multi=schedule_observation(normalize_response({**payload,timing_pin:2}),channel)
    assert multi['daily_points']==seasonal['periods']
    assert 'seasons' not in multi
    constant=schedule_observation(normalize_response({**payload,timing_pin:0}),channel)
    assert constant['timing_type']=='Constant'
    assert 'seasons' not in constant and 'daily_points' not in constant
    assert ('ramp_time' in seasonal)==(channel!='Blue')
    assert ('ramp_time' in multi)==(channel!='Blue')


@pytest.mark.parametrize('model', list(VERIFIED_MEASUREMENTS))
def test_blue_has_no_ramp_measurement_in_any_model(model):
    assert not any(d.channel=='Blue' and d.key=='ramp_time' for d in VERIFIED_MEASUREMENTS[model])
    assert any(d.channel=='Yellow' and d.key=='ramp_time' for d in VERIFIED_MEASUREMENTS[model])


@pytest.mark.parametrize('channel', ['Yellow','Red','Blue'])
@pytest.mark.parametrize('code', [0,1,2,3,4])
def test_live_enum_reader_uses_channel_table(channel,code):
    expected = ({0:'Constant',1:'Day Night',2:'Multi',3:'Periodic',4:'Seasonal'} if channel=='Blue'
                else {0:'Constant',1:'Day Night',2:'Multi',3:'Seasonal'})
    assert timing_type_mapping(channel).get(str(code))==expected.get(code)
    if code in expected:
        assert enum_value(str(code)+'.0',timing_type_mapping(channel))==expected[code]
        assert enum_value(code,timing_type_mapping(channel))==expected[code]
    else:
        assert enum_value(code,timing_type_mapping(channel)) is None


def test_unknown_channel_does_not_decode_ambiguous_code():
    assert enum_value(3,timing_type_mapping('Unknown')) is None
    assert timing_type_mapping('Unknown')=={}


def test_only_blue_periodic_exposes_unparsed_periodic_fields():
    payload=normalize_response({'v53':3,'v83':3,'v113':3,'v55':60,'v56':0,'v85':60,'v86':0,'v115':60,'v116':0})
    for channel in ('Yellow','Red'):
        result=schedule_observation(payload,channel)
        assert result['timing_type']=='Seasonal'
        assert 'periodic_interval' not in result and 'periodic_duration' not in result
    result=schedule_observation(payload,'Blue')
    assert result['timing_type']=='Periodic'
    assert result['periodic_interval']['raw']==60
    assert result['periodic_duration']['raw']==0
    assert result['periodic_interval']['interpretation']=='reported_unparsed'
    assert CHANNEL_CAPABILITIES['Blue']['variable_output'] is False
    assert 'ramp_time' not in result
