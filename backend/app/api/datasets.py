import os
import secrets
import polars as pl
from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel
from ..data.registry import REGISTRY, CONFIG
from ..data.opendosm import get_dataset_metadata, load_dataset, refresh_dataset, DataUnavailable
from ..data.service import analytical_data
from ..data.cache import LOCK
from ..data.states import normalize_state,STATES,TERRITORIES
from ..analysis.catalogue import definitions
router=APIRouter()
@router.get('/datasets')
def datasets(): return {'datasets':[get_dataset_metadata(key) for key in REGISTRY],'discovery':CONFIG['discovery']}
@router.get('/catalogue')
def catalogue():
    df,_=analytical_data()
    return {'metrics':[{**d,'years':df.filter(pl.col('metric')==d['id'])['year'].unique().sort(descending=True).to_list()} for d in definitions()],'years':df['year'].unique().sort(descending=True).to_list(),'states':STATES,'territories':TERRITORIES}
@router.get('/datasets/{dataset_id}/raw')
def raw(dataset_id:str,state:str|None=None,year:int|None=None,sector:str|None=None,series:str|None=None,limit:int=Query(100,ge=1,le=1000),offset:int=Query(0,ge=0)):
    if dataset_id not in REGISTRY: raise HTTPException(404,'Unknown dataset')
    df=load_dataset(dataset_id)
    filters={c:sorted(df[c].drop_nulls().cast(pl.String).unique().to_list()) for c in ['state','sector','series'] if c in df.columns}
    filters['year']=sorted(df['date'].cast(pl.String).str.slice(0,4).unique().to_list(),reverse=True)
    if state:
        state=normalize_state(state)
        df=df.filter(pl.col('state').replace({s:normalize_state(s) for s in df['state'].unique()})==state)
    if year is not None: df=df.filter(pl.col('date').cast(pl.String).str.slice(0,4)==str(year))
    for column,value in [('sector',sector),('series',series)]:
        if value:
            if column not in df.columns: raise HTTPException(422,f'Dataset has no {column} dimension')
            df=df.filter(pl.col(column)==value)
    return {'dataset':get_dataset_metadata(dataset_id),'columns':df.columns,'filters':filters,'total':df.height,'offset':offset,'limit':limit,'rows':df.slice(offset,limit).to_dicts()}
class RefreshRequest(BaseModel):
    dataset:str|None=None
@router.post('/data/refresh')
def refresh(body:RefreshRequest|None=None,authorization:str|None=Header(None)):
    token=os.getenv('DATA_REFRESH_TOKEN')
    if token and not secrets.compare_digest(authorization or '',f'Bearer {token}'): raise HTTPException(403,'Refresh token required')
    keys=[body.dataset] if body and body.dataset else list(REGISTRY)
    if any(key not in REGISTRY for key in keys): raise HTTPException(404,'Unknown dataset')
    results=[]
    with LOCK:
        for key in keys:
            try: results.append({'dataset':key,'status':'ok','metadata':refresh_dataset(key)})
            except DataUnavailable as exc: results.append({'dataset':key,'status':'error','error':str(exc)})
        analytical_data.cache_clear()
    return {'results':results}
@router.get('/data/audit')
def audit(): return {'discrepancies':analytical_data()[1],'policy':'HIES wins overlapping survey years; no figures from conversation are used as inputs.'}
