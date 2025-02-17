from pydantic import BaseModel
from typing import Optional
from datetime import datetime



class HubCreate(BaseModel):
    hub_name: str
    hub_address: str
    hub_user: str

    class Config:
        orm_mode = True
        from_attributes = True

    
class HubResponse(BaseModel):
    hub_id: str
    hub_name: str
    hub_address: str
    hub_user: str
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True




