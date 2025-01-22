from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from utils.responses import datetime_to_str



class OTPRecordCreate(BaseModel):
    otp_id: str
    mobile_number: str = Field(..., max_length=11)
    otp_code: str = Field(..., max_length=6)
    otp_type: str
    expired_at: datetime


class OTPRecordResponse(BaseModel):
    otp_id: str
    mobile_number: str
    otp_code: str
    otp_type: str
    is_used: bool
    expired_at: datetime
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


    @classmethod
    def from_orm(cls, obj):
        """
        Converts the SQLAlchemy object to the Pydantic response model.

        Args:
            obj: The SQLAlchemy object to convert.

        Returns:
            UserResponse: The converted user response object.
        """
        obj_dict = obj.__dict__

        if 'created_at' in obj_dict:
            obj_dict['created_at'] = datetime_to_str(obj_dict['created_at'])
        if 'updated_at' in obj_dict:
            obj_dict['updated_at'] = datetime_to_str(obj_dict['updated_at'])


        return super().from_orm(obj)





