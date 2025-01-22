from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.repositories.kyc_repository import KYCRepository

from utils.responses import json_response
from decouple import config
from fastapi import HTTPException
import httpx 


class KYCService:
    @staticmethod
    async def kyc_topwallet(db: AsyncSession, user_id: str):
        try:
            user_wallet_extension = await KYCRepository.get_user(db, user_id)
            external_id = user_wallet_extension.external_id


            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url = f"{config('TW_API_URL')}/b2bapi/user_kyc_by_id/{external_id}",
                    headers = {
                        "apikey": config('TW_API_KEY'),
                        "secretkey": config("TW_SECRET_KEY"),
                    },
                    json = {
                    "return_url": "https://gosendit.net/kyc_success.php",
                    "display_name": "GoSEND"
                    }
                )

                # Log response details for debugging
                #print(f"Response status code: {response.status_code}")
                #print(f"Response headers: {response.headers}")
                #print(f"Response text: {response.text}")

                # Handle 400 status code
                if response.status_code == 400:
                    try:
                        error_data = response.json()
                    except ValueError:
                        error_data = {"message": response.text.strip() or "Invalid request format"}
                    return json_response(
                        message="Bad Request",
                        data=error_data,
                        status_code=400
                    )

                # Handle 200 status code
                if response.status_code == 200:
                    try:
                        return json_response(
                            message="KYC details fetched successfully",
                            data=response.json(),
                            status_code=200
                        )
                    except ValueError:
                        return json_response(
                            message="KYC details fetched, but response could not be parsed",
                            data={"raw_response": response.text},
                            status_code=200
                        )

                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"message": response.text.strip() or "Unknown error occurred"}
                return json_response(
                    message="KYC details not found",
                    data=error_data,
                    status_code=response.status_code
                )
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        