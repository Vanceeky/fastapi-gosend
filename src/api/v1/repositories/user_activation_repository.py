from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload

#from models.activation_history_model import ActivationHistory
from models.user_model import User

from sqlalchemy.exc import IntegrityError
from utils.responses import json_response

from api.v1.repositories.user_repository import UserRepository
from models.user_model import UserWallet, UserWalletExtension
from fastapi import HTTPException





class UserActivationRepository:
    @staticmethod
    async def get_user_topwallet_id(db: AsyncSession, user_id: str):
        try:
            user_wallet_result = await db.execute(
                select(UserWallet).filter(
                    UserWallet.user_id == user_id
                )
            )


            user_wallet = user_wallet_result.scalars().first()

            if not user_wallet:
                raise ValueError(f"No wallet found for user_id {user_id}")

         
            user_wallet_extension_result = await db.execute(
                select(UserWalletExtension).filter(
                    UserWalletExtension.wallet_id == user_wallet.wallet_id
                )
            )

            user_wallet_extension = user_wallet_extension_result.scalars().first()

            return user_wallet_extension.external_id
        
        except Exception as e:
            return HTTPException(detail=f"Error fetching user topwallet id: {str(e)}")

            
