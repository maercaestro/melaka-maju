import polars as pl
import pytest
from app.analysis.rankings import rank_states
from app.analysis.household import changes
from app.analysis.trends import validate_observations
from app.analysis.engine import Engine
from app.data.states import STATES,TERRITORIES,normalize_state
from app.data.registry import REGISTRY

def frame(values,metric='poverty',year=2024):
    return pl.DataFrame([{'state':state,'year':year,'metric':metric,'value':float(value),'dataset':'hies_state'} for state,value in values.items()])

def test_descending():
    df=frame({'Johor':100,'Kedah':80,'Melaka':60},'median_household_income')
    assert rank_states(df,'median_household_income',2024)['state'].to_list()==['Johor','Kedah','Melaka']

def test_lower_and_ties():
    df=frame({'Johor':2,'Kedah':5,'Melaka':8,'Perak':2})
    ranked=rank_states(df,'poverty',2024,'ascending')
    assert ranked['rank'].to_list()==[1,1,3,4]
    assert ranked['comparison_count'].to_list()==[4]*4

def test_universe():
    df=frame({s:i for i,s in enumerate(STATES+TERRITORIES+['Malaysia'])})
    assert rank_states(df,'poverty',2024).height==13
    assert rank_states(df,'poverty',2024,include_federal_territories=True).height==16
    assert not set(TERRITORIES)&set(rank_states(df,'poverty',2024)['state'])

def test_same_year_missing_and_previous():
    df=pl.concat([frame({'Melaka':4.2},year=2022),frame({'Melaka':3},year=2024),frame({'Melaka':2},year=2025)])
    engine=Engine(df,REGISTRY)
    metric=engine.metric('poverty','Melaka',2024)
    assert metric['year']==2024 and metric['value']==3
    assert metric['previous']=={'year':2022,'value':4.2}
    assert metric['change']['absolute']==pytest.approx(-1.2)
    assert engine.metric('poverty','Melaka',2023)['value'] is None
    assert engine.metric('poverty','Melaka')['year']==2025
    assert engine.overview('Melaka','same-year',2024,False)['mixed_years'] is False
    assert all(m['year']==2024 for m in engine.overview('Melaka','same-year',2024,False)['metrics'])

def test_changes():
    assert changes(3,4.2,'%')=={'absolute':-1.2,'percent':None,'unit':'percentage points'}
    assert changes(.337,.370,'coefficient')['absolute']==pytest.approx(-.033)
    assert changes(110,100,'RM/month')['percent']==pytest.approx(10)
    assert changes(10,0,'RM/month')['percent'] is None

def test_validation():
    df=frame({'Melaka':3})
    with pytest.raises(ValueError,match='Duplicate'):validate_observations(pl.concat([df,df]))
    with pytest.raises(ValueError,match='Out-of-range'):validate_observations(frame({'Melaka':1.1},'gini'))
    with pytest.raises(ValueError,match='Invalid'):validate_observations(frame({'Melaka':float('nan')}))

def test_aliases():
    assert normalize_state('Penang')=='Pulau Pinang'
    assert normalize_state('Malacca')=='Melaka'
    assert normalize_state('Kuala Lumpur')=='W.P. Kuala Lumpur'
