from pydantic import BaseModel
from .sources import Source
class Previous(BaseModel):
    year: int
    value: float
class Change(BaseModel):
    absolute: float
    percent: float | None = None
    unit: str
class Metric(BaseModel):
    id: str
    label: str
    state: str
    value: float | None
    unit: str
    year: int | None
    rank: int | None = None
    comparison_count: int
    eligible_count: int
    ranking_direction: str
    rank_label: str | None = None
    previous: Previous | None = None
    change: Change | None = None
    source: Source
    status: str
class Overview(BaseModel):
    state: str
    mode: str
    year: int | None
    mixed_years: bool
    include_federal_territories: bool
    metrics: list[Metric]
