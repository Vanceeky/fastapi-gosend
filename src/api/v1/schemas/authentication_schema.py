from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    mobile_number: str
    



class OTPRequest(BaseModel):
    mobile_number: str
    otp: str



class MPINSetupRequest(BaseModel):
    mobile_number: str
    mpin: str

