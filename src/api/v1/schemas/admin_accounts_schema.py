from pydantic import BaseModel
from typing import Optional




class AdminAccountCreate(BaseModel):
    username: str
    password: str
    mobile_number: Optional[str]
    account_type: str

class AdminAccountResponse(BaseModel):
    user_id: str
    username: str
    mobile_number: str
    account_type: str



class AdminLoginRequest(BaseModel):
    username: str
    password: str