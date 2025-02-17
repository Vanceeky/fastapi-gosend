from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.schemas.user_schema import UserCreate, UserUpdate, UserResponse, ProcessAccountInput, UplineResponse, DownlineResponse, ProcessMemberActivation, InitiateMemberActivation
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



@router.post('/downline', status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def get_downline(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(JWTBearer())
):
    user_id = get_jwt_identity(token)
    return await UserService.get_user_downline_members(db, user_id)


@router.post('/initiate-member-activation', status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def initiate_member_activation(
    user_id: InitiateMemberActivation,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(JWTBearer())
):
    activated_by = get_jwt_identity(token)
    return await UserService.initiate_member_activation(db, user_id, activated_by)

@router.post('/process-member-activation', status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
async def process_member_activation(
    user_id: ProcessMemberActivation,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(JWTBearer())
):
    activated_by = get_jwt_identity(token)
    return await UserService.process_member_activation(db, user_id, activated_by)



@router.get("/{user_id}/upline", response_model=UplineResponse)
async def get_user_upline(user_id: str, db: AsyncSession = Depends(get_db)):
    upline = await UserService.get_user_upline_service(db, user_id)
    return upline

@router.get("/{user_id}/downline", response_model=DownlineResponse)
async def get_user_downline(user_id: str, db: AsyncSession = Depends(get_db)):
    downline = await UserService.get_user_downline_service(db, user_id)
    return downline