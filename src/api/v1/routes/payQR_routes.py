from fastapi import APIRouter, Depends
from core.security import JWTBearer, get_jwt_identity
from fastapi import status
from core.database import get_db
from api.v1.services.qr_service import QRService
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.schemas.qr_schema import pay_qr
from api.v1.schemas.payQR_schema import PayQR, ProcessPayTransaction
from api.v1.services.payQR import PayQRService


router = APIRouter()

@router.post("/test", status_code = status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def get_payQR(
    payQR: pay_qr,
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(JWTBearer())
):
    user_id = get_jwt_identity(token)
    return await QRService.get_payQR(db, payQR, user_id)


@router.post("", status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def pay_merchant_qr(
    payQR_data: PayQR,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(JWTBearer()),
):
    user_id = get_jwt_identity(token)  # Extract user ID from JWT
    return await PayQRService.pay_merchant_qr(db, payQR_data, user_id)

@router.post("/process/payment/", status_code = status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def process_pay_qr(
    process_pay_qr_data: ProcessPayTransaction,
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(JWTBearer())
):
    user_id = get_jwt_identity(token)
    return await PayQRService.process_pay_qr(db, process_pay_qr_data, user_id)
