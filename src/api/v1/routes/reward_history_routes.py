from fastapi import APIRouter, Depends, HTTPException
from core.security import get_jwt_identity, JWTBearer
from core.database import get_db

from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.services.reward_distribution_service import RewardDistributionRepository
from fastapi import status



router = APIRouter()

@router.get('/reward-history/', status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def get_all_rewards(db: AsyncSession = Depends(get_db), token: str = Depends(JWTBearer())):
    user_id = get_jwt_identity(token)
    return await RewardDistributionRepository.get_all_rewards(db)

