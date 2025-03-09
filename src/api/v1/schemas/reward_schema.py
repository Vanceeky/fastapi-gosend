from pydantic import BaseModel

from typing import Optional
from datetime import datetime

class RewardInput(BaseModel):
    id: str
    reference_id: str
    reward_source_type: str
    reward_points: float
    reward_from: str
    receiver: str
    reward_type: str
    description: str
    #updated_at: str
    #created_at: str

class UserSchema(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    suffix_name: Optional[str] = None


class RewardHistorySchema(BaseModel):
    id: str
    reference_id: str
    reward_source_type: str
    reward_points: float
    reward_from: Optional[UserSchema] = None
    receiver: Optional[UserSchema] = None
    reward_type: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
