from sqlalchemy.ext.asyncio import AsyncSession
from utils.responses import json_response
from api.v1.schemas.payQR_schema import PayQR
from api.v1.repositories.user_repository import UserRepository


class PayQRService:

    @staticmethod
    async def pay_qr(db: AsyncSession, pay_qr_data: PayQR, user_id: str):
        try:
            user = await UserRepository.get_user(db, user_id)

            if not user:
                return json_response(
                    message="User not found",
                    status_code=404
                )
            
            target_url = {
                f"https://gosendit.net/paynow.php?"
                f"user_id={user_id}&"
                f"merchant_id={pay_qr_data.merchant_id}&"
                f"amount={pay_qr_data.amount}"
            }
            
            return json_response(
                message = "Successfully fetched PayQR URL",
                data = {
                    "url": target_url
                },
                status_code = 200
            )
        
        except Exception as e:
            print(e)
            return json_response(
                message = "Something went wrong",
                status_code = 500
            )