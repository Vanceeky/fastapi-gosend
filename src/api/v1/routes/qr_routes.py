from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.security import JWTBearer, get_jwt_identity
from fastapi import status
from core.database import get_db
from api.v1.services.qr_service import QRService

from api.v1.schemas.qr_schema import pay_qr

router = APIRouter()

@router.post("/payqr/", status_code = status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def get_payqr(
    payQR: pay_qr,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(JWTBearer()),
    ):
    user_id = get_jwt_identity(token)
    return await QRService.get_payQR(db, payQR, user_id)
