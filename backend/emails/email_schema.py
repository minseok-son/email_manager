from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Input schema
class EmailInput(BaseModel):
    id: Optional[int]
    internship_id: Optional[int]
    timestamp: str
    url: str
    confidence: int
    

# Output schema
class EmailOutput(BaseModel):
    internship_id: int
    timestamp: datetime
    url: str
    confidence: int
    

# InDB schema
class EmailInDb(BaseModel):
    id: int
    internship_id: int
    timestamp: datetime
    url: str
    confidence: int
    