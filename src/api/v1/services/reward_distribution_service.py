from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from decimal import Decimal
from api.v1.services.user_service import UserService
from fastapi import HTTPException  

from decouple import config
from api.v1.repositories.community_repository import CommunityRepository
from api.v1.repositories.hub_repository import HubRepository
from api.v1.repositories.investor_repository import InvestorRepository
from api.v1.services.unilevel_services import UnilevelService
from api.v1.repositories.user_repository import UserRepository
from api.v1.repositories.merchant_repository import MerchantRepository

from api.v1.repositories.reward_distribution_repository import RewardDistributionRepository
from api.v1.schemas.reward_schema import RewardInput
from api.v1.repositories.admin_repository import AdminRepository
from api.v1.services.unilevel_services import UnilevelService

class RewardService:
    @staticmethod
    async def save_reward_history(db: AsyncSession, reward_from: str, reward_to: str, reward_points: float, reference_id: str = None):
        try:
            if not reference_id:
                reference_id = str(uuid.uuid4())  # Generate a unique reference ID if not provided

            # Create a new reward history record
            '''
            reward_history = RewardHistory(
                id=str(uuid.uuid4()),
                reference_id=reference_id,
                reward_from=reward_from,
                receiver=reward_to,
                reward_points=reward_points,
            )
            '''

            # Add to the database session and commit
            #db.add(reward_history)
            await db.commit()
            #return reward_history

        except Exception as e:
            await db.rollback()  # Rollback in case of error
            raise e

    @staticmethod
    async def distribute_rewards2(db: AsyncSession, user_id: str, reward_points: float):
        try:
            # Fetch the user's referral levels (1st to 5th)
            referral_levels = await UserService.get_user_unilevel_5(db, user_id)

            # Loop through the levels 1 to 5
            reward_from = user_id  # The user giving the reward, can be admin or hub depending on context

            # Distribute rewards to each level (1st to 5th)
            for level, level_info in referral_levels.items():
                receiver = level_info["user_id"]
                if receiver == config("GOSEND_ADMIN"):
                    continue  # Skip GOSEND_ADMIN, as no rewards are given to admin

                reference_id = str(uuid.uuid4())  # Generate unique reference ID for each reward transaction
                await RewardService.save_reward_history(
                    db,
                    reward_from,  # Reward is coming from the user (or admin)
                    receiver,  # The user at the referral level
                    reward_points,
                    reference_id
                )

            # Reward the Hub, Investor, and Community directly
            # For Hub
            hub_id = await UserService.get_user_hub_id(db, user_id)  # Get Hub ID for the user (or specific logic for hub)
            if hub_id:
                reference_id = str(uuid.uuid4())  # Unique reference ID
                await RewardService.save_reward_history(
                    db,
                    reward_from,  # The source of the reward (Admin or Hub)
                    hub_id,  # Hub is the receiver
                    reward_points,
                    reference_id
                )

            # For Investor
            investor_id = await UserService.get_user_investor_id(db, user_id)  # Get Investor ID for the user (or specific logic for investor)
            if investor_id:
                reference_id = str(uuid.uuid4())  # Unique reference ID
                await RewardService.save_reward_history(
                    db,
                    reward_from,  # The source of the reward (Admin or Investor)
                    investor_id,  # Investor is the receiver
                    reward_points,
                    reference_id
                )

            # For Community
            community_id = await UserService.get_user_community_id(db, user_id)  # Get Community ID for the user (or specific logic for community)
            if community_id:
                reference_id = str(uuid.uuid4())  # Unique reference ID
                await RewardService.save_reward_history(
                    db,
                    reward_from,  # The source of the reward (Admin or Community)
                    community_id,  # Community is the receiver
                    reward_points,
                    reference_id
                )

            # For Admin (if the reward is from admin)
            admin_id = config("GOSEND_ADMIN")  # Admin user ID
            reference_id = str(uuid.uuid4())  # Unique reference ID
            await RewardService.save_reward_history(
                db,
                reward_from,  # Admin is the source of the reward
                admin_id,  # Admin is the receiver
                reward_points,
                reference_id
            )

            return {"status": "success", "message": "Rewards distributed successfully."}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error distributing rewards: {str(e)}")



