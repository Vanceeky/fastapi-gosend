from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models.referral_model import Referral, MerchantReferral
from uuid import uuid4
from fastapi import HTTPException
from datetime import datetime
from models.user_model import User
from models.merchant_model import Merchant

from utils.responses import json_response

from sqlalchemy.exc import IntegrityError


class ReferralRepository:

    @staticmethod
    async def get_all_referrals(db: AsyncSession):
        try:
            result = await db.execute(
                select(Referral)
            )

            referrals = result.scalars().all()

            return referrals    
        except Exception as e:
            raise e
        

    @staticmethod
    async def create_referral(db: AsyncSession, referred_by: str, referred_to: str) -> Referral:
        try:
            
            referred_by_result = await db.execute(
                select(User).filter(User.referral_id == referred_by)
            )
            #referred_by = referred_by_result.scalars().all()
            print("referred_by", referred_by)
            referred_by = referred_by_result.scalars().first()
            if not referred_by:
                raise HTTPException(status_code=400, detail="Referred by user not found")

            referred_to_result = await db.execute(
                select(User).filter(User.user_id == referred_to)
            )
            referred_to = referred_to_result.scalars().first()
            if not referred_to:
                raise HTTPException(status_code=400, detail="Referred to user not found")

            existing_referral = await db.execute(
                select(Referral).filter(
                    Referral.referred_by == referred_by,
                    Referral.referred_to == referred_to,
                )
            )
            if existing_referral.scalars().first():
                raise HTTPException(status_code=400, detail="Referral already exists")

            # Create a new referral object
            new_referral = Referral(
                referral_id=str(uuid4()),
                referred_by=referred_by,
                referred_to=referred_to,
            )

            # Add to DB and commit
            db.add(new_referral)
            await db.commit()
            await db.refresh(new_referral)

            return new_referral

        except HTTPException:
            raise  # Re-raise HTTP exceptions directly

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create referral: {e}")


    @staticmethod
    async def create_referral2(db: AsyncSession, referred_by: str, referred_to: str) -> Referral:
        try:
            # Fetch both referred_by and referred_to users in a single query
            result = await db.execute(
                select(User).filter(User.user_id.in_([referred_by, referred_to]))
            )
            users = result.scalars().all()

            # Check if both users exist (must return exactly two users)
            if len(users) != 2:
                raise HTTPException(status_code=404, detail="One or both users not found")
            
            existing_referral = await db.execute(
                select(Referral).filter(
                    Referral.referred_by == referred_by,
                    Referral.referred_to == referred_to,
                )
            )

            if existing_referral.scalars().first():
                raise HTTPException(status_code=400, detail="Referral already exists")

            # Create a new referral object
            new_referral = Referral(
                referral_id=str(uuid4()),
                referred_by=referred_by,
                referred_to=referred_to,
            )

            # Add to DB and commit
            db.add(new_referral)
            await db.commit()
            await db.refresh(new_referral)

            return new_referral

        except Exception as e:
            await db.rollback()
            raise e


    @staticmethod
    async def get_referral(db: AsyncSession, user_id: str):
        try:
            
            result = await db.execute(
                select(Referral.referred_by).filter(Referral.referred_to == user_id)
            )

            referred_by = result.scalars().first()
            return referred_by

        except Exception as e:
            raise e


        


    @staticmethod
    async def create_commission(db: AsyncSession):
        pass



    @staticmethod
    async def create_merchant_referral(db: AsyncSession, referred_by: str, referred_to: str) -> MerchantReferral:
        try:

            user = await db.execute(select(User).filter(
                User.user_id == referred_by
            ))

            user = user.scalars().first()


            merchant = await db.execute(
                select(Merchant).filter(
                    Merchant.mobile_number == referred_to
                )
            )

            merchant = merchant.scalars().first()

            if not user or not merchant:
                return None


            merchant_referral = MerchantReferral(
                referral_id=str(uuid4()), 
                referred_by=referred_by,
                referred_to=merchant.merchant_id  
            )

            db.add(merchant_referral)
            await db.commit()
            await db.refresh(merchant_referral)

            return merchant_referral
        
        except IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                return json_response(
                    message="Referral already exists for this merchant",
                    status_code=400
                )
            
            return json_response(
                message=f"Database integrity error while creating referral {str(e)}",
                status_code=400
            )
        
        except Exception as e:
            await db.rollback()
            return json_response(
                message=f"Unexpected error creating Merchant referral: {str(e)}",
                status_code=400
            )
            
            #raise HTTPException(status_code=400, detail=f"Error creating Merchant referral: {str(e)}")
