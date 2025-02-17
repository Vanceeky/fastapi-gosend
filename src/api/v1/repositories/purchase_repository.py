from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.purchase_model import MerchantPurchase
from models.merchant_model import Merchant
from fastapi import HTTPException



class PurchaseRepository:

    @staticmethod
    async def get_merchant_purchase(db: AsyncSession, reference_id: str):

        try:
            result = await db.execute(
                select(MerchantPurchase).where(
                    MerchantPurchase.reference_id == reference_id
                )
            )

            purchases = result.scalars().first()

            return purchases

        except Exception as e:
            raise e
        
    @staticmethod
    async def get_merchant_discount(db: AsyncSession, merchant_id: str):
        try:
            result = await db.execute(
                select(
                    Merchant.discount
                ).where(
                    Merchant.merchant_id == merchant_id
                )
            )

            discount = result.scalars().first()

            return discount

        except Exception as e:
            raise e