"""Cyclic calendar order, including the closing fourth-to-first boundary."""
import itertools
import pytest
from custom_components.microclimate_integration.write_contract import (
    definition_for, serialize, WriteValidationError, SEASON_PINS)


def check(values,index=0):
    return serialize(definition_for('Evo Connect 3',f'season_{index+1}_start_pin'),values[index],dict(zip(SEASON_PINS,values)))


@pytest.mark.parametrize('values',[
    ['09/10','01/01','01/06','01/07'],
    ['01/05','01/09','01/01','01/03'],
    ['01/01','01/04','01/07','01/10'],
    ['31/12','01/01','28/02','01/03'],
])
def test_permitted_cycles(values):
    for i in range(4):assert check(values,i)==values[i]


@pytest.mark.parametrize('values',[
    ['01/01','02/12','01/04','01/11'],
    ['20/02','01/02','30/06','20/06'],
    ['01/01','01/04','01/04','01/10'],
    ['01/01','01/01','01/01','01/01'],
    # One internal descent alone is insufficient; the closing edge matters too.
    ['01/01','01/10','01/04','01/07'],
])
def test_rejected_cycles(values):
    with pytest.raises(WriteValidationError,match='invalid_season_order'):check(values)


def test_all_permutations_only_rotations_are_valid():
    chronological=('01/01','01/04','01/07','01/10')
    expected={chronological[i:]+chronological[:i] for i in range(4)}
    accepted=set()
    for values in itertools.permutations(chronological):
        try:check(values);accepted.add(values)
        except WriteValidationError:pass
    assert accepted==expected


@pytest.mark.parametrize('invalid',['01/13','29/02','31/04','01.07',None,'bogus'])
def test_invalid_neighbor_blocks_validation(invalid):
    with pytest.raises(WriteValidationError,match='season_dates_unavailable'):
        check(['01/05','01/09','01/01',invalid])


def test_unset_siblings_allow_population_but_not_unknown_siblings():
    assert check(['09/10','00/00','00/00','00/00'])=='09/10'
    assert check(['09/10','00/00','01/06','01/07'])=='09/10'
    with pytest.raises(WriteValidationError,match='invalid_season_order'):check(['01/01','00/00','01/10','01/07'])
    with pytest.raises(WriteValidationError,match='invalid_date'):check(['00/00']*4)


@pytest.mark.parametrize('channel,pin',[('Yellow','v48'),('Red','v78')])
@pytest.mark.parametrize('value',[0,1,239,240,12.0,'120.0'])
def test_ramp_valid(channel,pin,value):
    from custom_components.microclimate_integration.write_contract import matches
    f=definition_for('Evo Connect 3',f'{channel}_ramp_time')
    assert f.pin==pin and f.platform=='number'
    wire=serialize(f,value,{})
    assert wire==str(int(float(value)))
    assert matches(f,wire,{pin:float(value)})
    assert not matches(f,wire,{pin:f'{value}°F'})


@pytest.mark.parametrize('value',[-1,241,0.5,239.999,True,False,None,float('nan'),float('inf'),'x'])
def test_ramp_invalid(value):
    f=definition_for('Evo Connect 3','Yellow_ramp_time')
    with pytest.raises(WriteValidationError,match='invalid_ramp'):serialize(f,value,{})
