from pydantic import BaseModel






class pay_qr(BaseModel):
    merchant_id: str
    amount: float