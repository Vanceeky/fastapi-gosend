
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from api.v1.services.admin_account_service import AdminAccountService
from fastapi import status
from core.security import JWTBearer, get_jwt_identity
from api.v1.schemas.admin_accounts_schema import AdminAccountCreate, AdminAccountResponse, AdminLoginRequest

from fastapi import HTTPException
from core.security import decode_jwt

router = APIRouter()


@router.post("/create-admin-accountt/", response_model=AdminAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_account2(
    admin_account_data: AdminAccountCreate,
    db: AsyncSession = Depends(get_db),  # Inject the database session correctly
):
    return await AdminAccountService.create_admin_account(db, admin_account_data)

@router.post("/create-admin-account/", response_model=AdminAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_account(
    admin_account_data: AdminAccountCreate,
    db: AsyncSession = Depends(get_db), 
    token_data: dict = Depends(JWTBearer()) 
):
    
    # Decode the token manually to extract the payload
    try:
        token_data = decode_jwt(token_data)  # Decode the JWT token using your function
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Invalid token or expired token: {str(e)}")

    # Now you have the token payload in `token_data`, which is a dictionary
    account_type = token_data.get('account_type')
    print("Account Type:", account_type)

    # Check if the account type is valid (SUPERADMIN or ADMIN)
    if account_type not in ["SUPERADMIN", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Unauthorized action based on account type.")

    
    return await AdminAccountService.create_admin_account(db, admin_account_data, account_type)


@router.post("/{account_url}/login", status_code=status.HTTP_200_OK)
async def initiate_login(
    account_url: str,  # Get account_url from URL path
    login_request: AdminLoginRequest,  # Accept password from request body
    db: AsyncSession = Depends(get_db),  # Inject the database session
):
    return await AdminAccountService.initiate_login(db, account_url, login_request)

