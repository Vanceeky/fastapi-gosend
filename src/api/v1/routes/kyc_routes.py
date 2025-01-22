from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from api.v1.services.kyc_service import KYCService
from fastapi import status

from core.security import JWTBearer, get_jwt_identity



router = APIRouter()

@router.post('/topwallet', status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def kyc_topwallet(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(JWTBearer()),
    ):
    user_id = get_jwt_identity(token)
    return await KYCService.kyc_topwallet(db, user_id)

