from sqlalchemy.ext.asyncio import AsyncSession


from models.activation_history_model import ActivationHistory
from api.v1.repositories.user_activation_repository import UserActivationRepository

from utils.responses import json_response

class UserActivationService:
    @staticmethod
    async def initiate_account_activation(db: AsyncSession, user_id: str):
        try:

            user = await UserActivationRepository.get_user_topwallet_id(db, user_id)

        except Exception as e:
            return json_response(
                message=f"Error fetching user topwallet id: {str(e)}",
                data={"user_id": user_id},
                status_code = 404
            )