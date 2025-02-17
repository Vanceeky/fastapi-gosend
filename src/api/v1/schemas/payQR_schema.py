from pydantic import BaseModel



class PayQR(BaseModel):
    merchant_id: str
    #customer_id: str
    amount: float


class ProcessPayTransaction(BaseModel):
    reference_id: str
   # otp: str