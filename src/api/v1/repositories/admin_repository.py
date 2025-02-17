from sqlalchemy.ext.asyncio import AsyncSession



from sqlalchemy.future import select


from models.user_model import User, UserWallet
from models.wallet_model import Wallet


from sqlalchemy import update
from fastapi import HTTPException
from decouple import config


class AdminRepository:
    @staticmethod
    async def get_admin_reward_points(db: AsyncSession, user_id: str):
        try:
            # Query to retrieve the reward points of the user from the Wallet table
            result = await db.execute(
                select(
                    Wallet.reward_points  # Select reward_points from Wallet
                )
                .join(UserWallet, UserWallet.wallet_id == Wallet.wallet_id)  # Join UserWallet to Wallet
                .join(User, User.user_id == UserWallet.user_id)  # Join User to UserWallet to get user details
                .where(User.user_id == user_id)
            )

            # Retrieve the reward points of the user
            reward_points = result.scalar_one_or_none()

            return reward_points if reward_points is not None else 0  # Return 0 if no reward points are found

        except Exception as e:
            raise e

    @staticmethod
    async def update_admin_reward_points(db: AsyncSession, user_id: str, new_reward_points: float):
        try:
            # Fetch wallet ID for user
            result = await db.execute(
                select(UserWallet.wallet_id)
                .where(UserWallet.user_id == user_id)
            )

            print("User ID Wallet why hub againnn:", user_id)

            wallet_id = result.scalar_one_or_none()

            print("Get User wallet ID in updating reward points:", wallet_id)

            if not wallet_id:
                raise HTTPException(status_code=404, detail="Wallet not found for the user")

            # **Fix: Get current reward points first**
            result = await db.execute(
                select(Wallet.reward_points)
                .where(Wallet.wallet_id == wallet_id)
            )
            current_reward_points = result.scalar_one_or_none() or 0  # Default to 0 if None

            # **Fix: Add instead of overwrite**
            stmt = (
                update(Wallet)
                .where(Wallet.wallet_id == wallet_id)
                .values(reward_points=current_reward_points + new_reward_points)  # ✅ Accumulate
            )

            await db.execute(stmt)
            await db.commit()

            return {"message": "User reward points updated successfully",
                    "reward_points": current_reward_points + new_reward_points,  # ✅ Return updated total
                    "user_id": user_id}

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error updating user reward points: {str(e)}")

    @staticmethod
    async def update_admin_reward_points2(db: AsyncSession, user_id: str, new_reward_points: float):
        try:
            
            # Fetch wallet ID for user
            result = await db.execute(
                select(UserWallet.wallet_id)
                .where(UserWallet.user_id == user_id)
            )

            print("User ID Wallet why hub againnn:", user_id)

            wallet_id = result.scalar_one_or_none()

            print("Get User wallet ID in updating reward points:", wallet_id)
            
            if not wallet_id:
                raise HTTPException(status_code=404, detail="Wallet not found for the user")

            # Update reward points
            stmt = (
                update(Wallet)
                .where(Wallet.wallet_id == wallet_id)
                .values(reward_points=new_reward_points)
                )
            
            await db.execute(stmt)
            await db.commit()

            return {"message": "User reward points updated successfully",
                    "reward_points": new_reward_points,
                    "user_id": user_id}
        
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error updating user reward points: {str(e)}")
        