# Assuming you already have a repository for updating the wallets and logging transactions
    @staticmethod
    async def distribute_rewards(db: AsyncSession, admin_amount: float, user_id: str, hub_id: str, investor_id: str):
        try:
            # Fetch Unilevel rewards
            unilevel_rewards = await UnilevelService.get_user_unilevel_5(db, user_id)

            # Fetch community, hub, and investor rewards
            community_reward = await CommunityRepository.get_community_leader_reward_points(db, user_id)
            hub_reward = await HubRepository.get_hub_user_reward_points(db, hub_id)
            investor_reward = await InvestorRepository.get_investor_user_reward_points(db, investor_id)
            merchant_referrer_reward = await MerchantRepository.get_merchant_referrer_reward_points(db, user_id)
            user_reward = await UserRepository.get_user_reward_points(db, user_id)

            

            # Calculate reward pool distribution
            reward_pool = admin_amount  # The reward pool is the admin_amount

            # Define the distribution percentages (these values can be changed as needed)
            distribution = {
                "Hub": reward_pool * 0.05,  # 5% for Hub
                "Community": reward_pool * 0.05,  # 5% for Community
                "Merchant": reward_pool * 0.1,  # 10% for Merchant
                "User": reward_pool * 0.1,  # 10% for User
                "Referrer of Merchant": reward_pool * 0.15,  # 15% for Referrer of Merchant
                "Investor": reward_pool * 0.05,  # 5% for Investor
                "Unilevel Referral": {
                    "Level 1": reward_pool * 0.06 * 0.8,  # 6% for Level 1, adjusted by 80%
                    "Level 2": reward_pool * 0.05 * 0.8,  # 5% for Level 2, adjusted by 80%
                    "Level 3": reward_pool * 0.04 * 0.8,  # 4% for Level 3, adjusted by 80%
                    "Level 4": reward_pool * 0.03 * 0.8,  # 3% for Level 4, adjusted by 80%
                    "Level 5": reward_pool * 0.02 * 0.8,  # 2% for Level 5, adjusted by 80%
                },
                "Unilevel Remainder to MotherWallet": reward_pool * 0.04,  # 4% remainder goes to Mother Wallet

                "Admin (Mother Wallet)": admin_amount * 0.3,  # 30% of the reward pool for Admin allocation
            }

            # Create a dictionary to hold all user updates
            user_updates = {
                "Hub": hub_reward + distribution["Hub"],
                "Community": community_reward + distribution["Community"],
                "Merchant": distribution["Merchant"],  
                "User": user_reward +distribution["User"],  
                "Referrer of Merchant": merchant_referrer_reward + distribution["Referrer of Merchant"],
                "Investor": investor_reward + distribution["Investor"],
                "Admin (Mother Wallet)": distribution["Admin (Mother Wallet)"] + distribution["Unilevel Remainder to MotherWallet"],
            }

            # Loop through user_updates to create individual records for each user
            for user_type, reward_amount in user_updates.items():
                # You can customize receiver based on user_type and use a specific user ID if needed
                receiver = user_type  # For now, using the user_type as the receiver
                
                # Create individual reward history entry for each user
                """
                await RewardHistoryRepository.create_reward_history(
                    db,
                    reward_points=reward_amount,
                    reference_id=str(uuid4()),  # Unique reference for each transaction
                    reward_from="Purchase",  # Adjust as needed
                    receiver=receiver,  # Receiver will be the type of user (Hub, Community, etc.)
                )

            # If you want to handle the Unilevel rewards separately, you can include them here too
            for level, reward_amount in distribution["Unilevel Referral"].items():
                # Handle reward distribution for each level
                level_receiver = unilevel_rewards.get(level)  # Retrieve the user for each level
                
                if level_receiver:
                    await RewardHistoryRepository.create_reward_history(
                        db,
                        reward_points=reward_amount,
                        reference_id=str(uuid4()),  # Unique reference for each transaction
                        reward_from="Unilevel",  # Adjust as needed
                        receiver=level_receiver["user_id"],  # Receiver is the user from each level
                    )
                """
            return {"status": "success", "message": "Rewards distributed successfully."}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error distributing rewards: {str(e)}")


    @staticmethod
    async def distribute_rewards_main2(db: AsyncSession, admin_amount: float, user_id: str, hub_id: str, investor_id: str, merchant_id: str):
        try:
            # Fetch Unilevel rewards
            unilevel_rewards = await UnilevelService.get_user_unilevel_5(db, user_id)

            # Fetch community, hub, and investor rewards
            community_reward = await CommunityRepository.get_community_leader_reward_points(db, user_id)
            hub_reward = await HubRepository.get_hub_user_reward_points(db, hub_id)
            investor_reward = await InvestorRepository.get_investor_user_reward_points(db, investor_id)
            merchant_referrer_reward = await MerchantRepository.get_merchant_referrer_reward_points(db, user_id)
            user_reward = await UserRepository.get_user_reward_points(db, user_id)
            merchant_reward = await MerchantRepository.get_merchant_reward_points(db, merchant_id)

            # Calculate reward pool distribution
            reward_pool = admin_amount  # The reward pool is the admin_amount

            # Define the distribution percentages (these values can be changed as needed)
            distribution = {
                "Hub": reward_pool * 0.05,  # 5% for Hub
                "Community": reward_pool * 0.05,  # 5% for Community
                "Merchant": reward_pool * 0.1,  # 10% for Merchant
                "User": reward_pool * 0.1,  # 10% for User
                "Referrer of Merchant": reward_pool * 0.15,  # 15% for Referrer of Merchant
                "Investor": reward_pool * 0.05,  # 5% for Investor
                "Unilevel Referral": {
                    "Level 1": reward_pool * 0.06 * 0.8,  # 6% for Level 1, adjusted by 80%
                    "Level 2": reward_pool * 0.05 * 0.8,  # 5% for Level 2, adjusted by 80%
                    "Level 3": reward_pool * 0.04 * 0.8,  # 4% for Level 3, adjusted by 80%
                    "Level 4": reward_pool * 0.03 * 0.8,  # 3% for Level 4, adjusted by 80%
                    "Level 5": reward_pool * 0.02 * 0.8,  # 2% for Level 5, adjusted by 80%
                },
                "Unilevel Remainder to MotherWallet": reward_pool * 0.04,  # 4% remainder goes to Mother Wallet
                "Admin (Mother Wallet)": admin_amount * 0.3,  # 30% of the reward pool for Admin allocation
            }

            # Create a dictionary to hold all user updates
            user_updates = {
                "Hub": hub_reward + distribution["Hub"],
                "Community": community_reward + distribution["Community"],
                "Merchant": merchant_reward +distribution["Merchant"],  
                "User": user_reward + distribution["User"],  
                "Referrer of Merchant": merchant_referrer_reward + distribution["Referrer of Merchant"],
                "Investor": investor_reward + distribution["Investor"],
                "Admin (Mother Wallet)": distribution["Admin (Mother Wallet)"] + distribution["Unilevel Remainder to MotherWallet"],
            }


        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error distributing rewards: {str(e)}")


    @staticmethod
    async def distribute_rewards_main(db: AsyncSession, admin_amount: float, user_id: str, hub_id: str, investor_id: str, merchant_id: str, reference_id: str):
        try:
            # Fetch Unilevel rewards
           # unilevel_rewards = await UnilevelService.get_user_unilevel_5(db, user_id)
            #community_id = '595f9815-2f79-4ebd-a4c7-8e33050f882e'

            user_community_id = await UserRepository.get_user_communty(db, user_id)
            print(f"UserID: {user_id}")

            community_id = user_community_id.community_id
        
            # Fetch community, hub, and investor rewards
            community_reward = await CommunityRepository.get_community_leader_reward_points(db, community_id)
            hub_reward = await HubRepository.get_hub_user_reward_points(db, hub_id)
            investor_reward = await InvestorRepository.get_investor_user_reward_points(db, investor_id)
            merchant_referrer_reward = await MerchantRepository.get_merchant_referrer_reward_points(db, merchant_id)
            user_reward = await UserRepository.get_user_reward_points(db, user_id)
            merchant_direct_referrer_reward = await MerchantRepository.get_merchant_direct_referrer_reward_points(db, merchant_id)
            print(f"Merchant direct referrer reward: {merchant_direct_referrer_reward}")
            #merchant_reward = await MerchantRepository.get_merchant_reward_points(db, merchant_id)

            print(f"Community reward: {community_reward}")
            print(f"Hub reward: {hub_reward}")
            print(f"Investor reward: {investor_reward}")
            print(f"Merchant referrer reward: {merchant_referrer_reward}")
            print(f"User reward: {user_reward}")
            print(f"Merchant direct referrerreward: {merchant_direct_referrer_reward}")
            print(f"Admin reward: {admin_amount}")

            #admin_id = "6e9d7f0e-7808-4042-aebd-ddb46e5c1ce1"
            admin_id = config("ADMIN_STAGING")
            admin_reward = await AdminRepository.get_admin_reward_points(db, admin_id)  # Admin's reward points

            




            # Calculate reward pool distribution
            reward_pool = admin_amount  # The reward pool is the admin_amount
            print(f"Reward Pooool: {reward_pool}")


            # 15% direct referrer of user ( first level )
            # 10% referrer of merchant

            distribution = {
                "Hub": Decimal(reward_pool) * Decimal('0.05'), 
                "Community": Decimal(reward_pool) * Decimal('0.05'),

                # first level of merchant owner
                "Merchant Direct Referrer": Decimal(reward_pool) * Decimal('0.15'), # direct referrer of user ( first level )
                "User": Decimal(reward_pool) * Decimal('0.1'), # personal rebate
                "Referrer of Merchant": Decimal(reward_pool) * Decimal('0.1'), # referrer of the merchant
                "Investor": Decimal(reward_pool) * Decimal('0.05'),
                "Unilevel Referral": {
                    "Level 1": Decimal(reward_pool) * Decimal('0.06') * Decimal('0.8'),
                    "Level 2": Decimal(reward_pool) * Decimal('0.05') * Decimal('0.8'),
                    "Level 3": Decimal(reward_pool) * Decimal('0.04') * Decimal('0.8'),
                    "Level 4": Decimal(reward_pool) * Decimal('0.03') * Decimal('0.8'),
                    "Level 5": Decimal(reward_pool) * Decimal('0.02') * Decimal('0.8'),
                },
                "Unilevel Remainder to MotherWallet": Decimal(reward_pool) * Decimal('0.04'),
                # change admin_amount to reward_pool
                "Admin (Mother Wallet)": Decimal(reward_pool) * Decimal('0.3'),
            }

            print(f"Distribution: {distribution}")

            user_updates = {
                "Hub": hub_reward + distribution["Hub"],
                "Community": community_reward + distribution["Community"],
                "Merchant Direct Referrer": merchant_direct_referrer_reward + distribution["Merchant Direct Referrer"],
                "User": user_reward + distribution["User"],
                "Referrer of Merchant": merchant_referrer_reward + distribution["Referrer of Merchant"],
                "Investor": investor_reward + distribution["Investor"],
                "Admin (Mother Wallet)": admin_reward + distribution["Admin (Mother Wallet)"],
                "Unilevel Remainder to MotherWallet": admin_reward + distribution["Unilevel Remainder to MotherWallet"],
                #"Admin (Mother Wallet)": admin_reward + distribution["Admin (Mother Wallet)"] + distribution["Unilevel Remainder to MotherWallet"],
            }

            print(f"User Updates: {user_updates}")

            '''
            # ✅ Save reward history after updating reward points
            reward_history_data = RewardInput(
                id = str(uuid.uuid4()),
                reference_id = reference_id,  # Use hub_id as reference
                reward_source_type = "Merchant Purchase Distribution",
                reward_points = distribution["Hub"],
                reward_from = merchant_id,  # Who gave the reward
                receiver = hub_new_points.get("user_id"),  # Who received it
                reward_type = "Hub Reward",
                description = f"Hub received {user_updates['Hub']} reward points"
            )

            await RewardDistributionRepository.create_reward_distribution_history(db, reward_history_data)
            '''

            '''
            # Update reward points in the database
            hub_new_points = await HubRepository.update_hub_user_reward_points(db, hub_id, user_updates["Hub"])
            # get community ID instead of user ID
            community_leader_new_points = await CommunityRepository.update_community_leader_reward_points(db, community_id, user_updates["Community"])
            merchant_new_points = await MerchantRepository.update_merchant_direct_referrer_reward_points(db, merchant_id, user_updates["Merchant Direct Referrer"])
            print(f"Merchant new reward pointsss: {merchant_new_points.get('reward_points')}")
            user_new_points = await UserRepository.update_user_reward_points(db, user_id, user_updates["User"])
            merchant_referrer_new_points = await MerchantRepository.update_merchant_referrer_reward_points(db, merchant_id, user_updates["Referrer of Merchant"])
            investor_new_points = await InvestorRepository.update_investor_user_reward_points(db, investor_id, user_updates["Investor"])
    

            print("Hub new reward pointss: ", hub_new_points.get("reward_points"))
            print("Community Leader new reward points: ", community_leader_new_points.get("reward_points"))
            print("Merchant Direct Referrer new reward points: ", merchant_new_points.get("reward_points"))
            print(f"User new reward points: {user_new_points.get('reward_points')}")
            print("Merchant Referrer new reward points: ", merchant_referrer_new_points.get("reward_points"))
            print("Investor new reward points: ", investor_new_points.get("reward_points"))
            '''


            # List of reward categories and their repository functions
            # Execute update functions sequentially and store the results
            updated_rewards = {}

            updated_rewards["Hub"] = await HubRepository.update_hub_user_reward_points(db, hub_id, distribution["Hub"])
            updated_rewards["Community"] = await CommunityRepository.update_community_leader_reward_points(db, community_id, distribution["Community"])
            updated_rewards["Merchant Direct Referrer"] = await MerchantRepository.update_merchant_direct_referrer_reward_points(db, merchant_id, distribution["Merchant Direct Referrer"])
            updated_rewards["User"] = await UserRepository.update_user_reward_points(db, user_id, distribution["User"])
            updated_rewards["Referrer of Merchant"] = await MerchantRepository.update_merchant_referrer_reward_points(db, merchant_id, distribution["Referrer of Merchant"])
            updated_rewards["Investor"] = await InvestorRepository.update_investor_user_reward_points(db, investor_id, distribution["Investor"])

            admin_updated_rewards = await AdminRepository.update_admin_reward_points(db, admin_id, distribution["Admin (Mother Wallet)"])
            admin_unilevel_updated_rewards = await AdminRepository.update_admin_reward_points(db, admin_id, distribution["Unilevel Remainder to MotherWallet"])



            print(f"Hub new reward pointss: {updated_rewards['Hub'].get('reward_points')}")
            print(f"Community Leader new reward points: {updated_rewards['Community'].get('reward_points')}")
            print(f"Merchant Direct Referrer new reward points: {updated_rewards['Merchant Direct Referrer'].get('reward_points')}")
            print(f"User new reward points: {updated_rewards['User'].get('reward_points')}")
            print(f"Merchant Referrer new reward points: {updated_rewards['Referrer of Merchant'].get('reward_points')}")
            print(f"Investor new reward points: {updated_rewards['Investor'].get('reward_points')}")
            print(f"Admin new reward points: {admin_updated_rewards.get('reward_points')}")
            print(f"Admin Unilevel new reward points: {admin_unilevel_updated_rewards.get('reward_points')}")

            # ✅ Save reward history for each reward target using distribution points
            for key, reward_data in updated_rewards.items():
                if reward_data:  # Ensure reward data exists
                    reward_history_data = RewardInput(
                        id=str(uuid.uuid4()),
                        reference_id=reference_id,
                        reward_source_type="Merchant Purchase Distribution",
                        reward_points=distribution[key],  # 🔥 Use points from `distribution`, not `user_updates`
                        reward_from=merchant_id,
                        receiver=reward_data.get("user_id"),  # Extract user_id from the result
                        reward_type=f"{key} Reward",
                        description=f"{key} received {distribution[key]} reward points"  # 🔥 Use `distribution[key]`
                    )

                    await RewardDistributionRepository.create_reward_distribution_history(db, reward_history_data)



            reward_history_data = RewardInput(
                id = str(uuid.uuid4()),
                reference_id = reference_id,
                reward_source_type = "Merchant Purchase Distribution",
                reward_points = distribution['Admin (Mother Wallet)'], 
                reward_from = merchant_id,
                receiver = admin_updated_rewards.get("user_id"),  # Extract user_id from the result
                reward_type = f"Admin (Mother Wallet)",
                description = f"Admin received {distribution['Admin (Mother Wallet)']} reward points"  # 🔥 Use `distribution[key]`
            )

            await RewardDistributionRepository.create_reward_distribution_history(db, reward_history_data)
            await RewardDistributionRepository.create_admin_reward_distribution_history(db, reward_history_data)


            reward_history_data = RewardInput(
                id=str(uuid.uuid4()),
                reference_id=reference_id,
                reward_source_type="Merchant Purchase Distribution",
                reward_points= distribution['Unilevel Remainder to MotherWallet'],  # 🔥 Use points from `distribution`, not `user_updates`
                reward_from=merchant_id,
                receiver=admin_unilevel_updated_rewards.get("user_id"),  # Extract user_id from the result
                reward_type=f"Unilevel Remainder to MotherWallet",
                description=f"Admin received {distribution['Unilevel Remainder to MotherWallet']} reward points"  # 🔥 Use `distribution[key]`
            )

            await RewardDistributionRepository.create_reward_distribution_history(db, reward_history_data)
            await RewardDistributionRepository.create_admin_reward_distribution_history(db, reward_history_data)

            await UnilevelService.distribute_unilevel_rewards(db, user_id, reward_pool, reference_id)

            # Handle unilevel rewards, ensuring rewards go to Admin if a level is missing
            '''
            for level, reward in distribution["Unilevel Referral"].items():
                level_data = unilevel_rewards[level.lower()] 
                level_user_id = level_data["user_id"]

                if level_user_id == config("GOSEND_ADMIN"):  # If no referral exists, add to Admin
                    user_updates["Admin (Mother Wallet)"] += reward
                else:
                    if level_user_id not in user_updates:
                        user_updates[level_user_id] = 0  # Ensure the user exists in updates
                    user_updates[level_user_id] += reward  # Add reward points
            '''




            # Create reward history for tracking

            await db.commit()
            #await db.refresh(user_updates)

            return {"message": "Rewards distributed successfully"}

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"Error distributing rewards: {str(e)}")


