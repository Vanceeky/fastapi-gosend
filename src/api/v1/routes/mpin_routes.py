from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from api.v1.services.mpin_service import MPINService
from fastapi import status

from core.security import JWTBearer
from api.v1.schemas.mpin_schema import MPINRequest, ResetMPIN
from api.v1.repositories.user_repository import UserRepository

from core.security import get_jwt_identity

router = APIRouter()


@router.post('/validate/', status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def validate_mpin(
    validateMPIN: MPINRequest, 
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(JWTBearer())
):
    user_id = get_jwt_identity(token)
    return await MPINService.validate_mpin(db, validateMPIN, user_id)
    



@router.post('/set/', status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def set_mpin(
    setMPIN: MPINRequest, 
    db: AsyncSession = Depends(get_db),
    token: str = Depends(JWTBearer()),
):

    user_id = get_jwt_identity(token)
    response = await MPINService.set_mpin(db, setMPIN, user_id)
    return response

@router.get('/reset/', status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def initiate_mpin_reset(
    db: AsyncSession = Depends(get_db),
    token: str =  Depends(JWTBearer()),
):
    
    user_id = get_jwt_identity(token)
    response = await MPINService.initiate_mpin_reset(db, user_id)
    return response

@router.post('/reset/', status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def process_mpin_reset(
    mpin_data: ResetMPIN, 
    db: AsyncSession = Depends(get_db),
    token: str = Depends(JWTBearer()),
    ):

    user_id = get_jwt_identity(token)

    user = await UserRepository.get_user(db, user_id)

    mobile_number = user.mobile_number
    
    print(f"mobile number: {mobile_number}")

    response = await MPINService.process_mpin_reset(db, mpin_data, mobile_number)
    return response
