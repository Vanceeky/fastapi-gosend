from sqlalchemy.ext.asyncio import AsyncSession
from utils.responses import json_response

from api.v1.repositories.merchant_repository import MerchantRepository
from api.v1.repositories.user_repository import UserRepository


from api.v1.schemas.qr_schema import pay_qr
import httpx
from fastapi import HTTPException


class QRService:
    @staticmethod
    async def get_payQR(db: AsyncSession, pay_qr_data: pay_qr, user_id: str):
        try:
            # Fetch merchant from repository
            merchant = await MerchantRepository.get_merchant(db, pay_qr_data.merchant_id)

            if not merchant:
                return json_response(
                    message="Merchant not found",
                    status_code=404
                )

            # Construct URL
            target_url = (
                f"https://gosendit.net/paynow.php?"
                f"user_id={merchant.user_id}&"
                f"merchant_id={merchant.merchant_id}&"
                f"amount={pay_qr_data.amount}"
            )

            # Success response
            return json_response(
                message="Successfully fetched PayQR URL",
                data={
                    "url": target_url
                },
                status_code=200
            )

            
    
        except Exception as e:

            return json_response(message=str(e), data={}, status_code=500)

    @staticmethod
    async def scan_qrcode(db: AsyncSession, user_id: str):
        try:
            pass
        except Exception as e:
            return json_response(
                message=str(e),
                data={},
                status_code=500
            )
        


    @staticmethod
    async def initiate_qrph_transfer(db: AsyncSession, user_id: str):
        
        try:
            
            user = await UserRepository.get_user(db, user_id)
            

        except Exception as e:
            raise HTTPException(status_code=400, detail = f"Error Initiating QRPH Transfer: {str(e)}")