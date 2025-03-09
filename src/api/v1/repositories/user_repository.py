from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from models.user_model import User, UserAddress, UserDetail, UserWallet, UserWalletExtension
from models.wallet_model import Wallet
from sqlalchemy import delete, update
from sqlalchemy.exc import IntegrityError
from utils.responses import json_response
from fastapi import HTTPException
from models.referral_model import Referral
from typing import Optional, List
from api.v1.schemas.user_schema import UserSchema, ReferralDownlineSchema, ReferralUplineSchema
from models.community_model import Community

from sqlalchemy.sql import union_all
from fastapi.responses import JSONResponse

import logging
logging.basicConfig(level=logging.INFO)

class UserRepository:

    @staticmethod
    async def create_user(db: AsyncSession, user_data: dict, address_data: dict = None, details_data: dict = None):
        try:
            user = User(**user_data)
            db.add(user)
            await db.commit()
            await db.refresh(user)

            if address_data:
                user_address = UserAddress(user_id=user.user_id, **address_data)
                db.add(user_address)

            if details_data:
                user_detail = UserDetail(user_id=user.user_id, **details_data)
                db.add(user_detail)

            await db.commit()
            return user
        
        except IntegrityError as e:
            await db.rollback()
            return json_response(message="User already exists", status_code=400)
        
        except Exception as e:

            await db.rollback()
            raise e
        
        

    @staticmethod
    async def get_user(db: AsyncSession, user_id: str):
        """
        Fetches a user by their user_id along with related address, details, and wallets.

        Args:
            db (AsyncSession): Database session for async operations.
            user_id (str): The unique identifier of the user.

        Returns:
            User: The user object, including related data.
        """
        result = await db.execute(
            select(User)
            .filter(User.user_id == user_id)
            .options(
                selectinload(User.user_address),
                selectinload(User.user_details),
                selectinload(User.user_wallets).selectinload(UserWallet.wallets)
            )
        )
        user = result.scalars().first()
        return user

    @staticmethod
    async def get_all_users(db: AsyncSession):
        """
        Fetches all users along with their related address, details, and wallets.

        Args:
            db (AsyncSession): Database session for async operations.

        Returns:
            List[User]: A list of all user objects with related data.
        """
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.user_address),
                selectinload(User.user_details),
                selectinload(User.user_wallets).selectinload(UserWallet.wallets)
            )
        )
        users = result.scalars().all()
        return users

    @staticmethod
    async def update_user(db: AsyncSession, user_id: str, user_data: dict):
        """
        Updates a user and optionally their address and details.

        Args:
            db (AsyncSession): Database session for async operations.
            user_id (str): The unique identifier of the user.
            user_data (dict): Data to update the user.

        Returns:
            User: The updated user object, or None if the user was not found.
        """
        try:
            result = await db.execute(select(User).filter(User.user_id == user_id))
            user = result.scalars().first()
            if not user:
                return None

            for key, value in user_data.items():
                if value is not None:
                    setattr(user, key, value)

            await db.commit()

            if 'user_address' in user_data and user_data['user_address']:
                await UserRepository.update_user_address(db, user_id, user_data['user_address'])

            if 'user_details' in user_data and user_data['user_details']:
                await UserRepository.update_user_details(db, user_id, user_data['user_details'])

            return user
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def update_user_address(db: AsyncSession, user_id: str, address_data: dict):
        """
        Updates the address for a given user.

        Args:
            db (AsyncSession): Database session for async operations.
            user_id (str): The unique identifier of the user.
            address_data (dict): Data to update the user's address.

        Returns:
            UserAddress: The updated address object, or None if the address was not found.
        """
        try:
            result = await db.execute(select(UserAddress).filter(UserAddress.user_id == user_id))
            user_address = result.scalars().first()

            if not user_address:
                return None

            for key, value in address_data.items():
                if value is not None:
                    setattr(user_address, key, value)

            await db.commit()
            return user_address
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def update_user_details(db: AsyncSession, user_id: str, details_data: dict):
        """
        Updates the details for a given user.

        Args:
            db (AsyncSession): Database session for async operations.
            user_id (str): The unique identifier of the user.
            details_data (dict): Data to update the user's details.

        Returns:
            UserDetail: The updated user details object, or None if the details were not found.
        """
        try:
            result = await db.execute(select(UserDetail).filter(UserDetail.user_id == user_id))
            user_details = result.scalars().first()

            if not user_details:
                return None

            for key, value in details_data.items():
                if value is not None:
                    setattr(user_details, key, value)

            await db.commit()
            return user_details
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: str):
        """
        Deletes a user and their related records, including address, details, and wallet.

        Args:
            db (AsyncSession): Database session for async operations.
            user_id (str): The unique identifier of the user.

        Returns:
            bool: True if the user was successfully deleted, None otherwise.
        """
        try:
            user = await db.execute(
                select(User).filter(User.user_id == user_id)
            )
            user = user.scalars().one_or_none()
            if not user:
                return None
            
            wallet_ids = await db.execute(
                select(UserWallet.wallet_id).filter(UserWallet.user_id == user_id)
            )
            wallet_ids = wallet_ids.scalars().all()

            for wallet_id in wallet_ids:
                await db.execute(delete(Wallet).filter(Wallet.wallet_id == wallet_id))
            await db.commit()

            await db.execute(delete(UserWallet).filter(UserWallet.user_id == user_id))
            await db.commit()

            await db.execute(delete(UserAddress).filter(UserAddress.user_id == user_id))
            await db.commit()

            await db.execute(delete(UserDetail).filter(UserDetail.user_id == user_id))
            await db.commit()
            
            await db.execute(delete(User).filter(User.user_id == user_id))
            await db.commit()
            
            return True

        except Exception as e:
            await db.rollback()
            raise e



    @staticmethod
    async def get_user_unilevel(db: AsyncSession, user_id: str):

        try:
            results = await db.execute(
                select(User).filter(User.user_id == user_id)
            )

            user = results.scalars().first()

            user_unilevel = user.unilevel

            return user_unilevel

        except Exception as e:
            raise e
        

    @staticmethod
    async def get_user_communty(db: AsyncSession, user_id: str):
        try:
            result = await db.execute(
                select(User).where(User.user_id == user_id)
            )

            return result.scalars().first()
        
        except Exception as e:
            raise e

    @staticmethod
    async def get_user_wallet_balance(db: AsyncSession, user_id: str):
        try:
            result = await db.execute(
                select(Wallet.balance, Wallet.reward_points).join(
                    UserWallet, UserWallet.wallet_id == Wallet.wallet_id
                ).where(UserWallet.user_id == user_id)
            )

            wallet_data = result.first() 

            if wallet_data:
                balance, reward_points = wallet_data 
                return {"balance": balance, "reward_points": reward_points}

            return {"balance": 0.00, "reward_points": 0.00} 

        except Exception as e:
            raise e


    @staticmethod
    async def get_user_reward_points(db: AsyncSession, user_id: str):
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
    async def update_user_reward_points(db: AsyncSession, user_id: str, new_reward_points: float):
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
                    "reward_points": new_reward_points,
                    "user_id": user_id}
        
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error updating user reward points: {str(e)}")
        
        

    @staticmethod
    async def update_user_reward_points2(db: AsyncSession, user_id: str, new_reward_points: float):
        try:
            # Fetch wallet ID for user
            result = await db.execute(
                select(UserWallet.wallet_id).where(UserWallet.user_id == user_id)
            )

            wallet_id = result.scalar_one_or_none()
            if not wallet_id:
                raise HTTPException(status_code=404, detail="Wallet not found for the user")

            # Update reward points
            stmt = update(Wallet).where(Wallet.wallet_id == wallet_id).values(reward_points=new_reward_points)
            await db.execute(stmt)
            await db.commit()

            return {"message": "User reward points updated successfully"}

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error updating user reward points: {str(e)}")
        

    @staticmethod
    async def get_user_by_referral_id(db: AsyncSession, referral_id: str):
        try:
            # Query to retrieve the user based on referral_id
            result = await db.execute(
                select(User).filter(User.referral_id == referral_id)
            )
            
            # Get the user from the result
            user = result.scalar_one_or_none()

            # If no user is found, raise an exception
            if not user:
                raise HTTPException(status_code=404, detail=f"User with referral_id {referral_id} not found")
            
            return user
        
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error retrieving user by referral_id: {str(e)}")
        




    # ✅ Fetch Upline Hierarchy Using CTE
    @staticmethod
    async def get_upline(db: AsyncSession, user_id: str) -> Optional[ReferralUplineSchema]:
        """Fetch the upline hierarchy recursively (all uplines) using CTE."""
        try:
            # ✅ Recursive CTE Query for Uplines
            cte = (
                select(
                    Referral.referred_by.label("upline_id"),
                    Referral.referred_to.label("downline_id")
                )
                .where(Referral.referred_to == user_id)
                .cte(name="upline_cte", recursive=True)
            )

            recursive_query = (
                cte.union_all(
                    select(
                        Referral.referred_by.label("upline_id"),
                        cte.c.upline_id.label("downline_id")
                    )
                    .join(Referral, Referral.referred_to == cte.c.upline_id)
                )
            )

            # Execute Query to Fetch All Uplines
            result = await db.execute(
                select(User)
                .join(recursive_query, recursive_query.c.upline_id == User.user_id)
                .options(joinedload(User.user_details))
            )
            uplines = result.scalars().all()

            # ✅ Fetch the Current User's Details
            user_query = select(User).filter(User.user_id == user_id).options(joinedload(User.user_details))
            user_result = await db.execute(user_query)
            current_user = user_result.scalars().first()

            if not current_user:
                return None  # User not found

            # ✅ Format User Data (Using Schema)
            user_data = UserSchema(
                user_id=current_user.user_id,
                mobile_number=current_user.mobile_number,
                account_type=current_user.account_type,
                first_name=current_user.user_details.first_name if current_user.user_details else None,
                middle_name=current_user.user_details.middle_name if current_user.user_details else None,
                last_name=current_user.user_details.last_name if current_user.user_details else None,
                suffix=current_user.user_details.suffix_name if current_user.user_details else None,
                status="ACTIVATED" if current_user.is_activated else "NOT ACTIVATED"
            )

            # ✅ Format Uplines Data (Using Schema)
            uplines_data = [
                UserSchema(
                    user_id=upline.user_id,
                    mobile_number=upline.mobile_number,
                    account_type=upline.account_type,
                    first_name=upline.user_details.first_name if upline.user_details else None,
                    middle_name=upline.user_details.middle_name if upline.user_details else None,
                    last_name=upline.user_details.last_name if upline.user_details else None,
                    suffix=upline.user_details.suffix_name if upline.user_details else None,
                    status="ACTIVATED" if upline.is_activated else "NOT ACTIVATED"
                )
                for upline in uplines
            ]

            return ReferralUplineSchema(user=user_data, uplines=uplines_data)

        except Exception as e:
            print(f"Error fetching upline: {e}")
            return None  # Handle error gracefully


    @staticmethod
    async def get_downline(db: AsyncSession, user_id: str) -> Optional[ReferralDownlineSchema]:
        """Fetch user details and their downline hierarchy recursively using CTE."""

        try:
            # ✅ Step 1: Define the recursive CTE to get all downline user IDs
            downline_cte = (
                select(Referral.referred_by, Referral.referred_to)
                .filter(Referral.referred_by == user_id)
                .cte(name="downline", recursive=True)
            )

            recursive_query = (
                select(Referral.referred_by, Referral.referred_to)
                .join(downline_cte, Referral.referred_by == downline_cte.c.referred_to)
            )

            downline_cte = downline_cte.union_all(recursive_query)

            # ✅ Step 2: Fetch user details for downline members
            result = await db.execute(
                select(User)
                .join(downline_cte, User.user_id == downline_cte.c.referred_to)
                .options(joinedload(User.user_details))  # Load user details relationship
            )

            downlines = [
                UserSchema(
                    user_id=user.user_id,
                    mobile_number=user.mobile_number,
                    account_type=user.account_type,
                    first_name=user.user_details.first_name if user.user_details else None,
                    middle_name=user.user_details.middle_name if user.user_details else None,
                    last_name=user.user_details.last_name if user.user_details else None,
                    suffix=user.user_details.suffix_name if user.user_details else None,
                    status="ACTIVATED" if user.is_activated else "NOT ACTIVATED"
                )
                for user in result.scalars().all()
            ]

            # ✅ Step 3: Fetch the current user's details
            result = await db.execute(
                select(User)
                .filter(User.user_id == user_id)
                .options(joinedload(User.user_details))
            )
            current_user = result.scalars().first()

            if not current_user:
                return None  # If user not found, return None

            user_data = UserSchema(
                user_id=current_user.user_id,
                mobile_number=current_user.mobile_number,
                account_type=current_user.account_type,
                first_name=current_user.user_details.first_name if current_user.user_details else None,
                middle_name=current_user.user_details.middle_name if current_user.user_details else None,
                last_name=current_user.user_details.last_name if current_user.user_details else None,
                suffix=current_user.user_details.suffix_name if current_user.user_details else None,
                status="ACTIVATED" if current_user.is_activated else "NOT ACTIVATED"
            )

            # ✅ Step 4: Return structured response with both user and downlines
            return ReferralDownlineSchema(user=user_data, downlines=downlines)

        except Exception as e:
            print(f"Error fetching downline: {e}")
            return None


    @staticmethod
    async def get_user_downline(db: AsyncSession, user_id: str) -> List[UserSchema]:
        """Fetch only the downline members recursively (all levels)."""

        try:
            # Recursive Common Table Expression (CTE) to fetch all downlines
            downline_cte = (
                select(Referral.referred_by, Referral.referred_to)
                .filter(Referral.referred_by == user_id)
                .cte(name="downline", recursive=True)
            )

            recursive_query = (
                select(Referral.referred_by, Referral.referred_to)
                .join(downline_cte, Referral.referred_by == downline_cte.c.referred_to)
            )

            downline_cte = downline_cte.union_all(recursive_query)

            # Execute the query to get all downlines with joined user details
            result = await db.execute(
                select(User)
                .join(downline_cte, User.user_id == downline_cte.c.referred_to)
                .options(joinedload(User.user_details))  # Load user details relationship
            )

            downlines = [
                UserSchema(
                    user_id=user.user_id,
                    mobile_number=user.mobile_number,
                    account_type=user.account_type,
                    first_name=user.user_details.first_name if user.user_details else None,
                    middle_name=user.user_details.middle_name if user.user_details else None,
                    last_name=user.user_details.last_name if user.user_details else None,
                    suffix=user.user_details.suffix_name if user.user_details else None,
                    status="ACTIVATED" if user.is_activated else "NOT ACTIVATED"
                )
                for user in result.scalars().all()
            ]

            return downlines  # ✅ Return only the downlines list

        except Exception as e:
            print(f"Error fetching downline: {e}")
            return []

    
    @staticmethod
    async def get_users_by_activation_status(db: AsyncSession, is_activated: bool) -> List[User]:
        query = (
            select(User)
            .options(
                joinedload(User.user_details),  # Load user details
                joinedload(User.community)  # Load community info
            )
            .where(User.is_activated == is_activated)
        )
        result = await db.execute(query)
        return result.scalars().all()  # Return list of User objects


    

    @staticmethod
    async def get_user_by_mobile(db: AsyncSession, mobile_number: str):
        try:
            result = await db.execute(
                select(User).filter(User.mobile_number == mobile_number)
            )
            user = result.scalars().first()
            return user
        
        except Exception as e:
            raise e
        







    # NEW USER REPOSITORY

    @staticmethod
    async def get_user_data(db: AsyncSession, user_id: str):
        try:
            query = (
            select(User)
            .where(User.user_id == user_id)
            )

            result = await db.execute(query)
            user = result.scalar_one_or_none()

            return user

        except Exception as e:
            raise e

    @staticmethod
    async def get_user_external_id(db: AsyncSession, user_id: str):
        try:
            query = (
                select(UserWalletExtension.external_id)
                .join(UserWallet, UserWallet.wallet_id == UserWalletExtension.wallet_id)
                .where(UserWallet.user_id == user_id)
            )

            result = await db.execute(query)
            external_id = result.scalar_one_or_none()

            return external_id

        except Exception as e:
            raise e
        
    @staticmethod
    async def get_user_name(db: AsyncSession, user_id: str):
        try:
            query = (
                select(
                    UserDetail.last_name, 
                    UserDetail.first_name, 
                    UserDetail.middle_name, 
                    UserDetail.suffix_name
                )
                .where(UserDetail.user_id == user_id)
            )
            result = await db.execute(query)
            user_details = result.first()

            if user_details:
                return {
                    "last_name": user_details.last_name,
                    "first_name": user_details.first_name,
                    "middle_name": user_details.middle_name,
                    "suffix_name": user_details.suffix_name,
                }
            return None
        except Exception as e:
            raise e

    

    @staticmethod
    async def get_user_wallet_balance(db: AsyncSession, user_id: str):
        try:
            query = (
                select(Wallet.balance)
                .join(UserWallet, Wallet.wallet_id == UserWallet.wallet_id)
                .where(UserWallet.user_id == user_id)
            )

            result = await db.execute(query)
            balance = result.scalar_one_or_none()

            return balance
        
        except Exception as e:
            raise e
    
    @staticmethod
    async def update_user_wallet_balance(db: AsyncSession, user_id: str, new_balance: float):
        try:
            query = (
                update(Wallet)
                .values(balance=new_balance)
                .where(Wallet.wallet_id == select(UserWallet.wallet_id)
                    .where(UserWallet.user_id == user_id)
                    .scalar_subquery())
            )
            await db.execute(query)
            await db.commit()  # Commit changes to the database
        except Exception as e:
            await db.rollback()
            raise e






    @staticmethod
    async def get_member_details(db: AsyncSession):
        try:
            query = (
                select(
                    User.user_id,
                    UserDetail.last_name,
                    UserDetail.first_name,
                    UserDetail.middle_name,
                    UserDetail.suffix_name,
                    User.mobile_number,
                    Wallet.balance.label("wallet_balance"),
                    Wallet.reward_points,
                    User.account_type,
                    Community.community_id,
                    Community.community_name,
                    UserAddress.house_number,
                    UserAddress.street_name,
                    UserAddress.barangay,
                    UserAddress.city,
                    UserAddress.province,
                    UserAddress.region,
                    User.is_kyc_verified,
                    User.is_activated,
                    User.created_at.label("date_created")
                )
                .join(UserDetail, User.user_id == UserDetail.user_id)
                .outerjoin(UserWallet, User.user_id == UserWallet.user_id)
                .outerjoin(Wallet, UserWallet.wallet_id == Wallet.wallet_id)
                .outerjoin(Community, User.community_id == Community.community_id)
                .outerjoin(UserAddress, User.user_id == UserAddress.user_id)
            )

            result = await db.execute(query)
            users_list = result.mappings().all()  # Convert to list of dictionaries

            return users_list

        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={"message": f"Error fetching member details: {str(e)}"}
            )



    @staticmethod
    async def get_member_info(db: AsyncSession, user_id: str):
        try:
            query = (
                select(
                    User.user_id,
                    User.referral_id,
                    UserDetail.last_name,
                    UserDetail.first_name,
                    UserDetail.middle_name,
                    UserDetail.suffix_name,
                    User.mobile_number,
                    Wallet.balance.label("wallet_balance"),
                    Wallet.reward_points,
                    User.account_type,
                    Community.community_id,
                    Community.community_name,
                    UserAddress.house_number,
                    UserAddress.street_name,
                    UserAddress.barangay,
                    UserAddress.city,
                    UserAddress.province,
                    UserAddress.region,
                    User.is_kyc_verified,
                    User.is_activated,
                    User.created_at.label("date_created")
                )
                .join(UserDetail, User.user_id == UserDetail.user_id)
                .outerjoin(UserWallet, User.user_id == UserWallet.user_id)
                .outerjoin(Wallet, UserWallet.wallet_id == Wallet.wallet_id)
                .outerjoin(Community, User.community_id == Community.community_id)
                .outerjoin(UserAddress, User.user_id == UserAddress.user_id)
                .where(User.user_id == user_id)
            )

            result = await db.execute(query)
            user_data = result.mappings().first()  # Fetch single user

            if not user_data:
                return JSONResponse(
                    status_code=404,
                    content={"message": "User not found"}
                )

            # Convert Decimal to float
            user_dict = dict(user_data)
            if user_dict.get("wallet_balance") is not None:
                user_dict["wallet_balance"] = float(user_dict["wallet_balance"])
            if user_dict.get("reward_points") is not None:
                user_dict["reward_points"] = float(user_dict["reward_points"])

            return user_dict  # Return as dictionary for Pydantic parsing

        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={"message": f"Error fetching member details: {str(e)}"}
            )

















