from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.schemas.merchant_schema import MerchantCreate
from api.v1.schemas.merchant_schema import MerchantDetailsCreate
#from api.v1.services.merchant_service import create_merchant_service, get_all_merchants_service
from core.database import get_db

from api.v1.schemas.merchant_schema import MerchantCreate, MerchantResponse, MerchantUpdate, PurchaseData
from api.v1.services.merchant_service import MerchantService
from api.v1.repositories.merchant_repository import MerchantRepository
from typing import List

from utils.responses import json_response
from core.security import JWTBearer, get_jwt_identity
from fastapi import status


router = APIRouter()


@router.get('/', response_model=List[MerchantResponse])
async def get_all_merchants(db: AsyncSession = Depends(get_db)):
    return await MerchantService.get_all_merchant_service(db)


@router.get("/{merchant_id}", response_model=dict)
async def get_merchant(merchant_id: str, db: AsyncSession = Depends(get_db)):
    return await MerchantService.get_merchant_service(db, merchant_id)

@router.post('/{referrer_id}')
async def create_merchant(merchant_data: MerchantCreate, referral_id: str,db: AsyncSession = Depends(get_db)):
    return await MerchantService.create_merchant_service(db, merchant_data, referral_id)

@router.put("/{merchant_id}")
async def update_merchant_view(merchant_id: str, merchant_update_data: MerchantUpdate, db: AsyncSession = Depends(get_db)):
    return await MerchantService.update_merchant_service(db, merchant_id, merchant_update_data)

@router.delete("/{merchant_id}")
async def delete_merchant(merchant_id: str, db: AsyncSession = Depends(get_db)):
    return await MerchantService.delete_merchant_service(db, merchant_id)






@router.post('/purchase/{merchant_id}', status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def initiate_merchant_purchase(amount: PurchaseData, merchant_id: str, db: AsyncSession = Depends(get_db), token: str = Depends(JWTBearer())):
    user_id = get_jwt_identity(token)
    return await MerchantService.initiate_merchant_purchase(db, amount, merchant_id, user_id)