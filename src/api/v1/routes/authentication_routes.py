from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from api.v1.services.authentication_service import AuthenticationService
from fastapi import status
from api.v1.schemas.authentication_schema import LoginRequest

router = APIRouter()


@router.post("/login/", status_code=status.HTTP_200_OK)
async def initiate_login(login_request: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthenticationService.initiate_login(db, login_request.mobile_number)

@router.post("/login/{otp_code}/", status_code=status.HTTP_200_OK)
async def process_login(
    otp_code: str,
    data: LoginRequest, 
    db: AsyncSession = Depends(get_db),
):
    return await AuthenticationService.process_login(db, data, otp_code)
