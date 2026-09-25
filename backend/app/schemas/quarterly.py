from pydantic import BaseModel
from .sources import Source
from .metrics import Change

class QuarterObservation(BaseModel):
    year: int | None
    quarter: int | None
    period: str | None
    value: float | None

class QuarterSnapshot(QuarterObservation):
    state: str
    rank: int | None
    comparison_count: int
    rank_label: str | None
    previous: QuarterObservation | None
    change: Change | None

class QuarterlyUnemployment(BaseModel):
    state: str
    frequency: str
    unit: str
    period: str | None
    periods: list[str]
    metric: QuarterSnapshot
    states: list[QuarterSnapshot]
    eligible_count: int
    comparison_count: int
    observations: list[QuarterObservation]
    source: Source
