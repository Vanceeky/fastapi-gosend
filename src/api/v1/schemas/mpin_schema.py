from pydantic import BaseModel
from typing import Optional



class MPINRequest(BaseModel):
    imei: Optional[str] = None
    mpin: str


class ResetMPIN(BaseModel):
    otp_code: str
    mpin: str

