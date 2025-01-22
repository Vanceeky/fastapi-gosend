from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models.user_model import User, UserAddress, UserDetail, UserWallet
from models.wallet_model import Wallet
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from utils.responses import json_response

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