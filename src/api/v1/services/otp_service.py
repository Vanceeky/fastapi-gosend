from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.repositories.otp_repository import OTPRepository
from utils.responses import json_response
from datetime import datetime, timedelta
from api.v1.schemas.otp_schema import OTPRecordCreate, OTPRecordResponse
#from sqlalchemy import func
from random import choices
from uuid import uuid4

from decouple import config

class OTPService:

    @staticmethod
    async def generate_otp():
        return "".join(choices('0123456789', k=6))


    @staticmethod
    async def verify_otp(db: AsyncSession, mobile_number: str, otp_code: str) -> bool:
        
        otp_record = await OTPRepository.get_by_number_and_code(db, mobile_number, otp_code)

        if not otp_record or otp_record.is_used or otp_record.expired_at < datetime.utcnow():
            return False

        await OTPRepository.mark_as_used(db, otp_record.otp_id)

        return True

    @staticmethod
    async def create_otp(db: AsyncSession, mobile_number: str, otp_type: str) -> OTPRecordResponse:
        otp_code = await OTPService.generate_otp()
        otp_id = str(uuid4())
        expired_at = datetime.utcnow() + timedelta(seconds=180) # 3 minutes
        
        otp_data = OTPRecordCreate(
            otp_id=otp_id,
            mobile_number=mobile_number,
            otp_code=otp_code,
            otp_type=otp_type,
            expired_at=expired_at
        )

        otp_record = await OTPRepository.create_otp(db, otp_data)
        return otp_record
    
    @staticmethod
    async def send_otp(recipient: str, otp_code: str):
        import aiohttp
        payload = {
            "Email": config("ITEXMO_API_EMAIL"),
            "Password": config("ITEXMO_API_PASSWORD"),
            "ApiCode": config("ITEXMO_API_CODE"),
            "SenderId": config("ITEXMO_SENDER_ID"),
            "Recipients": [recipient],
            "Message": f"DO NOT SHARE YOUR OTP, your One-Time-Pin is {otp_code}",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=config("ITEXMO_API_ENDPOINT"),
                    json=payload,
                    headers={"Content-Type": "application/json"},
                ) as response:
                    response_text = await response.text()
                    print(f"Raw Response: {response_text}")  

                    if response.status != 200:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Error sending OTP to {recipient}: {response_text}",
                        )

                    response_json = await response.json()
                    print(f"Parsed Response JSON: {response_json}") 

                    
                    if response_json.get("Error", True): 
                        raise HTTPException(
                            status_code=400,
                            detail=f"Failed to send OTP: {response_json.get('Failed', 'Unknown error')}",
                        )

                    return response_json

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred: {str(e)}",
            )


    @staticmethod
    async def send_otp2(recipient: str, otp_code: str):
        import aiohttp
        # Prepare the payload
        payload = {
            "Email": config("ITEXMO_API_EMAIL"),
            "Password": config("ITEXMO_API_PASSWORD"),
            "ApiCode": config("ITEXMO_API_CODE"),
            "SenderId": config("ITEXMO_SENDER_ID"),
            "Recipients": [recipient],
            "Message": f"DO NOT SHARE YOUR OTP, your One-Time-Pin is {otp_code}",
        }

        try:
        
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=config("ITEXMO_API_ENDPOINT"),
                    json=payload,  
                    headers={"Content-Type": "application/json"}, 
                ) as response:
                    response_text = await response.text()

                    print(f"Raw Response: {response_text}")  # Debug raw response
                    
                    if response.status != 200:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Error sending OTP to {recipient}: {response_text}",
                        )
                    
                  
                    response_json = await response.json()
                    

                    print(f"Parsed Response JSON: {response_json}")  # Debug parsed JSON
                  
                    if response_json.get("status") != "success":
                        raise HTTPException(
                            status_code=400,
                            detail=f"Failed to send OTP: {response_json.get('message', 'Unknown error')}",
                        )
                    
                    return response_json

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred: {str(e)}",
            )

