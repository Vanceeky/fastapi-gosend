from pydantic import BaseModel



class LoginRequest(BaseModel):
    mobile_number: str



class AuthUser(BaseModel):
    mobile_number: str
    mpin: str
    otp: str

class OTPRequest(BaseModel):
    mobile_number: str
    otp: str



