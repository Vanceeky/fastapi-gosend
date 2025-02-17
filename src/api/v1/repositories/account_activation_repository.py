from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.activation_history_model import ActivationHistory

from fastapi import HTTPException



class ActivationHistoryRepository:
    @staticmethod
    async def get_activation_history(db: AsyncSession, reference_id: str):

        try:
            result = await db.execute(
                select(ActivationHistory).where(
                    ActivationHistory.reference_id == reference_id
                )
            )

            activation_history = result.scalars().first()

            return activation_history
        
        except Exception as e:
            raise e
        
    