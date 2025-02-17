from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from api.v1.schemas.user_schema import UserResponse
from utils.responses import datetime_to_str





class MerchantDetailsCreate(BaseModel): # USED
    latitude: str
    longitude: str

    contact_number: str
    business_email: str
    #password: str

    region: str
    province: str
    municipality_city: str
    barangay: str
    street: Optional[str]

    class Config:
        orm_mode = True
        from_attributes = True

class MerchantCreate(BaseModel): # USED
    #merchant_id: str
    mobile_number: str
    business_name: str
    business_type: str
    discount: float

    status: bool
    merchant_details: MerchantDetailsCreate

    class Config:
        orm_mode = True
        from_attributes = True


# Pydantic Model for MerchantDetails when returning data
class MerchantDetailsResponse(BaseModel):
    latitude: str
    longitude: str

    contact_number: str
    business_email: str

    region: str
    province: str
    municipality_city: str
    barangay: str
    street: Optional[str]

    created_at: str
    updated_at: str

    class Config:
        orm_mode = True
        from_attributes = True






# Response model for returning merchant data
class MerchantResponse(BaseModel):
    #merchant_id: str
    mobile_number: str
    business_name: str
    business_type: str
    discount: float

    status: bool
    merchant_details: List[MerchantDetailsCreate]

    class Config:
        orm_mode = True
        from_attributes = True


# Pydantic Model for Updating MerchantDetails
class MerchantDetailsUpdate(BaseModel):
    latitude: Optional[str] = None  
    longitude: Optional[str] = None  
    merchant_name: Optional[str] = None
    merchant_address: Optional[str] = None 

    class Config:
        orm_mode = True
        from_attributes = True


# Pydantic Model for Updating Merchant
class MerchantUpdate(BaseModel):
   # user_id: Optional[str] = None  
    #business_name: str
    #business_type: str
    discount: float
    status: Optional[bool] = None  
    merchant_details: List[MerchantDetailsCreate]


    class Config:
        orm_mode = True
        from_attributes = True




class PurchaseData(BaseModel):
    amount: float
