
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.services.unilevel_services import UnilevelService

from core.database import get_db
from core.security import JWTBearer, get_jwt_identity

router = APIRouter()
from fastapi import status



@router.get("", status_code=status.HTTP_200_OK)
async def get_unilevel_tree(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(JWTBearer())
    ):
    user_id = get_jwt_identity(token)
    return await UnilevelService.get_user_unilevel(db, user_id)