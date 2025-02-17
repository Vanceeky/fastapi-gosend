from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.reward_history_model import RewardHistory
from models.admin_history_model import AdminRewardHistory
from api.v1.schemas.reward_schema import RewardInput

from fastapi import HTTPException


class RewardDistributionRepository:
    
    @staticmethod
    async def create_reward_distribution_history(db: AsyncSession, reward_history_data: RewardInput):
        try:
            reward = RewardHistory(
                **reward_history_data.dict()
            )
            db.add(reward)

            await db.commit()
            await db.refresh(reward)

            return reward
        
        except Exception as e:
            await db.rollback()
            print(e)
            raise HTTPException(status_code=400, detail=f"Error creating reward: {str(e)}")
        
    @staticmethod
    async def create_admin_reward_distribution_history(db: AsyncSession, reward_history_data: RewardInput):
        try:
            reward = AdminRewardHistory(
                **reward_history_data.dict()
            )
            db.add(reward)

            await db.commit()
            await db.refresh(reward)

            return reward
        
        except Exception as e:
            await db.rollback()
            print(e)
            raise HTTPException(status_code=400, detail=f"Error creating reward for admin: {str(e)}")
        

        