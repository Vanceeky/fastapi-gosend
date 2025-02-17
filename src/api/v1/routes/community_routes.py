from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.schemas.community_schema import CommunityCreate, CommunityResponse, CommunityWithLeaderDetailsResponse, CommunityMembersResponse, CommunitySchema
from api.v1.services.community_service import CommunityService
from api.v1.repositories.community_repository import CommunityRepository
from fastapi import APIRouter, Depends

from core.database import get_db
from typing import List

from fastapi import HTTPException

router = APIRouter()


@router.post("", response_model=CommunityResponse)
async def create_community(community_data: CommunityCreate, db: AsyncSession = Depends(get_db)):
    return await CommunityService.create_community(db, community_data)


@router.get("/", response_model=List[CommunitySchema])  # Response validation
async def get_all_communities(db: AsyncSession = Depends(get_db)):
    return await CommunityService.get_all_communities(db)

@router.get("/{community_id}/members", response_model=CommunityMembersResponse)
async def get_community_members(community_id: str, db: AsyncSession = Depends(get_db)):
    community_data = await CommunityService.get_community_members(db, community_id)

    if not community_data:
        raise HTTPException(status_code=404, detail="Community not found or has no members.")

    return community_data  # FastAPI automatically converts dict to Pydantic model


@router.get("/{community_id}", response_model=CommunityWithLeaderDetailsResponse)
async def get_community_with_leader_details_endpoint(community_id: str, db: AsyncSession = Depends(get_db)):
    return await CommunityRepository.get_community_with_leader_details(db, community_id)
