from sqlalchemy.ext.asyncio import AsyncSession
from utils.responses import json_response

from api.v1.repositories.user_repository import UserRepository
from fastapi import HTTPException
from api.v1.repositories.referral_repository import ReferralRepository


from decimal import Decimal
from uuid import uuid4
from api.v1.schemas.reward_schema import RewardInput
from api.v1.repositories.reward_distribution_repository import RewardDistributionRepository

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
                return {"first_level": config("ADMIN_STAGING"), "second_level": config("ADMIN_STAGING"), "third_level": config("ADMIN_STAGING")}
            
            # get the second-level referral (who referred the first-level user)
            second_level = await ReferralRepository.get_referral(db, first_level)
            if not second_level:
                return {"first_level": first_level, "second_level": config("ADMIN_STAGING"), "third_level": config("ADMIN_STAGING")}
            
            # get the third-level referral (who referred the second-level user)
            third_level = await ReferralRepository.get_referral(db, second_level)
            if not third_level:
                return {"first_level": first_level, "second_level": second_level, "third_level": config("ADMIN_STAGING")}
            
            return {
                "first_level": first_level,
                "second_level": second_level,
                "third_level": third_level,
            }
            
        except Exception as e:
            raise e


    @staticmethod
    async def get_user_unilevel_5(db: AsyncSession, user_id: str):
        try:
            levels = {}  # Store user_id and reward_points for each level
            current_user_id = user_id

            for level in range(1, 6):  # Loop through levels 1 to 5
                if current_user_id == config("ADMIN_STAGING"):  
                    # If the previous level was ADMIN_STAGING, no need to query further
                    levels[f"level_{level}"] = {"user_id": config("ADMIN_STAGING"), "reward_points": 0.0}
                else:
                    referrer_id = await ReferralRepository.get_referral(db, current_user_id) or config("ADMIN_STAGING")
                    reward_points = await UserRepository.get_user_reward_points(db, referrer_id) if referrer_id != config("ADMIN_STAGING") else 0.0
                    levels[f"level_{level}"] = {"user_id": referrer_id, "reward_points": reward_points}
                    current_user_id = referrer_id  # Move up the chain

            return levels  # Return structured response
        
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error fetching user unilevel rewards: {str(e)}")

    @staticmethod
    async def get_user_unilevel_5_test(db: AsyncSession, user_id: str):
        try:
            # Fetching the first referral level (if exists)
            first_level = await ReferralRepository.get_referral(db, user_id)
            if not first_level:
                first_level = config("ADMIN_STAGING")  # Default if no referral
            first_level_reward_points = await UserRepository.get_user_reward_points(db, first_level)  # Get reward points for first level

            # Fetching second level referral (if exists)
            second_level = await ReferralRepository.get_referral(db, first_level)
            if not second_level:
                second_level = config("ADMIN_STAGING")  # Default if no referral
            second_level_reward_points = await UserRepository.get_user_reward_points(db, second_level)  # Get reward points for second level

            # Fetching third level referral (if exists)
            third_level = await ReferralRepository.get_referral(db, second_level)
            if not third_level:
                third_level = config("ADMIN_STAGING")  # Default if no referral
            third_level_reward_points = await UserRepository.get_user_reward_points(db, third_level)  # Get reward points for third level

            # Fetching forth level referral (if exists)
            fourth_level = await ReferralRepository.get_referral(db, third_level)
            if not fourth_level:
                fourth_level = config("ADMIN_STAGING")  # Default if no referral
            forth_level_reward_points = await UserRepository.get_user_reward_points(db, fourth_level)  # Get reward points for forth level

            # Fetching fifth level referral (if exists)
            fifth_level = await ReferralRepository.get_referral(db, fourth_level)
            if not fifth_level:
                fifth_level = config("ADMIN_STAGING")  # Default if no referral
            fifth_level_reward_points = await UserRepository.get_user_reward_points(db, fifth_level)  # Get reward points for fifth level

            return {
                "first_level": {"user_id": first_level, "reward_points": first_level_reward_points},
                "second_level": {"user_id": second_level, "reward_points": second_level_reward_points},
                "third_level": {"user_id": third_level, "reward_points": third_level_reward_points},
                "forth_level": {"user_id": fourth_level, "reward_points": forth_level_reward_points},
                "fifth_level": {"user_id": fifth_level, "reward_points": fifth_level_reward_points},
            }
        
            """
            SAMPLE RESPONSE
            {
                "first_level": {"user_id": "user1", "reward_points": 50.0},
                "second_level": {"user_id": "user2", "reward_points": 30.0},
                "third_level": {"user_id": "user3", "reward_points": 20.0},
                "forth_level": {"user_id": "user4", "reward_points": 15.0},
                "fifth_level": {"user_id": "user5", "reward_points": 10.0}
            }
            
            """

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error fetching user unilevel up to 5 levels with reward points: {str(e)}")


    @staticmethod
    async def get_user_unilevel_5_main(db: AsyncSession, user_id: str):
        try:
            # Fetching the first referral level (if exists)
            first_level = await ReferralRepository.get_referral(db, user_id)
            if not first_level:
                return {
                    "first_level": config("ADMIN_STAGING"),
                    "second_level": config("ADMIN_STAGING"),
                    "third_level": config("ADMIN_STAGING"),
                    'forth_level': config("ADMIN_STAGING"),
                    'fifth_level': config("ADMIN_STAGING"),
                }
            
            
            # Fetching second level referral (if exists)
            second_level = await ReferralRepository.get_referral(db, first_level)
            if not second_level:
                return {
                    "first_level": first_level,
                    "second_level": config("ADMIN_STAGING"),
                    "third_level": config("ADMIN_STAGING"),
                    'forth_level': config("ADMIN_STAGING"),
                    'fifth_level': config("ADMIN_STAGING"),
                }
            
            # Fetching third level referral (if exists)
            third_level = await ReferralRepository.get_referral(db, second_level)
            if not third_level:
                return {
                    "first_level": first_level,
                    "second_level": second_level,
                    "third_level": config("ADMIN_STAGING"),
                    'forth_level': config("ADMIN_STAGING"),
                    'fifth_level': config("ADMIN_STAGING"),
                }
            
            # Fetching forth level referral (if exists)
            forth_level = await ReferralRepository.get_referral(db, third_level)
            if not forth_level:
                return {
                    "first_level": first_level,
                    "second_level": second_level,
                    "third_level": third_level,
                    'forth_level': config("ADMIN_STAGING"),
                    'fifth_level': config("ADMIN_STAGING"),
                }
            
            # Fetching fifth level referral (if exists)
            fifth_level = await ReferralRepository.get_referral(db, forth_level)
            if not fifth_level:
                return {
                    "first_level": first_level,
                    "second_level": second_level,
                    "third_level": third_level,
                    'forth_level': forth_level,
                    'fifth_level': config("ADMIN_STAGING"),
                }

            # Return all the levels if all are found
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
    


    @staticmethod
    async def distribute_unilevel_rewards_test(db: AsyncSession, user_id: str, reward_pool: Decimal):
        try:
            # Reward percentages based on the given structure
            reward_distribution = {
                "level_1": Decimal('0.06') * Decimal('0.8'),
                "level_2": Decimal('0.05') * Decimal('0.8'),
                "level_3": Decimal('0.04') * Decimal('0.8'),
                "level_4": Decimal('0.03') * Decimal('0.8'),
                "level_5": Decimal('0.02') * Decimal('0.8'),
            }

            # Fetch the 5-level referral structure
            referral_levels = await RewardRepository.get_user_unilevel_5_main(db, user_id)

            # Iterate over each level and distribute rewards
            for level, percentage in reward_distribution.items():
                referrer_id = referral_levels[level]
                reward_amount = reward_pool * percentage  # Calculate reward
                
                # Update the referrer's wallet balance
                await UserRepository.update_reward_points(db, referrer_id, reward_amount)

            await db.commit()  # Commit transaction

            return json_response(
                message="Unilevel rewards distributed successfully",
                data={
                    "reward_pool": str(reward_pool),
                    "distributed_rewards": {level: str(reward_pool * percentage) for level, percentage in reward_distribution.items()}
                },
                status_code=200
            )

        except Exception as e:
            await db.rollback()  # Rollback transaction if error occurs
            raise HTTPException(status_code=500, detail=f"Error distributing unilevel rewards: {str(e)}")


    @staticmethod
    async def distribute_unilevel_rewards(db: AsyncSession, user_id: str, reward_pool: float, reference_id: str):
        try:
            from decimal import Decimal  # Ensure Decimal precision

            unilevel_distribution = {
                "Level 1": Decimal(reward_pool) * Decimal('0.06') * Decimal('0.8'),
                "Level 2": Decimal(reward_pool) * Decimal('0.05') * Decimal('0.8'),
                "Level 3": Decimal(reward_pool) * Decimal('0.04') * Decimal('0.8'),
                "Level 4": Decimal(reward_pool) * Decimal('0.03') * Decimal('0.8'),
                "Level 5": Decimal(reward_pool) * Decimal('0.02') * Decimal('0.8'),
            }

            GOSEND_ADMIN = config("ADMIN_STAGING")
            current_user = user_id
            total_admin_reward = Decimal("0")  # Track admin's unilevel rewards separately

            for level, reward in unilevel_distribution.items():
                referrer = await ReferralRepository.get_referral(db, current_user)  # Get referrer

                if not referrer:  
                    total_admin_reward += reward  # Track reward for admin
                    continue  # Skip updating a missing referrer

                # Fetch referrer's current reward points
                referrer_reward_points = await UserRepository.get_user_reward_points(db, referrer)

                # Update referrer's reward points
                updated_reward_points = reward
                await UserRepository.update_user_reward_points(db, referrer, updated_reward_points)

                # Store reward history
                reward_history_data = RewardInput(
                    id=str(uuid4()),
                    reference_id=reference_id,
                    reward_source_type="Unilevel Reward",
                    reward_points=reward,
                    reward_from=user_id,
                    receiver=referrer,
                    reward_type=f"{level} Unilevel Reward",
                    description=f"{level} Unilevel reward of {reward} points credited to {referrer}",
                )
                await RewardDistributionRepository.create_reward_distribution_history(db, reward_history_data)
                #await RewardDistributionRepository.create_admin_reward_distribution_history(db, reward_history_data)

                current_user = referrer  # Move to next referrer

            # 🔹 Update admin reward once after the loop
            if total_admin_reward > 0:
                admin_reward_points = await UserRepository.get_user_reward_points(db, GOSEND_ADMIN)
                print("Unilevel admin reward pointsss:", admin_reward_points)
                updated_admin_points = total_admin_reward
                print("Unilevel updated admin reward pointsss:", updated_admin_points)
                await UserRepository.update_user_reward_points(db, GOSEND_ADMIN, updated_admin_points)

                # Store admin reward history
                admin_reward_history = RewardInput(
                    id=str(uuid4()),
                    reference_id=reference_id,
                    reward_source_type="Unilevel Reward",
                    reward_points=total_admin_reward,
                    reward_from=user_id,
                    receiver=GOSEND_ADMIN,
                    reward_type="Unilevel Admin Reward",
                    description=f"Admin received {total_admin_reward} unilevel reward points",
                )
                await RewardDistributionRepository.create_reward_distribution_history(db, admin_reward_history)
                # Store admin reward history
                admin_reward_history_entry = RewardInput(
                    id=str(uuid4()),  # Ensure a new UUID
                    reference_id=reference_id,
                    reward_source_type="Unilevel Reward",
                    reward_points=total_admin_reward,
                    reward_from=user_id,
                    receiver=GOSEND_ADMIN,
                    reward_type="Unilevel Admin Reward",
                    description=f"Admin received {total_admin_reward} unilevel reward points",
                )
                await RewardDistributionRepository.create_admin_reward_distribution_history(db, admin_reward_history_entry)

            await db.commit()
            return {"message": "Unilevel rewards distributed successfully"}

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"Error in unilevel distribution: {str(e)}")

        
    @staticmethod
    async def distribute_unilevel_rewards2_working(db: AsyncSession, user_id: str, reward_pool: float):
        try:
            from decimal import Decimal  # Ensure Decimal precision
            
            # Define unilevel reward distribution
            unilevel_distribution = {
                "Level 1": Decimal(reward_pool) * Decimal('0.06') * Decimal('0.8'),
                "Level 2": Decimal(reward_pool) * Decimal('0.05') * Decimal('0.8'),
                "Level 3": Decimal(reward_pool) * Decimal('0.04') * Decimal('0.8'),
                "Level 4": Decimal(reward_pool) * Decimal('0.03') * Decimal('0.8'),
                "Level 5": Decimal(reward_pool) * Decimal('0.02') * Decimal('0.8'),
            }

            GOSEND_ADMIN = config("ADMIN_STAGING")  # Fallback if no referrer exists
            current_user = user_id

            referrer_rewards = {}  # Store rewards per referrer
            
            for level, reward in unilevel_distribution.items():
                referrer = await ReferralRepository.get_referral(db, current_user)  # Get referrer
                
                if not referrer:  # If no referrer, send reward to GOSEND_ADMIN
                    referrer = GOSEND_ADMIN
                
                # Fetch referrer’s current reward points
                referrer_reward_points = await UserRepository.get_user_reward_points(db, referrer)
                
                # Update reward points
                updated_reward_points = referrer_reward_points + reward
                await UserRepository.update_user_reward_points(db, referrer, updated_reward_points)
                
                # Store reward history
                reward_history_data = RewardInput(
                    id=str(uuid4()),
                    reference_id=user_id,  # Transaction reference
                    reward_source_type="Unilevel Reward",
                    reward_points=reward,
                    reward_from=user_id,
                    receiver=referrer,
                    reward_type=f"{level} Unilevel Reward",
                    description=f"{level} Unilevel reward of {reward} points credited to {referrer}",
                )
                await RewardDistributionRepository.create_reward_distribution_history(db, reward_history_data)

                # Move to the next referrer (if any)
                current_user = referrer

            await db.commit()  # Commit changes
            return {"message": "Unilevel rewards distributed successfully"}

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"Error in unilevel distribution: {str(e)}")



    @staticmethod
    async def distribute_activation_unilevel_rewards(db: AsyncSession, user_id: str, reference_id: str):
        try:
            from decimal import Decimal  # Ensure Decimal precision

            unilevel_distribution = {
                "Level 1": 40,
                "Level 2": 10,
                "Level 3": 5
            }

            GOSEND_ADMIN = config("ADMIN_STAGING")
            current_user = user_id
            total_admin_reward = Decimal("0")  # Track admin's unilevel rewards separately

            for level, reward in unilevel_distribution.items():
                referrer = await ReferralRepository.get_referral(db, current_user)  # Get referrer

                if not referrer:  
                    total_admin_reward += reward  # Track reward for admin
                    continue  # Skip updating a missing referrer

                # Fetch referrer's current reward points
                await UserRepository.get_user_reward_points(db, referrer)

                # Update referrer's reward points
                updated_reward_points = reward
                await UserRepository.update_user_reward_points(db, referrer, updated_reward_points)

                # Store reward history
                reward_history_data = RewardInput(
                    id=str(uuid4()),
                    reference_id=reference_id,
                    reward_source_type="Unilevel Reward",
                    reward_points=reward,
                    reward_from=user_id,
                    receiver=referrer,
                    reward_type=f"{level} Unilevel Reward",
                    description=f"{level} Unilevel reward of {reward} points credited to {referrer}",
                )
                await RewardDistributionRepository.create_reward_distribution_history(db, reward_history_data)
                #await RewardDistributionRepository.create_admin_reward_distribution_history(db, reward_history_data)

                current_user = referrer  # Move to next referrer

            # 🔹 Update admin reward once after the loop
            if total_admin_reward > 0:
                admin_reward_points = await UserRepository.get_user_reward_points(db, GOSEND_ADMIN)
                print("Unilevel admin reward pointsss:", admin_reward_points)
                updated_admin_points = total_admin_reward
                print("Unilevel updated admin reward pointsss:", updated_admin_points)
                await UserRepository.update_user_reward_points(db, GOSEND_ADMIN, updated_admin_points)

                # Store admin reward history
                admin_reward_history = RewardInput(
                    id=str(uuid4()),
                    reference_id=reference_id,
                    reward_source_type="Unilevel Reward",
                    reward_points=total_admin_reward,
                    reward_from=user_id,
                    receiver=GOSEND_ADMIN,
                    reward_type="Unilevel Admin Reward",
                    description=f"Admin received {total_admin_reward} unilevel reward points",
                )
                await RewardDistributionRepository.create_reward_distribution_history(db, admin_reward_history)
                
                # Store admin reward history
                admin_reward_history_entry = RewardInput(
                    id=str(uuid4()),  # Ensure a new UUID
                    reference_id=reference_id,
                    reward_source_type="Unilevel Reward",
                    reward_points=total_admin_reward,
                    reward_from=user_id,
                    receiver=GOSEND_ADMIN,
                    reward_type="Unilevel Admin Reward",
                    description=f"Admin received {total_admin_reward} unilevel reward points",
                )
                await RewardDistributionRepository.create_admin_reward_distribution_history(db, admin_reward_history_entry)

            await db.commit()
            return {"message": "Unilevel rewards distributed successfully"}

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"Error in unilevel distribution: {str(e)}")



