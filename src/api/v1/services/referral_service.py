from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from utils.responses import json_response
from api.v1.repositories.referral_repository import ReferralRepository
from models.referral_model import Commission
from api.v1.schemas.referral_schema import ReferralCreate, ReferralResponse
from api.v1.repositories.user_repository import UserRepository
from models.user_model import User
from sqlalchemy import select

from uuid import uuid4

class ReferralService:
        
    @staticmethod
    async def get_all_referrals_service(db: AsyncSession):
        try:
            referrals = await ReferralRepository.get_all_referrals(db)
            return referrals

        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to get referrals")
    


    @staticmethod
    async def create_referral_service(db: AsyncSession, referral_data: ReferralCreate):
        try:
            user = await UserRepository.get_user(db, referral_data.referred_to)


            if user:
                new_referral = await ReferralRepository.create_referral(db, referral_data.referred_by, referral_data.referred_to)

                return json_response(
                    status_code=201,
                    message="Referral created successfully",
                    data={"referral_id": new_referral.referral_id}
                )

            if not user:
                return json_response(
                    status_code=404,
                    message = "User not found!",
                    data={"user_id": referral_data.referred_to}
                )
 
        except Exception as e:
            return json_response(
                status_code = 404,
                message = str(e),
                data = {"user_id": referral_data.referred_to}
            )
        
    @staticmethod
    async def create_referral_service2(db: AsyncSession, referral_data: ReferralCreate) -> ReferralResponse:
        try:
            
            referred_by = referral_data.referred_by
            #referred_to = referral_data.referred_to

            referred_user_level = 1

            if referred_by:
                referrer = await UserRepository.get_user(db, referred_by)

                if not referrer:
                    return HTTPException(status_code=404, detail="Referrer not found")
                
                referred_user_level = referrer.unilevel + 1

                if referred_user_level > 3:
                    referred_user_level = 3
                
            
            new_referral = await ReferralRepository.create_referral(db, referral_data.referred_by, referral_data.referred_to)

            return {"referral_id": new_referral.referral_id}

            """
            return json_response(
                status_code=201,
                message="Referral created successfully",
                data={"referral_id": new_referral.referral_id}
            )
            """

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to create referral")
        

    @staticmethod
    async def create_commission2(db: AsyncSession, referred_to: str):
        unilevel_distribution_amount = {1: 40.00, 2: 10.00, 3: 5.00}

        try:
            referral = await ReferralRepository.get_referral(db, referred_to)

            if referral:
                # Start from the direct referrer of the referred_to user
                referrer_user_id = referral.referred_by
                level = 1  # Start at Level 1

                while referrer_user_id and level <= 3:
                    # Fetch the referrer user
                    referrer = await UserRepository.get_user(db, referrer_user_id)
                    if not referrer:
                        break

                    # Update the unilevel if not already set
                    if referrer.unilevel < level:
                        referrer.unilevel = level
                        db.add(referrer)

                    # Create a commission record for the referrer
                    commission = Commission(
                        commission_id=str(uuid4()),
                        user_id=referrer.user_id,
                        triggered_by=referred_to,
                        level=level,
                        amount=unilevel_distribution_amount[level],
                    )
                    db.add(commission)

                    # Move to the next level up the hierarchy
                    next_referral = await ReferralRepository.get_referral(db, referrer_user_id)
                    if not next_referral:
                        break
                    referrer_user_id = next_referral.referred_by
                    level += 1

                await db.commit()
                return json_response(
                    status_code=201,
                    message="Commission created successfully",
                )

            else:
                return json_response(
                    status_code=404,
                    message="Referral not found",
                    data={"referred_to": referred_to}
                )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create commission: {str(e)}")


    @staticmethod
    async def create_commission(db: AsyncSession, user_id: str):
        try:
            user = await UserRepository.get_user(db, user_id)

            if not user:
                return json_response(
                    status_code=404,
                    message="User not found",
                    data={"user_id": user_id}
                )
            
            unilevel_distribution_amount = {
                "first_level": 40.00,
                "second_level": 10.00,
                "third_level": 5.00
            }

            # Fetch the user's referral levels

            # Create a commission record for the user

            

        except Exception as e:
            raise e
