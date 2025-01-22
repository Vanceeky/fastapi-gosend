from fastapi import APIRouter, Depends
from core.security import JWTBearer, get_jwt_identity
from fastapi import status
from core.database import get_db
from api.v1.services.qr_service import QRService
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.schemas.qr_schema import pay_qr

router = APIRouter()

@router.post("", status_code = status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def get_payQR(
    payQR: pay_qr,
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(JWTBearer())
):
    user_id = get_jwt_identity(token)
    return await QRService.get_payQR(db, payQR, user_id)