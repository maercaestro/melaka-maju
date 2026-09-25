from fastapi import APIRouter, Query
from .dependencies import engine, metric_name
from ..schemas.rankings import Rankings
router=APIRouter()
@router.get('/rankings/{metric}',response_model=Rankings)
def rankings(metric:str,year:int|None=Query(None,ge=1900,le=2200),include_federal_territories:bool=False):
    return engine().rankings(metric_name(metric),year,include_federal_territories)
