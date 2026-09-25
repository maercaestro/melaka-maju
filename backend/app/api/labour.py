from fastapi import APIRouter, Query
from .dependencies import state_name
from ..data.opendosm import load_dataset, get_dataset_metadata
from ..analysis.quarterly import quarterly_unemployment, DATASET
from ..schemas.quarterly import QuarterlyUnemployment

router = APIRouter()

@router.get('/labour/unemployment-quarterly', response_model=QuarterlyUnemployment)
def unemployment_quarterly(state: str = 'Melaka', period: str | None = Query(None, pattern=r'^\d{4}-Q[1-4]$'), include_federal_territories: bool = False):
    state = state_name(state)
    return quarterly_unemployment(load_dataset(DATASET), get_dataset_metadata(DATASET), state, period, include_federal_territories)
