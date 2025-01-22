from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from api.v1.repositories.user_repository import UserRepository
from models.user_model import User
from utils.responses import json_response
from api.v1.services.otp_service import OTPService
from api.v1.schemas.user_schema import UserResponse, UserAddressCreate, UserDetailCreate
from api.v1.schemas.mpin_schema import MPINRequest, ResetMPIN
from api.v1.repositories.kyc_repository import KYCRepository
import httpx
from decouple import config

class MPINService:




    @staticmethod
    async def validate_mpin(db: AsyncSession, validateMPIN: MPINRequest, user_id: str):
        try:
            user = await UserRepository.get_user(db, user_id)

            user_topwallet_id = await KYCRepository.get_user(db, user_id)

            user_topwallet_id = user_topwallet_id.external_id

            if user:
                if user.mpin != validateMPIN.mpin:
                    return json_response(
                        message="Invalid MPIN",
                        status_code=404
                    )
                if not user.mpin:
                    return json_response(
                        message="MPIN not set",
                        status_code=404
                    )
                
                if user.mpin == validateMPIN.mpin:


                    async with httpx.AsyncClient() as client:

                        response = await client.post(
                            url = f"{config('TW_API_URL')}/b2bapi/get_profile",
                            headers = {
                                "apikey": config('TW_API_KEY'),
                                "secretkey": config("TW_SECRET_KEY"),
                            },
                            json={"userid": user_topwallet_id}
                        )


                        if response.status_code != 200:
                            try:
                                error_data = response.json()
                            except Exception:
                                error_data = {"message": response.text.strip()}

                            return json_response(
                                message="Failed to fetch user details",
                                data = error_data,
                                status_code = response.status_code
                            )

                        else:
                            return json_response(
                                message="Successfully fetched user details",
                                data = response.json(),
                                status_code = 200
                            )

                
            
                
            else:
                return json_response(
                    message="User not found",
                    data = {**validateMPIN.dict(), "user_id": user_id},
                    status_code=404
                )

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
 


    @staticmethod
    async def set_mpin(db: AsyncSession, mpin_data: MPINRequest, user_id: str):
        try:
            user = await UserRepository.get_user(db, user_id)

            if not user.mpin:
                user.mpin = mpin_data.mpin
                db.add(user)
                await db.commit()
                return json_response(
                    message="MPIN set successfully",
                    data = {
                        "phone_number": user.mobile_number,
                        "mpin": mpin_data.mpin,
                    },
                    status_code=200
                )
            else:
                return json_response(
                    message="MPIN already set",
                    status_code=400
                )

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        
    
    @staticmethod
    async def initiate_mpin_reset(db: AsyncSession, user_id: str):
        try:
            user = await UserRepository.get_user(db, user_id)

            if user:
                otp_response = await OTPService.create_otp(db, user.mobile_number, otp_type="mpin_reset")

                return json_response(
                    message="OTP sent successfully",
                    data={
                        "otp_code": otp_response.otp_code,
                        "expired_at": otp_response.expired_at.isoformat()  # serialize datetime
                    }
                )

            else:
                return json_response(
                    message="User not found",
                    data={"user_id": user_id},
                    status_code=404
                )



        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
            
    @staticmethod
    async def process_mpin_reset(db: AsyncSession, mpin_data: ResetMPIN, mobile_number):
        try:
            #user = await UserRepository.get_user(db, mobile_number)
            #mobile_number = user.mobile_number
        
            is_valid_otp = await OTPService.verify_otp(db, mpin_data.otp_code, mobile_number)

            if is_valid_otp:
                return json_response(
                    message="OTP verified successfully",
                    data={"new_mpin": mpin_data.mpin},
                    status_code=200
                )
            
            else:
                return json_response(
                    message="Invalid or expired OTP",
                    data={
                        "mobile_number": mobile_number,
                        "OTP": mpin_data.otp_code
                    },
                    status_code=400
                )
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))