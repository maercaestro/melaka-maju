from pydantic import BaseModel
from .sources import Source
class Observation(BaseModel):
    year: int
    value: float
    source: Source
class Trend(BaseModel):
    metric: str
    label: str
    unit: str
    state: str
    observations: list[Observation]
    annotation: dict
