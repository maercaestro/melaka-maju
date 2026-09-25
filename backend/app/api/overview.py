from typing import Literal
from fastapi import APIRouter, HTTPException, Query
from .dependencies import engine, state_name
from ..schemas.metrics import Overview
router=APIRouter()
@router.get('/state/{state}/overview',response_model=Overview)
def overview(state:str,mode:Literal['latest','same-year']='latest',year:int|None=Query(None,ge=1900,le=2200),include_federal_territories:bool=False):
    state=state_name(state)
    if mode=='same-year' and year is None: raise HTTPException(422,'Same-year mode requires year')
    return engine().overview(state,mode,year,include_federal_territories)
