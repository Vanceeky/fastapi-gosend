from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.repositories.web_authentication_repository import WebAuthenticationRepository
from api.v1.schemas.web_authentication_schema import LoginRequest, AuthUser

from utils.responses import json_response
from decouple import config

from core.security import sign_jwt, verify_password

from api.v1.services.otp_service import OTPService

from fastapi import HTTPException

class WebAuthenticationService:

    @staticmethod
    async def verifiy_mpin(db: AsyncSession, mobile_number: str, mpin: str) -> bool:
        try:
            user = await WebAuthenticationRepository.get_user(db, mobile_number)

            if not user:
                print("User not found!")
                return False

            hashed_mpin = user.mpin

            if not hashed_mpin:
                print("No MPIN found for the user!")
                return False


            print(f"Fetched hashed MPIN: {hashed_mpin}")
            print(f"Input MPIN: {mpin}")

            # Verify the hashed MPIN
            is_valid = verify_password(mpin, hashed_mpin)
            print(f"MPIN verification result: {is_valid}")

            return is_valid

        except Exception as e:
            print(f"Error verifying MPIN: {str(e)}")
            return False





    @staticmethod
    async def initiate_login(db: AsyncSession, mobile_number: str):
        try:
            user = await WebAuthenticationRepository.get_user(db, mobile_number)

            if user:
                otp_response = await OTPService.create_otp(db, mobile_number, otp_type="web login")

                return json_response(
                    message = "OTP sent successfully!",
                    data = {
                        "otp_code": otp_response.otp_code,
                        "expired_at": otp_response.expired_at.isoformat() # serialize datetime
                    }
                )


            else:
                return json_response(
                    message="User not found!",
                    data = {
                        "mobile_number": mobile_number
                    },
                    status_code=404
                )
        
        except Exception as e:
            return json_response(
                message=f"An error occured: {str(e)}",
                status_code=500
            )




    @staticmethod
    async def verify_otp_and_authenticate(db: AsyncSession, auth_data: AuthUser):
        try:

            is_valid_otp = await OTPService.verify_otp(db, auth_data.mobile_number, auth_data.otp)

            if not is_valid_otp:
                return json_response(
                    message = "Invalid or expired OTP",
                    status_code=400
                )
            
            user = await WebAuthenticationRepository.get_user(db, auth_data.mobile_number)
            if not user:
                return json_response(
                    message = "User not found!",
                    data = {
                        "mobile_number": auth_data.mobile_number
                    },
                    status_code=404
                )

            is_valid_mpin = await WebAuthenticationService.verifiy_mpin(db, auth_data.mobile_number, auth_data.mpin)

            if not is_valid_mpin:
                return json_response(
                    message = "Invalid MPIN",
                    status_code=400
                )

            access_token = sign_jwt(user.user_id)['access_token']

            return json_response(
                message = "User authenticated!",
                data = {
                    "access_token": access_token,
                    "user_role": user.account_type
                },
                status_code=200
            )
            

            
        except Exception as e:
            return json_response(
                message = f"An error occured {str(e)}",
                status_code = 500
            )
        

