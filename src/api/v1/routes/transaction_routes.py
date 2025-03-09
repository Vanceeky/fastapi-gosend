from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.schemas.transaction_schema import TransactionCreate, ProcessTransaction, MerchantData, ProcessQrphTransaction
from api.v1.services.transaction_service import TransactionService
from core.database import get_db
from core.security import JWTBearer
from fastapi import status
from core.security import get_jwt_identity
router = APIRouter()



@router.get('/transactions', status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def get_all_transactions(db: AsyncSession = Depends(get_db), token: str = Depends(JWTBearer())):
    user_id = get_jwt_identity(token)
    return await TransactionService.get_all_transactions(db, user_id)

@router.get('/bank-list/', status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def bank_list(db: AsyncSession = Depends(get_db)):
    return await TransactionService.bank_list(db)

@router.post('/cash-out/', status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def initiate_cashout(
    transaction_data: TransactionCreate, 
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(JWTBearer())
):
    user_id = get_jwt_identity(token)
    return await TransactionService.initiate_cashout(db, transaction_data, user_id)


@router.post('/cash-out/{otp_code}/', status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def process_cashout(transaction_reference: ProcessTransaction, otp_code: str, db: AsyncSession = Depends(get_db), token: str = Depends(JWTBearer())):
    user_id = get_jwt_identity(token)
    return await TransactionService.process_cashout(db, transaction_reference, otp_code, user_id)

@router.post('resend-otp/', status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def resend_otp(
    transaction_id: ProcessTransaction, 
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(JWTBearer())
    ):
    user_id = get_jwt_identity(token)
    return await TransactionService.resend_tw_otp(db, transaction_id, user_id)




@router.post("/qrph/transfer/initiate", status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def initiate_qrph_transfer(transaction_data: MerchantData, db: AsyncSession = Depends(get_db), token: str = Depends(JWTBearer())):
    user_id = get_jwt_identity(token)
    return await TransactionService.initiate_qrph_transfer(db, transaction_data, user_id)


@router.post("qrph/transfer/process/{otp_code}", status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def process_qrph_transfer(
    transaction_reference: ProcessQrphTransaction, 
    otp_code: str, 
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(JWTBearer())
):
    user_id = get_jwt_identity(token)
    return await TransactionService.process_qrph_transfer(db, transaction_reference, otp_code, user_id)