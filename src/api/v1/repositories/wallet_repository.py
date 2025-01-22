from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models.wallet_model import Wallet, WalletExtensions


class WalletRepository:
    @staticmethod
    async def get_wallet_extension(db: AsyncSession, extension_name: str):
        try:
            result = await db.execute(
                select(WalletExtensions).filter(WalletExtensions.extension_name == extension_name)
            )

            wallet_extension = result.scalars().first()

            return wallet_extension

        except Exception as e:
            raise e