from sqlalchemy.ext.asyncio import AsyncSession

from models.hub_model import Hub

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload

from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from api.v1.schemas.hub_schema import HubCreate, HubResponse



from models.user_model import User, UserWallet
from models.wallet_model import Wallet

from sqlalchemy import update


class HubRepository:
    
    @staticmethod
    async def is_hub_name_exists(db: AsyncSession, hub_name: str) -> bool:
        result = await db.execute(
            select(Hub).where(
                Hub.hub_name == hub_name
            )
        )

        return result.scalar() is not None
    
    @staticmethod
    async def is_hub_user_exists(db: AsyncSession, hub_user: str) -> bool:
        result = await db.execute(
            select(Hub).where(
                Hub.hub_user == hub_user
            )
        )

        return result.scalar() is not None
    
    @staticmethod
    async def update_hub_role(db: AsyncSession, hub_user: str):
        try:
            result = await db.execute(
                select(User).where(User.mobile_number == hub_user)
            )

            hub = result.scalar()

            if not hub:
                raise HTTPException(status_code=404, detail="Hub not found")

            if hub.account_type != "MEMBER":
                raise HTTPException(status_code=400, detail="User is already assigned to another role")
            
            hub.account_type = "HUB"
            
            await db.commit()
            await db.refresh(hub)

            return True

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))


    @staticmethod
    async def create_hub(db: AsyncSession, hub_data: HubCreate):
        try:
            if await HubRepository.is_hub_name_exists(db, hub_data['hub_name']):
                raise HTTPException(status_code=400, detail="Hub name already exists")
            
            if await HubRepository.is_hub_user_exists(db, hub_data['hub_user']):
                raise HTTPException(status_code=400, detail="User already assigned to another Hub")
            
            if not await HubRepository.update_hub_role(db, hub_data['hub_user']):
                raise HTTPException(status_code=400, detail="User role update failed")
            
            hub = Hub(
                **hub_data
            )

            db.add(hub)
            await db.commit()
            await db.refresh(hub)

            return hub
        

        except IntegrityError as e:
            await db.rollback()
            if "Unique constraint failed" in str(e):
                raise HTTPException(status_code=400, detail="Hub already exists")
            
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        



    @staticmethod
    async def get_hub_user_reward_points(db: AsyncSession, hub_id: str):
        result = await db.execute(
            select(Wallet.reward_points)
            .join(UserWallet, Wallet.wallet_id == UserWallet.wallet_id)
            .join(User, User.user_id == UserWallet.user_id)
            .join(Hub, Hub.hub_user == User.mobile_number)  # Match the hub's user
            .filter(Hub.hub_id == hub_id)
        )
        reward_points = result.scalar()
        return reward_points


    @staticmethod
    async def update_hub_user_reward_points(db: AsyncSession, hub_id: str, new_reward_points: float):
        try:
            # First, retrieve the wallet_id of the hub user
            result = await db.execute(
                select(User.user_id)
                .join(Hub, Hub.hub_user == User.mobile_number)  # Join Hub with User to get the hub user
                .where(Hub.hub_id == hub_id)
            )

            hub_user_id = result.scalar_one_or_none()

            if not hub_user_id:
                raise HTTPException(status_code=404, detail="Hub user not found")

            # Retrieve the wallet ID of the hub user
            result_wallet = await db.execute(
                select(UserWallet.wallet_id)
                .where(UserWallet.user_id == hub_user_id)
            )

            wallet_id = result_wallet.scalar_one_or_none()

            if not wallet_id:
                raise HTTPException(status_code=404, detail="Wallet not found for the hub user")

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
                .values(reward_points = current_reward_points + new_reward_points)  # ✅ Accumulate
            )

            # Execute the update statement
            await db.execute(stmt)
            await db.commit()

            return {"message": "Hub new reward points updated successfully",
                    "reward_points": current_reward_points + new_reward_points,  # ✅ Return updated total
                    "user_id": hub_user_id
                    }

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error updating hub user reward points: {str(e)}")

        
    @staticmethod
    async def update_hub_user_reward_points2(db: AsyncSession, hub_id: str, new_reward_points: float):
        try:
            # First, retrieve the wallet_id of the hub user
            result = await db.execute(
                select(User.user_id)
                .join(Hub, Hub.hub_user == User.mobile_number)  # Join Hub with User to get the hub user
                .where(Hub.hub_id == hub_id)
            )

            hub_user_id = result.scalar_one_or_none()

            if not hub_user_id:
                raise HTTPException(status_code=404, detail="Hub user not found")

            # Retrieve the wallet ID of the hub user
            result_wallet = await db.execute(
                select(UserWallet.wallet_id)
                .where(UserWallet.user_id == hub_user_id)
            )

            wallet_id = result_wallet.scalar_one_or_none()

            if not wallet_id:
                raise HTTPException(status_code=404, detail="Wallet not found for the hub user")

            # Update the reward_points in the Wallet table
            stmt = (
                update(Wallet)
                .where(Wallet.wallet_id == wallet_id)
                .values(reward_points=new_reward_points)
            )



            # Execute the update statement
            await db.execute(stmt)
            await db.commit()

            return {"message": "Hub new reward points updated successfully",
                    "reward_points": new_reward_points,
                    "user_id": hub_user_id
                    }

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error updating hub user reward points: {str(e)}")
        
