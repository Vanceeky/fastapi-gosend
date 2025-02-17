from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload


from models.admin_accounts_model import AdminAccount
from api.v1.schemas.admin_accounts_schema import AdminAccountCreate

from fastapi import HTTPException
from models.user_model import User



class AdminAccountRepository:
    @staticmethod
    async def create_admin_account(db: AsyncSession, admin_account_data: dict):
        try:
            # Create the admin account object in the repository
            admin_account = AdminAccount(**admin_account_data)
            db.add(admin_account)
            await db.commit()
            await db.refresh(admin_account)
            return admin_account
        except Exception as e:
            # Handle any error during the creation of the admin account
            raise HTTPException(status_code=500, detail=f"Error creating admin account: {str(e)}")


    @staticmethod
    async def get_user_by_mobile_number(db: AsyncSession, mobile_number: str):
        result = await db.execute(
            select(User).where(User.mobile_number == mobile_number)
        )
        user = result.scalar_one_or_none()  # Returns the user object or None
        return user


    @staticmethod
    async def get_admin_account(db: AsyncSession, account_url: str):
        result = await db.execute(
            select(AdminAccount).where(AdminAccount.account_url == account_url)
        )

        admin_account = result.scalar()
        if not admin_account:
            raise HTTPException(status_code=404, detail="Admin account not found")

        return admin_account