from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.schemas.hub_schema import HubCreate, HubResponse
from api.v1.repositories.hub_repository import HubRepository

from utils.responses import json_response
from fastapi import HTTPException



class HubService:
    @staticmethod
    async def create_hub(db: AsyncSession, hub_data: HubCreate):
        try:
            
            hub_data = hub_data.dict()

            await HubRepository.create_hub(db, hub_data)
            

            return json_response(
                message="Hub Created Successfully!",
                status_code=201
            )
        
        except HTTPException as e:
            return json_response(
                message = e.detail,
                status_code= e.status_code
            )
        
        except Exception as e:
            return json_response(
                message=str(e),
                status_code=500
            )