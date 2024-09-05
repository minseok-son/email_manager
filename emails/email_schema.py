from pydantic import BaseModel
from typing import Optional

# Input schema
class EmailInput(BaseModel):
    id: Optional[int]
    url: str
    confidence: int
    internship_id: Optional[int]

# Output schema
class EmailOutput(BaseModel):
    url: str
    confidence: int
    internship_id: int

# InDB schema
class EmailInDb(BaseModel):
    id: int
    url: str
    confidence: int
    internship_id: int