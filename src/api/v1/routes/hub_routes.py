from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.schemas.hub_schema import HubCreate, HubResponse
from api.v1.services.hub_service import HubService

from fastapi import APIRouter, Depends

from core.database import get_db

router = APIRouter()


@router.post("", response_model=HubResponse)
async def create_hub(hub_data: HubCreate, db: AsyncSession = Depends(get_db)):
    return await HubService.create_hub(db, hub_data)