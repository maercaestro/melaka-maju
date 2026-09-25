from fastapi import HTTPException
from ..data.service import analytical_data
from ..data.registry import REGISTRY
from ..data.opendosm import get_dataset_metadata
from ..data.states import normalize_state, STATES, TERRITORIES
from ..analysis.engine import Engine
from ..analysis.catalogue import DEFINITIONS

def engine():
    return Engine(analytical_data()[0],{key:get_dataset_metadata(key) for key in REGISTRY})
def state_name(state):
    result=normalize_state(state)
    if result not in STATES+TERRITORIES: raise HTTPException(422,'Unknown state')
    return result
def metric_name(metric):
    if metric not in DEFINITIONS: raise HTTPException(404,'Unknown metric')
    return metric
