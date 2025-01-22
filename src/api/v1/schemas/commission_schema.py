from pydantic import BaseModel
from typing import Optional



class CommissionCreate(BaseModel):
    user_id: str
    transaction_type: str
    level: str
    amount: float
    