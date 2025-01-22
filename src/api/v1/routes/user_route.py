from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.schemas.user_schema import UserCreate, UserUpdate, UserResponse, ProcessAccountInput
from api.v1.services.user_service import UserService
from core.database import get_db
from core.security import JWTBearer, get_jwt_identity
from fastapi import status

router = APIRouter()

@router.post("", response_model=UserResponse)
async def create_user(user_data: UserCreate, referral_id: str, db: AsyncSession = Depends(get_db)):
    return await UserService.create_user(db, user_data, referral_id)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    return await UserService.get_user(db, user_id)

@router.get("", response_model=list[UserResponse])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    return await UserService.get_all_users(db)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_data: UserUpdate, db: AsyncSession = Depends(get_db)):
    return await UserService.update_user(db, user_id, user_data)

@router.delete("/{user_id}")
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):
    return await UserService.delete_user(db, user_id)



@router.get('/user-balance', status_code = status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def get_user_balance(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(JWTBearer())
):
    user_id = get_jwt_identity(token)
    print("getting_user_balance", user_id)

    return await UserService.get_user_balancee(db, user_id)

@router.get("/activate-account/", status_code = status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def initiate_account_activation(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(JWTBearer())
):
    user_id = get_jwt_identity(token)

    return await UserService.initiate_account_activation(db, user_id)


@router.post("/activate-account/", status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def process_account_activation(
    process_account_input: ProcessAccountInput,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(JWTBearer())
):
    user_id = get_jwt_identity(token)

    return await UserService.process_account_activation(db, process_account_input, user_id)