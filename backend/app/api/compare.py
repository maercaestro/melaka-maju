from typing import Literal
from fastapi import APIRouter, HTTPException, Query
from .dependencies import engine,metric_name,state_name
router=APIRouter()
@router.get('/compare')
def compare(metric:str,states:str='Melaka,Johor,Negeri Sembilan,Pulau Pinang,Selangor',year:int|None=Query(None,ge=1900,le=2200),mode:Literal['latest','same-year']='latest',include_federal_territories:bool=False):
    metric_name(metric)
    selected=[state_name(s) for s in states.split(',')]
    if len(selected)!=len(set(selected)): raise HTTPException(422,'Duplicate states')
    if mode=='same-year' and year is None: raise HTTPException(422,'Same-year mode requires year')
    e=engine()
    # Latest comparison uses one shared metric year, never different years for different states.
    target=year if year is not None else e.latest_year(metric)
    return {'metric':metric,'year':target,'mixed_years':False,'states':[e.metric(metric,s,target,include_federal_territories) for s in selected]}
