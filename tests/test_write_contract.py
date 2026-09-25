"""Allowlist, wire encoding, and field-specific validation boundaries."""
from datetime import time, timezone
from decimal import Decimal
import json
from pathlib import Path
import pytest
from custom_components.microclimate_integration.write_contract import (
    WriteValidationError, write_definitions, definition_for, serialize, matches,
    numeric, date_string, time_seconds, applicable, encode_time)
from custom_components.microclimate_integration.const import CHANNELS, MODEL_CHANNEL_OPTIONS


def field(key='Yellow_period_1_setpoint',model='Evo Connect 3'):
    return definition_for(model,key)


@pytest.mark.parametrize('model',list(MODEL_CHANNEL_OPTIONS))
def test_allowlist(model):
    definitions=write_definitions(model)
    assert len({d.key for d in definitions})==len(definitions)
    pins={d.pin for d in definitions}
    assert not pins.intersection({'v8','v9','v10','v108','v114','v115','v116'})
    assert {d.channel for d in definitions if d.channel}==set(MODEL_CHANNEL_OPTIONS[model])
    assert [d.pin for d in definitions if d.kind=='date']==['v20','v21','v22','v23']
    for channel in MODEL_CHANNEL_OPTIONS[model]:
        first={'Yellow':32,'Red':62,'Blue':92}[channel]
        assert [int(d.pin[1:]) for d in definitions if d.channel==channel and d.index]==list(range(first,first+16))
    assert 'v48' in pins and ('v78' in pins)==(model=='Evo Connect 3')
    if model=='Evo Connect':
        assert dict(field('Blue_control_pin',model).options)=={'0':'fixed'}
        assert 'v109' not in pins and 'v110' not in pins
    for key in ['v8','Blue_output_type','Blue_ramp_time','not_a_field']:
        with pytest.raises(WriteValidationError):definition_for(model,key)
    assert write_definitions('unknown')==()


@pytest.mark.parametrize('value',[0,100,0.125,'25.50',Decimal('0.001'),1e-25])
def test_numeric_accept(value):
    wire=serialize(field(),value,{})
    assert Decimal(wire)==Decimal(str(value))
    assert matches(field(),wire,{'v33':value,'v52':0})


@pytest.mark.parametrize('value',[-1,100.01,'NaN',float('nan'),'Infinity',float('-inf'),True,False,None,[],{},'rubbish'])
def test_numeric_reject(value):
    with pytest.raises(WriteValidationError,match='invalid_number'):numeric(value)


@pytest.mark.parametrize('value',['01/01','28/02','30/04','31/12'])
def test_date_accept(value):assert date_string(value)==value


@pytest.mark.parametrize('value',['29/02','31/04','00/00','00/01','01/00','32/01','01/13','9/2','09/02/26',' 09/02',None,True])
def test_date_reject(value):
    with pytest.raises(WriteValidationError,match='invalid_date'):date_string(value)


@pytest.mark.parametrize('value',[time(0),time(23,59,59)])
def test_time_bounds(value):
    data={'v32':'0\0'+'0\0Europe/London\0'+'0\0\0opaque'}
    wire=serialize(field('Yellow_period_1_time'),value,data)
    parts=wire.split('\0'); assert parts[:2]==[str(time_seconds(value))]*2
    assert parts[2:]==['Europe/London','0','','opaque']
    assert '\\0' not in wire
    assert matches(field('Yellow_period_1_time'),wire,{'v32':wire})
    assert not matches(field('Yellow_period_1_time'),wire,{'v32':wire+'\0'})


@pytest.mark.parametrize('value',[None,'00:00:00','24:00:00','sr',time(1,microsecond=1),time(1,tzinfo=timezone.utc)])
def test_time_reject(value):
    with pytest.raises(WriteValidationError):time_seconds(value)


@pytest.mark.parametrize('raw',['sr\0'+'0\0Europe/London\0'+'0','7200\0'+'1\0Europe/London\0'+'0',
                                    '0\0'+'0\0badzone\0'+'0','0\0'+'0',True,None,'86400','nan'])
def test_encoding_reject(raw):
    with pytest.raises(WriteValidationError):encode_time(field('Yellow_period_1_time'),time(2),{'v32':raw})


def test_plain_template_and_conflicts():
    f=field('Yellow_period_1_time');data={'v32':'7200','v34':'0\0'+'0\0Europe/London\0'+'0'}
    assert encode_time(f,time(2),data)=='7200\0'+'7200\0Europe/London\0'+'0'
    with pytest.raises(WriteValidationError):encode_time(f,time(2),{'v32':'7200'})
    data['v36']='0\0'+'0\0UTC\0'+'0'
    with pytest.raises(WriteValidationError):encode_time(f,time(2),data)
    del data['v36'];data['v27']='0\0'+'0\0UTC\0'+'0'
    with pytest.raises(WriteValidationError):encode_time(f,time(2),data)


@pytest.mark.parametrize('channel,timing,expected',[('Yellow',0,0),('Yellow',1,2),('Yellow',2,8),('Yellow',3,8),
    ('Red',3,8),('Blue',3,0),('Blue',4,8),('Blue',99,0)])
def test_mode_applicability(channel,timing,expected):
    data={CHANNELS[channel]['control_pin']:1,CHANNELS[channel]['timing_type']:timing}
    definitions=[d for d in write_definitions('Evo Connect 3') if d.channel==channel and d.kind=='setpoint']
    data.update({d.pin:20 for d in definitions})
    assert sum(applicable(d,data) for d in definitions)==expected


def test_every_enum_code_and_suffix_readback():
    for model in MODEL_CHANNEL_OPTIONS:
        for d in write_definitions(model):
            for code,label in d.options:
                assert serialize(d,label,{})==code
                assert matches(d,code,{d.pin:float(code)})
            if d.options:
                with pytest.raises(WriteValidationError):serialize(d,'unknown',{})
    assert matches(field(),'25.25',{'v33':'25.25°F','v52':1})
    assert not matches(field(),'25.25',{'v33':'25.25°F','v52':0})
    assert not matches(field(),'25.25',{'v33':25.3,'v52':1})


def test_sanitized_evidence_replay():
    captures=json.loads(Path('fixtures/write_captures.json').read_text())
    assert 'https://' not in json.dumps(captures)
    for capture in captures:
        f=next(d for d in write_definitions('Evo Connect 2') if d.pin==capture['pin'])
        value=time(2) if f.kind=='time' else capture['requested']
        wire=serialize(f,value,capture['samples'][0]['payload'])
        assert wire==capture['requested']
        reads=[s for s in capture['samples'][1:] if isinstance(s.get('payload'),dict) and f.pin in s['payload']]
        assert reads and all(matches(f,wire,s['payload']) for s in reads)


def test_probeless_profile_rejects_thermal_context():
    f=field('Blue_period_1_setpoint','Evo Connect')
    assert not applicable(f,{'v93':20,'v113':2,'v112':1})
    assert applicable(f,{'v93':20,'v113':2,'v112':0})
