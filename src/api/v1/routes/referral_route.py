from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.schemas.referral_schema import ReferralCreate, ReferralResponse
from api.v1.services.referral_service import ReferralService
from core.database import get_db


router = APIRouter()

@router.post("", response_model=ReferralResponse)
async def create_referral(referral_data: ReferralCreate, db: AsyncSession = Depends(get_db)):
    return await ReferralService.create_referral_service(db, referral_data)


@router.get("", response_model=list[ReferralResponse])
async def get_all_referrals(db: AsyncSession = Depends(get_db)):
    return await ReferralService.get_all_referrals_service(db)

