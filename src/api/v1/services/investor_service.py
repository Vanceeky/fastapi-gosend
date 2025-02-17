from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.schemas.investor_schema import InvestorCreate
from api.v1.repositories.investor_repository import InvestorRepository

from utils.responses import json_response
from uuid import uuid4
from fastapi import HTTPException


class InvestorService:
    @staticmethod
    async def create_investor(db: AsyncSession, investor_data: InvestorCreate):
        try:
            if not investor_data.investor_user.strip():
                raise HTTPException(status_code=400, detail="Mobile number cannot be blank")
            
            investor_data = investor_data.dict()
            investor_data['investor_id'] = str(uuid4())

            # Call the repository to create the investor
            investor = await InvestorRepository.create_investor(db, investor_data)
            if investor:
                # Return the desired response structure
                return json_response(
                    message="Investor created successfully",
                    data={"investor_id": investor_data['investor_id']},
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
class InvestorService2:
    @staticmethod
    async def create_investor(db: AsyncSession, investor_data: InvestorCreate):
        try:
            # Start a transaction
            async with db.begin():  # This ensures all DB changes are wrapped in a transaction
                
                # Check if the user already exists as an investor
                if await InvestorRepository.is_user_already_investor(db, investor_data.investor_user):
                    raise HTTPException(status_code=400, detail="User already exists as an investor")
                
                # Update the user's role
                if not await InvestorRepository.update_investor_role(db, investor_data.investor_user):
                    raise HTTPException(status_code=400, detail="User role update failed")

                investor_data_dict = investor_data.dict()  # Convert to dict
                # Call repository to create the investor
                investor = await InvestorRepository.create_investor(db, investor_data_dict)

                # Commit the transaction and refresh the investor object
            await db.commit()
            await db.refresh(investor)

            # If everything was successful, return the response with the investor_id
            return json_response(
                message="Investor created successfully",
                data={"investor_id": investor.investor_id},  # Return the investor's ID after commit
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
        
        