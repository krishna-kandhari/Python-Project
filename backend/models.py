from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: Optional[int]
    email: str
    name: str
    
class SOSLocation(BaseModel):
    lat: float
    lng: float
    timestamp: str
