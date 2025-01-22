
from datetime import datetime
from utils.responses import datetime_to_str
from pydantic import BaseModel



class ReferralCreate(BaseModel):
    referred_by: str  # id of referrer
    referred_to: str  # id of referred user

    class Config:
        orm_mode = True 
        from_attributes = True

class ReferralResponse(ReferralCreate):
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  
        from_attributes = True