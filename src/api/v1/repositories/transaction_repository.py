from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from decouple import config
from models.user_model import UserDetail, User
from models.transaction_model import Transaction, Distribution
from api.v1.schemas.transaction_schema import TransactionDetails, DistributionCreate

from fastapi import HTTPException


class TransactionRepository:

    @staticmethod
    async def get_user(db: AsyncSession, user_id: str):
        try:

            result = await db.execute(
                select(User).filter(
                    User.user_id == user_id
                )
            )

            user = result.scalars().first()

            return user
        
        except Exception as e:
            raise e
        

    @staticmethod
    async def get_user_details(db: AsyncSession, user_id: str):
        try:

            result = await db.execute(
                select(UserDetail).filter(
                    UserDetail.user_id == user_id
                )
            )

            user_details = result.scalars().first()
            return user_details
        
        except Exception as e:
            raise e
        
    
    @staticmethod
    async def get_transaction(db: AsyncSession, transaction_reference: str):
        try:
            result = await db.execute(
                select(Transaction).filter(
                    Transaction.transaction_reference == transaction_reference
                )
            )

            transaction = result.scalars().first()

            return transaction
        
        except Exception as e:
            raise e
        

    @staticmethod
    async def create_transaction(db: AsyncSession, transaction_data: TransactionDetails):
        try:
            transaction = await Transaction(**transaction_data.dict())
            db.add(transaction)

            await db.commit()
            
            await db.refresh(transaction)

            return transaction
        except Exception as e:
            raise e
        
    @staticmethod
    async def create_distribution_history(db: AsyncSession, distribution_data: DistributionCreate):
        try:

            distribution = await Distribution(
                **distribution_data.dict()
            )

            db.add(distribution)
            await db.commit()
            await db.refresh(distribution)

            return distribution
        
        except Exception as e:
            raise HTTPException(status_code=400, details = f"Error creating Distribution: {str(e)}")
