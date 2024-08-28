from pydantic import BaseModel
from typing import Optional

# Input schema
class InternshipInput(BaseModel):
    company: str
    stage: int

# Output schema
class InternshipOutput(BaseModel):
    id: int
    company: str
    stage: int

# InDB schema
class InternshipInDb(BaseModel):
    id: Optional[int]
    company: str
    stage: int