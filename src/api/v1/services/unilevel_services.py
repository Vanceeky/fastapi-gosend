from sqlalchemy.ext.asyncio import AsyncSession
from utils.responses import json_response

from api.v1.repositories.user_repository import UserRepository
from fastapi import HTTPException
from api.v1.repositories.referral_repository import ReferralRepository


from decouple import config

class UnilevelService:
    @staticmethod
    async def add_user_unilevel(db: AsyncSession, user_id: str):
        try:
            user = await UserRepository.get_user(db, user_id)
        

        except HTTPException as e:
            return json_response(
                message = "User not found!",
                status_code = e.status_code,
            )
        
    
    # Add if there is no unilevel direct the reward to admin account
    @staticmethod
    async def get_user_unilevel(db: AsyncSession, user_id: str):
        try:
            # get the first-level referral (who referred this user)
            first_level = await ReferralRepository.get_referral(db, user_id)
            
            if not first_level:
                return {"first_level": config("GOSEND_ADMIN"), "second_level": config("GOSEND_ADMIN"), "third_level": config("GOSEND_ADMIN")}
            
            # get the second-level referral (who referred the first-level user)
            second_level = await ReferralRepository.get_referral(db, first_level)
            if not second_level:
                return {"first_level": first_level, "second_level": config("GOSEND_ADMIN"), "third_level": config("GOSEND_ADMIN")}
            
            # get the third-level referral (who referred the second-level user)
            third_level = await ReferralRepository.get_referral(db, second_level)
            if not third_level:
                return {"first_level": first_level, "second_level": second_level, "third_level": config("GOSEND_ADMIN")}
            
            return {
                "first_level": first_level,
                "second_level": second_level,
                "third_level": third_level,
            }
            
        except Exception as e:
            raise e



    @staticmethod
    async def get_user_umilevel_5(db: AsyncSession, user_id: str):
        try:
            first_level = await ReferralRepository.get_referral(db, user_id)
            if not first_level:
                return {
                    "first_level": config("GOSEND_ADMIN"),
                    "second_level": config("GOSEND_ADMIN"),
                    "third_level": config("GOSEND_ADMIN"),
                    'forth_level': config("GOSEND_ADMIN"),
                    'fifth_level': config("GOSEND_ADMIN"),
                }
            
            second_level = await ReferralRepository.get_referral(db, first_level)
            if not second_level:
                return {
                    "first_level": first_level,
                    "second_level": config("GOSEND_ADMIN"),
                    "third_level": config("GOSEND_ADMIN"),
                    'forth_level': config("GOSEND_ADMIN"),
                    'fifth_level': config("GOSEND_ADMIN"),
                }
            
            third_level = await ReferralRepository.get_referral(db, second_level)
            if not third_level:
                return {
                    "first_level": first_level,
                    "second_level": second_level,
                    "third_level": config("GOSEND_ADMIN"),
                    'forth_level': config("GOSEND_ADMIN"),
                    'fifth_level': config("GOSEND_ADMIN"),
                }
            
            forth_level = await ReferralRepository.get_referral(db, third_level)
            if not forth_level:
                return {
                    "first_level": first_level,
                    "second_level": second_level,
                    "third_level": third_level,
                    'forth_level': config("GOSEND_ADMIN"),
                    'fifth_level': config("GOSEND_ADMIN"),
                }
            
            fifth_level = await ReferralRepository.get_referral(db, forth_level)
            if not fifth_level:
                return {
                    "first_level": first_level,
                    "second_level": second_level,
                    "third_level": third_level,
                    'forth_level': forth_level,
                    'fifth_level': config("GOSEND_ADMIN"),
                }
            

            return {
                "first_level": first_level,
                "second_level": second_level,
                "third_level": third_level,
                'forth_level': forth_level,
                'fifth_level': fifth_level,
            }
            
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error fetching user unilevel up to 5 levels: {str(e)}")



    @staticmethod
    async def get_user_unilevel2(db: AsyncSession, user_id: str):
        try:
            first_level = await ReferralRepository.get_referral(db, user_id)
            if not first_level:
                return {"first_level": None, "second_level": None, "third_level": None}

            second_level = await ReferralRepository.get_referral(db, first_level.referred_by)
            if not second_level:
                second_level = None
                
            third_level = None
            if third_level:
                third_level = await ReferralRepository.get_referral(db, second_level.referred_by)

            # add transaction history, create unilevel repository for database operation

            # Now distribute rewards based on the referral chain
            unilevel_distribution_amount = {
                1: 40,  # Level 1 gets 40 pesos
                2: 10,  # Level 2 gets 10 pesos
                3: 5    # Level 3 gets 5 pesos
            }

            # Fetch the user's referral levels
            unilevel = await UnilevelService.get_user_unilevel(db, user_id)

            # Distribute rewards to the appropriate levels
            if unilevel["first_level"]:
                first_level_user = unilevel["first_level"].referred_by
                if first_level_user:
                    first_level_reward = unilevel_distribution_amount[1]
                    first_level_user.reward_balance += first_level_reward
                    db.add(first_level_user)
                    await db.commit()
                    await db.refresh(first_level_user)

            if unilevel["second_level"]:
                second_level_user = unilevel["second_level"].referred_by
                if second_level_user:
                    second_level_reward = unilevel_distribution_amount[2]
                    second_level_user.reward_balance += second_level_reward
                    db.add(second_level_user)
                    await db.commit()
                    await db.refresh(second_level_user)

            if unilevel["third_level"]:
                third_level_user = unilevel["third_level"].referred_by
                if third_level_user:
                    third_level_reward = unilevel_distribution_amount[3]
                    third_level_user.reward_balance += third_level_reward
                    db.add(third_level_user)
                    await db.commit()
                    await db.refresh(third_level_user)


            # Construct response with appropriate values
            return {
                "first_level": first_level,
                "second_level": second_level,
                "third_level": third_level
            }
        
        except Exception as e:
            # Handle any potential errors
            raise e



    @staticmethod
    async def distribute_reward_to_user(db: AsyncSession, user_id: str, amount:float):
        unilevel_distribution_amounts = {
            "first_level": 40,
            "second_level": 10,
            "third_level": 5,
        }

        return unilevel_distribution_amounts

        




