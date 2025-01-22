from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models.merchant_model import Merchant, MerchantDetails
from uuid import uuid4
from models.user_model import User
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from utils.responses import json_response


class MerchantRepository:

    @staticmethod
    async def get_all_merchants(db: AsyncSession):
        try:
            result = await db.execute(
                select(Merchant).options(
                    #load related merchant details
                    (selectinload(Merchant.merchant_details)) 
                )

            )

            merchants = result.scalars().all()

            return merchants
        except Exception as e:
            raise e


    @staticmethod
    async def create_merchant(db: AsyncSession, merchant_data_dict: dict):
        try:
            # Create and add the merchant
            merchant = Merchant(
                #merchant_id = str(uuid4()),
                **merchant_data_dict
            )
            db.add(merchant)

            await db.commit()
            await db.refresh(merchant)

            return merchant
        
        except IntegrityError as e:
            await db.rollback()
            if "UNIQUE constraint failed" in str(e):
                return json_response(
                    message = "Merchant already exists with the given details",
                    status_code = 400
                )
            return json_response(
                message= f"Error creating merchant: {str(e)}",
                    status_code=500
            )

        except Exception as e:
            await db.rollback()
            return json_response(
                message=f"Unexpected error creating merchant: {str(e)}",
                status_code=500
            )

        
    @staticmethod
    async def get_merchant(db: AsyncSession, merchant_id: str):
        result = await db.execute(
            select(Merchant).filter(Merchant.merchant_id == merchant_id).options(
                selectinload(Merchant.merchant_details)
            )
        )

        merchant = result.scalars().first()

        return merchant





    @staticmethod
    async def update_merchant(db: AsyncSession, merchant_id: str, merchant_data: dict, merchant_details_data: list = None):
        try:
            result = await db.execute(select(Merchant).filter(Merchant.merchant_id == merchant_id))
            merchant = result.scalars().first()
            if not merchant:
                raise HTTPException(status_code=404, detail="Merchant not found")
            
            for key, value in merchant_data.items():
                if value is not None:
                    setattr(merchant, key, value)

            await db.commit()


            if merchant_details_data:
                await MerchantRepository.update_merchant_details(db, merchant_id, merchant_details_data)

            return merchant
        
        except Exception as e:
            await db.rollback()
            raise e
        
    @staticmethod
    async def update_merchant_details(db: AsyncSession, merchant_id: str, merchant_details_data: list):
        try:
            result = await db.execute(select(Merchant).filter(Merchant.merchant_id == merchant_id))

            merchant = result.scalars().first()
            if not merchant:
                raise HTTPException(status_code=404, detail="Merchant not found")

            for detail in merchant_details_data:
                merchant_detail = MerchantDetails(merchant_id=merchant.merchant_id, **detail)
                db.add(merchant_detail)

            await db.commit()

            return merchant

        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def delete_merchant(db: AsyncSession, merchant_id: str):
        try:
            # Fetch the existing merchant by ID
            result = await db.execute(select(Merchant).filter(Merchant.merchant_id == merchant_id))
            merchant = result.scalars().first()
            
            if not merchant:
                raise HTTPException(status_code=404, detail="Merchant not found")
            
            # Delete all associated merchant details
            await db.execute(
                delete(MerchantDetails).where(MerchantDetails.merchant_id == merchant_id)
            )
            
            # Now delete the merchant
            await db.execute(
                delete(Merchant).where(Merchant.merchant_id == merchant_id)
            )
            
           
            await db.commit()

            return {"status": "success", "message": "Merchant and its details deleted successfully"}
        
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))