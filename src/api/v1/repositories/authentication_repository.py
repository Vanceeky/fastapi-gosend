from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models.user_model import User


class AuthenticationRepository:
    
    @staticmethod
    async def get_user_by_mobile_number(db: AsyncSession, mobile_number: str) -> User:
        result = await db.execute(
            select(User).where(User.mobile_number == mobile_number)
        )
        return result.scalars().first()
    
    

'''
    @staticmethod
    async def update_user_mpin(db: AsyncSession, user_id: str, mpin: str) -> User:
        user = await AuthenticationRepository.get_user_by_mobile_number(db, user_id)
        
        if user:
            user.mpin = mpin
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
        
        return None
'''

