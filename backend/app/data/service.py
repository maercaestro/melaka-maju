"""Orchestrates cached reads; analysis receives frames and performs no I/O."""
from functools import lru_cache
from .registry import REGISTRY
from .opendosm import load_dataset
from ..analysis.trends import build_observations, source_discrepancies
@lru_cache(maxsize=1)
def analytical_data():
    raw={key:load_dataset(key) for key in REGISTRY if REGISTRY[key]['frequency'] != 'quarterly'}
    return build_observations(raw),source_discrepancies(raw)
