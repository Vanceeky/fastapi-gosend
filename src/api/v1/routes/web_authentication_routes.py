from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

from api.v1.services.web_authentication_service import WebAuthenticationService
from fastapi import status
from api.v1.schemas.web_authentication_schema import LoginRequest, AuthUser

router = APIRouter()

@router.post('/initiate-login', status_code=status.HTTP_200_OK)
async def initiate_login(login_request: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await WebAuthenticationService.initiate_login(db, login_request.mobile_number)

@router.post('/verify-otp-and-authenticate', status_code=status.HTTP_200_OK)
async def verify_otp_and_authenticate(auth_data: AuthUser, db: AsyncSession = Depends(get_db)):
    return await WebAuthenticationService.verify_otp_and_authenticate(db, auth_data)