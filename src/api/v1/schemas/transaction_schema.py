from pydantic import BaseModel


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
    



