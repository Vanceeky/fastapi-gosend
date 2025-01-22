from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.otp_records_model import OTPRecord
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy import delete
from api.v1.schemas.otp_schema import OTPRecordCreate, OTPRecordResponse
from sqlalchemy import func

class OTPRepository:

    @staticmethod
    async def create_otp(db: AsyncSession, otp_record_data: OTPRecordCreate) -> OTPRecord:
        otp_record = OTPRecord(
            **otp_record_data.dict(),
        )

        db.add(otp_record)
        await db.commit()
        await db.refresh(otp_record)

        return otp_record
    
    @staticmethod
    async def get_by_number_and_code(db: AsyncSession, mobile_number: str, otp_code: str):
        try:
            result = await db.execute(
                select(OTPRecord).where(OTPRecord.mobile_number == mobile_number, OTPRecord.otp_code == otp_code)
            )

            
            return result.scalars().first()
        
        except Exception as e:
            raise e
        
    @staticmethod
    async def mark_as_used(db: AsyncSession, otp_record_id: str):
        try:
            result = await db.execute(
                select(OTPRecord).where(OTPRecord.otp_id == otp_record_id)
            )

            otp_record = result.scalars().first()
            if otp_record:
                otp_record.is_used = True
                await db.commit()
                return otp_record
            else:
                raise HTTPException(status_code=404, detail="OTP record not found")
            
        except Exception as e:
            raise e
        
    @staticmethod
    async def delete_expired(db: AsyncSession):
        try:
            result = await db.execute(
                select(OTPRecord).where(OTPRecord.expired_at < func.now())
            )

            otp_records = result.scalars().all()

            for otp_record in otp_records:
                db.delete(otp_record)

            await db.commit()

        except Exception as e:
            raise e

    async def delete_by_id(db: AsyncSession, otp_id: str):
        try:
            result = await db.execute(
                delete(OTPRecord).where(OTPRecord.otp_id == otp_id)
            )

            otp_record = result.scalar_one_or_none()

            if otp_record:
                await db.delete(otp_record)
                await db.commit()

            return None
        
        except Exception as e:
            raise e

        
        



