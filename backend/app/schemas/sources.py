from pydantic import BaseModel
class Source(BaseModel):
    provider: str = 'DOSM'
    dataset: str
    title: str
    url: str
    retrieved_at: str | None = None
    sha256: str | None = None
    calculated: bool = False
    calculation: str | None = None
    note: str | None = None
