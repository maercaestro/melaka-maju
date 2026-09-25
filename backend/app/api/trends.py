from fastapi import APIRouter, Query
from .dependencies import engine, metric_name,state_name
from ..schemas.trends import Trend
router=APIRouter()
@router.get('/trends/{metric}',response_model=Trend)
def trends(metric:str,state:str='Melaka',start_year:int=Query(2015,ge=1900,le=2200)):
    return engine().trend(metric_name(metric),state_name(state),start_year)
