from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from models.user_model import User




class WebAuthenticationRepository:
    @staticmethod
    async def get_user(db: AsyncSession, mobile_number: str):
        result = await db.execute(
            select(User).where(User.mobile_number == mobile_number)
        )
        user = result.scalar_one_or_none()  # Returns the user object or None
        return user
    
