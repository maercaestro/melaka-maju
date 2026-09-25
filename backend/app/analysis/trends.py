import polars as pl
from .catalogue import DEFINITIONS
from .household import household_frames
from .gdp import gdp_frames
from .sectors import sector_frames
from .labour import labour_frames
from ..data.states import normalize_state

def prepare(df):
    return df.with_columns(pl.col('date').cast(pl.String).str.slice(0,4).cast(pl.Int32).alias('year'),pl.col('state').replace({s:normalize_state(s) for s in df['state'].unique()}).alias('state'))
def emit(df,column,metric,dataset):
    return df.select('state','year',pl.col(column).cast(pl.Float64).alias('value'),pl.lit(metric).alias('metric'),pl.lit(dataset).alias('dataset')).filter(pl.col('value').is_not_null())
def validate_observations(df):
    if df.select('state','year','metric').is_duplicated().any(): raise ValueError('Duplicate state/year/metric observations')
    if df['value'].null_count() or df['value'].is_finite().not_().any(): raise ValueError('Invalid numeric observation')
    for metric,definition in DEFINITIONS.items():
        values=df.filter(pl.col('metric')==metric)['value']
        maximum=1 if metric=='gini' else 100 if definition.unit=='%' and metric!='gdp_growth' else None
        if maximum is not None and ((values<0)|(values>maximum)).any(): raise ValueError(f'Out-of-range {metric}')
        if definition.unit!='%' and (values<0).any(): raise ValueError(f'Negative {metric}')

def build_observations(raw):
    frames={key:prepare(value) for key,value in raw.items()}
    result=pl.concat(household_frames(frames,emit)+gdp_frames(frames,emit)+sector_frames(frames,emit)+labour_frames(frames,emit))
    validate_observations(result)
    return result.sort('metric','state','year')

def source_discrepancies(raw):
    result=[]
    primary=prepare(raw['hies_state'])
    for dataset,columns in [('hh_income_state',['income_mean','income_median']),('hh_inequality_state',['gini'])]:
        historical=prepare(raw[dataset])
        joined=primary.join(historical,on=['state','year'],suffix='_historical')
        for field in columns:
            for row in joined.filter((pl.col(field)-pl.col(field+'_historical')).abs()>0.000001).to_dicts():
                result.append({'state':row['state'],'year':row['year'],'field':field,'hies_value':row[field],'historical_value':row[field+'_historical'],'historical_dataset':dataset,'resolution':'hies_state takes precedence for overlapping survey years'})
    return result
