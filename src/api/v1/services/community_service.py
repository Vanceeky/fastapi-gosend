from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.schemas.community_schema import CommunityCreate, CommunitySchema
from api.v1.repositories.community_repository import CommunityRepository

from utils.responses import json_response
from uuid import uuid4
from fastapi import HTTPException
from typing import Dict, Any, List
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




class CommunityService:
    @staticmethod
    async def create_community(db: AsyncSession, community_data: CommunityCreate):
        try:

            if not community_data.community_name.strip():
                raise HTTPException(status_code=400, detail="Community name cannot be blank")
            
            community_data = community_data.dict()
            community_data['community_id'] = str(uuid4())

            await CommunityRepository.create_community(db, community_data)
            #print(f'Community created: {community}')

            return json_response(
                message="Community created successfully",
                data={"community_id": community_data['community_id']},
                status_code=201
            )
        except HTTPException as e:
            return json_response(
                message=e.detail,
                status_code=e.status_code
            )
        except Exception as e:
            return json_response(
                message=str(e),
                status_code=500
            )


    @staticmethod
    async def get_all_communities(db: AsyncSession) -> List[CommunitySchema]:
        try:    
            communities = await CommunityRepository.get_all_communities(db)

            print("communities", communities)
            
            if communities is None:
                return json_response(
                    message="Failed to retrieve communities",
                    status_code=500
                )

            return json_response(
                message="Communities retrieved successfully",
                data=[community.model_dump() for community in communities],  # Convert Pydantic model to dict
                status_code=200
            )

        except Exception as e:
            return json_response(
                message=str(e),
                status_code=500
            )

    @staticmethod
    async def get_community_members(db: AsyncSession, community_id: str):

        community_members = await CommunityRepository.get_community_members(db, community_id)
        return json_response(
            message="Community members retrieved successfully",
            data=community_members,
            status_code=200
        )
    
class CommunityService2:
    @staticmethod
    async def create_community(db: AsyncSession, community_data: CommunityCreate) -> Dict[str, Any]:
        """Service method to create a new community and update the leader's role."""
        try:
            # Validate community name
            if not community_data.community_name.strip():
                raise HTTPException(status_code=400, detail="Community name cannot be blank")

            # Convert Pydantic model to dictionary and add a unique community ID
            community_data_dict = community_data.dict()
            community_data_dict["community_id"] = str(uuid4())

            # Create the community
            community = await CommunityRepository.create_community(db, community_data_dict)

            # Update the leader's role
            await CommunityRepository.update_leader_role(db, community_data_dict["leader_mobile_number"])

            return {
                "message": "Community created successfully",
                "data": {"community_id": community_data_dict["community_id"]},
                "status_code": 201,
            }

        except HTTPException as e:
            logger.error(f"HTTPException in create_community: {e.detail}")
            return {"message": e.detail, "status_code": e.status_code}
        except Exception as e:
            logger.error(f"Unexpected error in create_community: {e}")
            return {"message": "Internal server error", "status_code": 500}
        
