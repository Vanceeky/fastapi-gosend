from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload


from models.investor_model import Investor

from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from api.v1.schemas.investor_schema import InvestorCreate

from uuid import uuid4 

from models.user_model import User, UserWallet
from models.wallet_model import Wallet
from sqlalchemy import update


class InvestorRepository2:
    @staticmethod
    async def is_user_already_investor(db: AsyncSession, investor_user: str):
        try:
            # Check if the user already exists as an investor
            result = await db.execute(select(Investor).filter_by(investor_user=investor_user))
            investor = result.scalars().first()
            return investor is not None
        except Exception as e:
            # Handle database-related errors
            raise HTTPException(status_code=500, detail=f"Error checking if user exists: {str(e)}")

    @staticmethod
    async def update_investor_role(db: AsyncSession, investor_user: str):
        try:
            # Logic to update user role
            user = await db.execute(select(User).filter_by(mobile_number=investor_user))
            user = user.scalars().first()
            if user:
                user.role = "Investor"  # Assuming the role needs to be updated
                await db.commit()
                return True
            return False
        except Exception as e:
            # Handle database-related errors
            raise HTTPException(status_code=500, detail=f"Error updating user role: {str(e)}")

    @staticmethod
    async def create_investor(db: AsyncSession, investor_data: dict):
        try:
            # Create the investor object in the repository
            investor_data['investor_id'] = str(uuid4())  # Ensure a unique ID for the investor
            investor = Investor(**investor_data)
            db.add(investor)
            return investor
        except Exception as e:
            # Handle any error during the creation of the investor
            raise HTTPException(status_code=500, detail=f"Error creating investor: {str(e)}")
        

class InvestorRepository:

    @staticmethod
    async def is_user_already_investor(db: AsyncSession, investor_user: str) -> bool:
        result = await db.execute(
            select(Investor).where(Investor.investor_user == investor_user)
        )
        return result.scalar() is not None

    @staticmethod
    async def update_investor_role(db: AsyncSession, investor_mobile_number: str):
        try:
            result = await db.execute(
                select(User).where(User.mobile_number == investor_mobile_number)
            )

            investor = result.scalar()

            if not investor:
                raise HTTPException(status_code=404, detail="Investor not found")



            if investor.account_type != "MEMBER":
                raise HTTPException(status_code=400, detail="User is already assigned to another role")
            
            investor.account_type = "INVESTOR"
            
            await db.commit()
            await db.refresh(investor)

            return True

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))


    @staticmethod
    async def create_investor(db: AsyncSession, investor_data: InvestorCreate ):
        try:

            if await InvestorRepository.is_user_already_investor(db, investor_data['investor_user']):
                raise HTTPException(status_code=400, detail="User already exists as an investor")
            
            if not await InvestorRepository.update_investor_role(db, investor_data['investor_user']):
                raise HTTPException(status_code=400, detail="User role update failed")
            
            investor = Investor(**investor_data)
            db.add(investor)

            await db.commit()
            await db.refresh(investor)

            return investor



        except IntegrityError as e:
            await db.rollback()
            if "UNIQUE constraint failed" in str(e):
                raise HTTPException(status_code=400, detail="Investor already exists")
        
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
            


    @staticmethod
    async def get_investor_user_reward_points(db: AsyncSession, investor_id: str):
        result = await db.execute(
            select(Wallet.reward_points)
            .join(UserWallet, Wallet.wallet_id == UserWallet.wallet_id)
            .join(User, User.user_id == UserWallet.user_id)
            .join(Investor, Investor.investor_user == User.mobile_number)  # Match investor user
            .filter(Investor.investor_id == investor_id)
        )
        reward_points = result.scalar()
        return reward_points


    @staticmethod
    async def get_investor_user_reward_points2(db: AsyncSession, investor_id: str):
        try:
            # Query to retrieve the reward points for the investor user
            result = await db.execute(
                select(
                    Wallet.reward_points  # Select reward_points from Wallet
                )
                .join(User, User.mobile_number == Investor.investor_user)  # Join Investor with User to get the investor user
                .join(UserWallet, UserWallet.user_id == User.user_id)  # Join UserWallet to get the wallet
                .join(Wallet, Wallet.wallet_id == UserWallet.wallet_id)  # Join Wallet to get the reward_points
                .where(Investor.investor_id == investor_id)
            )

            # Retrieve the reward points for the investor user
            reward_points = result.scalar_one_or_none()

            return reward_points if reward_points is not None else 0  # Return 0 if no reward points are found

        except Exception as e:
            raise e
        

    @staticmethod
    async def update_investor_user_reward_points(db: AsyncSession, investor_id: str, new_reward_points: float):
        try:
            # Fetch investor user_id
            result = await db.execute(
                select(User.user_id)
                .join(Investor, Investor.investor_user == User.mobile_number)
                .where(Investor.investor_id == investor_id)
            )

            investor_user_id = result.scalar_one_or_none()
            if not investor_user_id:
                raise HTTPException(status_code=404, detail="Investor user not found")

            # Fetch wallet ID
            result_wallet = await db.execute(
                select(UserWallet.wallet_id)
                .where(UserWallet.user_id == investor_user_id)
            )

            wallet_id = result_wallet.scalar_one_or_none()
            if not wallet_id:
                raise HTTPException(status_code=404, detail="Wallet not found for the investor user")
            
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

            return {"message": "Investor user reward points updated successfully", "reward_points": new_reward_points, "user_id": investor_user_id}

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error updating investor user reward points: {str(e)}")