from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.repositories.authentication_repository import AuthenticationRepository
from utils.responses import json_response
from api.v1.services.otp_service import OTPService
from api.v1.schemas.authentication_schema import LoginRequest
from core.security import sign_jwt
import httpx
from decouple import config

from api.v1.repositories.kyc_repository import KYCRepository

class AuthenticationService:
    @staticmethod
    async def initiate_login(db: AsyncSession, mobile_number: str):
        try:
            user = await AuthenticationRepository.get_user_by_mobile_number(db, mobile_number)

            if user:
                otp_response = await OTPService.create_otp(db, mobile_number, otp_type="login")

                # send otp to mobile number, comment for a while 
                #await OTPService.send_otp(mobile_number, otp_response.otp_code)

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
                    data={"mobile_number": mobile_number},
                    status_code=404
                )

        except Exception as e:
            raise e

    @staticmethod
    async def process_login(db: AsyncSession, data: LoginRequest, otp_code: str):

        # extract mobile number from data
        mobile_number = data.mobile_number

        # get user 

        user = await AuthenticationRepository.get_user_by_mobile_number(db, mobile_number)

        if not user.mpin:
            mpin_status = False
        else:
            mpin_status = True

        is_valid_otp = await OTPService.verify_otp(db, mobile_number, otp_code)

        if is_valid_otp:
            # generate the access token 
            access_token = sign_jwt(user.user_id)["access_token"]

            user = await KYCRepository.get_user(db, user.user_id)

            external_id = user.external_id


            async with httpx.AsyncClient() as client:
                response = await client.post(
                        url = f"{config('TW_API_URL')}/b2bapi/get_profile/",
                        headers = {
                            "apikey": config('TW_API_KEY'),
                            "secretkey": config("TW_SECRET_KEY"),
                        },
                        json = {
                            'userid': external_id
                        }
                    )
                
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                    except ValueError:
                        error_data = {"message": response.text.strip() or "Invalid request format"}
                    return json_response(
                        message="Bad Request",
                        data=error_data,
                        status_code=400
                    )
                else:
     
                    return json_response(
                        message="You have successfully logged in",
                        data={
                            "mpin_status": mpin_status,  
                            "access_token": access_token, 
                            'user_data': response.json()
                        },
                        status_code=200
                    )
        else:
          
            return json_response(
                message="Invalid or expired OTP",
                data={"mobile_number": mobile_number},  
                status_code=400
            )



        


