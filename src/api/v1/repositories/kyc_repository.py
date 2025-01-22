from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user_model import UserWallet, UserWalletExtension




class KYCRepository:

    @staticmethod
    async def get_user(db: AsyncSession, user_id: str):
        try:
            # Fetch user_wallet from the database
            user_wallet_result = await db.execute(
                select(UserWallet).filter(
                    UserWallet.user_id == user_id
                )
            )

            # Retrieve the user_wallet record
            user_wallet = user_wallet_result.scalars().first()

            # Check if the user_wallet is None
            if not user_wallet:
                raise ValueError(f"No wallet found for user_id {user_id}")

            # Fetch user_wallet_extension related to the user_wallet
            user_wallet_extension_result = await db.execute(
                select(UserWalletExtension).filter(
                    UserWalletExtension.wallet_id == user_wallet.wallet_id
                )
            )

            # Retrieve the first user_wallet_extension record
            user_wallet_extension = user_wallet_extension_result.scalars().first()

            # Return the user_wallet_extension if found
            return user_wallet_extension

        except Exception as e:
            print(f"Error fetching user data: {e}")
            raise e
