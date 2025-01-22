from sqlalchemy.ext.asyncio import AsyncSession
from utils.responses import json_response
from api.v1.services.unilevel_services import UnilevelService
from api.v1.repositories.commission_repository import CommissionRepository
from api.v1.repositories.user_repository import UserRepository
from api.v1.repositories.transaction_repository import TransactionRepository
from models.transaction_model import Transaction
from api.v1.schemas.transaction_schema import TransactionDetails
from decouple import config

from uuid import uuid4
from utils.extra import mask_name

from fastapi import HTTPException



class CommissionService:
    @staticmethod
    async def account_activation_reward(db: AsyncSession, user_id: str, transaction_id: str):


        unilevel_distribution_amounts = {
            "first_level": 40.00,
            "second_level": 10.00,
            "third_level": 5.00,
        }

        try:
            unilevels = await UnilevelService.get_user_unilevel(db, user_id)

            if not unilevels:
                return
                
            for level, reward_amount in unilevel_distribution_amounts.items():

                beneficiary_id = unilevels.get(level)

                beneficiary = await UserRepository.get_user(db, beneficiary_id)


                if beneficiary_id and beneficiary.is_activated:
                    await CommissionRepository.create_commmission(
                        db,
                        user_id = beneficiary_id,
                        transaction_type = "Account activation reward",
                        level = level,
                        amount = reward_amount
                    )


    
        except Exception as e:
            raise e


    @staticmethod
    async def admin_distribution_reward(db: AsyncSession, user_id: str, transaction_id: str):
        try:

            user = await UserRepository.get_user(db, user_id)

            transaction = await TransactionRepository.get_transaction(db, transaction_id)

            admin_reward = 95.0 # admin share

            # admin distribution
            # created admin distribution transaction
            admin_transaction = TransactionDetails(
                transaction_id = f"TRX{uuid4().hex}",
                sender_id = user_id,
                receiver_id = config("TW_MOTHERWALLET"),
                amount = admin_reward,
                currency = "peso",
                transaction_type = "debit",
                title = "Admin Distribution",
                description = f"Admin distribution for account activation by user {user_id}",
                #sender_name=f"{str(mask_name({user.first_name} {user.last_name}}))",
                sender_name = f"{str(mask_name({user.first_name}+ " " +{user.last_name}))}",
                receiver_name = "Admin",
                status = "Completed",
                transaction_reference = f"ADMIN-{transaction.transaction_reference}",
            )


            await TransactionRepository.create_transaction(db, admin_transaction)


        except Exception as e:
            raise HTTPException(
                status_code = 400,
                details = f"Error creating admin distribution: {str(e)}"
            )
        
        

        









