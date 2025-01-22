from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from api.v1.repositories.user_repository import UserRepository
from api.v1.repositories.referral_repository import ReferralRepository
from utils.responses import json_response

class UnilevelRepository:
    @staticmethod
    async def get_unilevel2(db: AsyncSession, user_id: str):
        try:

            user = await UserRepository.get_user(db, user_id)

            if user:
                pass


            if not user:
                return json_response(
                    message = "User not found!",
                    status_code = 404,
                    data = {"user_id": user_id}
                )

        except Exception as e:
            raise e
