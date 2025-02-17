from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.schemas.investor_schema import InvestorResponse, InvestorCreate
from api.v1.repositories.investor_repository import InvestorRepository
from fastapi import APIRouter, Depends


from fastapi import status 
from core.database import get_db
from api.v1.services.investor_service import InvestorService


router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_investor(investor_data: InvestorCreate, db: AsyncSession = Depends(get_db)):
    return await InvestorService.create_investor(db, investor_data)