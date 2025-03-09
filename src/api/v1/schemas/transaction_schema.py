from pydantic import BaseModel

from typing import Optional
from datetime import datetime
from decimal import Decimal

class TransactionSchema(BaseModel):
    transaction_id: str
    sender_id: str
    receiver_id: str
    amount: float  # Convert Decimal to float for JSON serialization
    currency: str
    transaction_type: str
    title: str
    description: Optional[str] = None
    sender_name: str
    receiver_name: str
    status: str
    transaction_reference: Optional[str] = None
    extra_metadata: Optional[str] = None
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True  # Allows working with ORM models
        json_encoders = {
            Decimal: float,   # Convert Decimal to float
            datetime: lambda v: v.isoformat()  # Convert datetime to ISO 8601 string
        }

class TransactionCreate(BaseModel):
    full_name: str
    account_number: str
    bank_code: str
    channel: str
    amount: float



class TransactionDetails(BaseModel):
    transaction_id: str
    sender_id: str
    receiver_id: str
    amount: float
    currency: str
    transaction_type: str
    title: str
    description: str
    sender_name: str
    receiver_name: str
    status: str
    transaction_reference: str


class ProcessTransaction(BaseModel):
    transaction_reference: str


class MerchantData(BaseModel):
    disburse_id: str
    merchant_name: str
    amount: float

class ProcessQrphTransaction(BaseModel):
    transaction_reference: str
    disburse_id: str





class DistributionCreate(BaseModel):
    distribution_id: str
    sponsor: str
    amount: float
    type: str
    transaction_id: str
    



