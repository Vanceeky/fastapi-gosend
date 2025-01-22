from pydantic import BaseModel



class PayQR(BaseModel):
    merchant_id: str
    amount: float