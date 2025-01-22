from sqlalchemy.ext.asyncio import AsyncSession
from models.referral_model import Commission

from api.v1.schemas.commission_schema import CommissionCreate

from uuid import uuid4




class CommissionRepository:
    @staticmethod
    async def create_commmission(db: AsyncSession, commission_data: CommissionCreate):

        try:
            commission = Commission(
                commission_id=str(uuid4()),
                user_id=commission_data.user_id,
                transaction_type=commission_data.transaction_type,
                level=commission_data.level,
                amount=commission_data.amount
            )

            db.add(commission)
            await db.commit()
            await db.refresh(commission)

            return commission

        except Exception as e:
            await db.rollback()
            raise e

class CommissionService:
    @staticmethod
    async def create_commission(db: AsyncSession, user_id: str, transaction_type: str, level: str, amount: float):
        try:
            commission = Commission(
                commission_id=str(uuid4()),  # Generate a unique ID for the commission record
                user_id=user_id,
                transaction_type=transaction_type,
                level=level,
                amount=amount,
            )

            db.add(commission)  # Add the commission to the database session
            await db.commit()  # Commit the changes

        except Exception as e:
            await db.rollback()  # Rollback the transaction in case of an error
            raise e

  