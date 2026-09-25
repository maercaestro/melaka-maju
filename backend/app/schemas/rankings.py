from pydantic import BaseModel
from .metrics import Metric
class Rankings(BaseModel):
    metric: str
    year: int | None
    comparison_count: int
    eligible_count: int
    missing_states: list[str]
    states: list[Metric]
