from pydantic import BaseModel
from typing import Optional
from datetime import datetime



class InvestorCreate(BaseModel):
    investor_user: str

    class Config:
        orm_mode = True 
        from_attributes = True

class InvestorResponse(BaseModel):
    investor_id: str
    investor_user: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True 
        from_attributes = True