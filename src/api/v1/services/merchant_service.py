from api.v1.repositories.merchant_repository import MerchantRepository
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.schemas.merchant_schema import MerchantCreate, MerchantUpdate, MerchantDetailsResponse, MerchantResponse
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from utils.responses import json_response
from uuid import uuid4
from datetime import datetime
from models.merchant_model import Merchant, MerchantDetails
from sqlalchemy import select
from typing import List
from sqlalchemy import delete  # Import the delete function
from sqlalchemy.exc import IntegrityError
from utils.responses import datetime_to_str
from models.referral_model import MerchantReferral
from api.v1.repositories.referral_repository import ReferralRepository
from fastapi.encoders import jsonable_encoder

import qrcode
from io import BytesIO
import base64


from api.v1.repositories.kyc_repository import KYCRepository
from api.v1.repositories.transaction_repository import TransactionRepository
from api.v1.repositories.merchant_repository import MerchantRepository
import httpx
from decouple import config 

from api.v1.repositories.community_repository import CommunityRepository
from api.v1.repositories.hub_repository import HubRepository
from api.v1.repositories.investor_repository import InvestorRepository
from api.v1.services.reward_distribution_service import RewardService

class MerchantService:  


    @staticmethod
    async def get_all_merchant_service(db: AsyncSession):
        try:
            merchants = await MerchantRepository.get_all_merchants(db)

            merchant_list = [
                MerchantResponse(
                    merchant_id=merchant.merchant_id,
                    mobile_number=merchant.mobile_number,
                    discount = merchant.discount,

                    business_name=merchant.business_name,
                    business_type=merchant.business_type,

                    status=merchant.status,
                    merchant_details=[
                        MerchantDetailsResponse(
                            latitude=detail.latitude,
                            longitude=detail.longitude,

                            contact_number=detail.contact_number,
                            business_email=detail.business_email,

                            region=detail.region,
                            province=detail.province,
                            municipality_city=detail.municipality_city,
                            barangay=detail.barangay,
                            street=detail.street,

                            created_at=detail.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                            updated_at=detail.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                        )
                        for detail in merchant.merchant_details
                    ],
                    created_at=merchant.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    updated_at=merchant.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                ).dict()  
                for merchant in merchants
            ]

            return json_response(
                message = "Merchants Retrieved Successfully",
                data = merchant_list,
                status_code = 200
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving merchants: {str(e)}")


    @staticmethod
    async def create_merchant_service(db: AsyncSession, merchant_data: MerchantCreate, referral_id: str):
        try:

            # change referrer_id to user_sponsor_id
            
            merchant_data = merchant_data.dict()
            merchant_data['merchant_id'] = str(uuid4())

            merchant_details_data = merchant_data.pop('merchant_details', None)

            #async with db.begin():
            merchant = await MerchantRepository.create_merchant(db, merchant_data)

            
            print(f"Merchant result: {merchant}")
            print(f"Merchant details data: {merchant_details_data}")
            print(f"Merchant ID: {merchant_data['merchant_id']}")


            if merchant:
                if merchant_details_data:
                    merchant_details = MerchantDetails(
                            merchant_id = merchant_data['merchant_id'], 
                            **merchant_details_data
                    )
                    db.add(merchant_details)

                    print(f"Referrer ID: {referral_id}")
                   
                    merchant_referral = MerchantReferral(
                        referral_id=str(uuid4()), 
                        referred_by=referral_id,
                        referred_to=merchant_data['merchant_id']  
                    )

                    db.add(merchant_referral)
                    
                    # Generate QR code for the merchant
                    qr_content = merchant_data['merchant_id']
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(qr_content)
                    qr.make(fit=True)

                    img = qr.make_image(fill_color="black", back_color="white")
                    buffered = BytesIO()
                    img.save(buffered, format="PNG")
                    qr_code_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

                    merchant.qr_code_url = qr_code_base64

                    
                    db.add(merchant)
        

            await db.commit()
            await db.refresh(merchant)

            print(f"Returning response for Merchant: {merchant}")

            return json_response(
                message="Merchant Created Successfully",
                status_code=200
            )

        except IntegrityError as e:
            await db.rollback()  
            
            if "UNIQUE constraint failed" in str(e):
                return json_response(
                    message="Merchant already exists with the given details",
                    status_code=400
                )
            return json_response(
                message=f"Database integrity error: {str(e)}",
                status_code=400
            )
        except Exception as e:
            await db.rollback()  
            return json_response(
                message=f"Error creating merchant: {str(e)}",
                status_code=400
            )


    @staticmethod
    async def get_merchant_service(db: AsyncSession, merchant_id: str):
        try:
            merchant = await MerchantRepository.get_merchant(db, merchant_id)

            if not merchant:
                raise HTTPException(status_code=404, detail="Merchant not found")

            merchant_data = {
                "merchant_id": merchant.merchant_id,
                "mobile_number": merchant.mobile_number,
                "business_name": merchant.business_name,
                "business_type": merchant.business_type,
                "discount": merchant.discount,
                "status": merchant.status,
                "merchant_details": [
                    {
                        "latitude": detail.latitude,
                        "longitude": detail.longitude,
                        "contact_number": detail.contact_number,
                        "business_email": detail.business_email,
                        "region": detail.region,
                        "province": detail.province,
                        "municipality_city": detail.municipality_city,
                        "barangay": detail.barangay,
                        "street": detail.street,
                        # "merchant_address": detail.merchant_address,
                    }

                    for detail in merchant.merchant_details
                ],
            }

            return merchant_data

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving merchant: {str(e)}")


    @staticmethod
    async def update_merchant_service(db: AsyncSession, merchant_id: str, merchant_update_data: MerchantUpdate):
        try:
            # Fetch the existing merchant by ID
            result = await db.execute(select(Merchant).filter(Merchant.merchant_id == merchant_id))
            merchant = result.scalars().first()
            
            if not merchant:
                raise HTTPException(status_code=404, detail="Merchant not found")

            if merchant_update_data.status is not None:
                merchant.status = merchant_update_data.status
            
            await db.commit()

            if merchant_update_data.merchant_details:
                await db.execute(
                    delete(MerchantDetails).where(MerchantDetails.merchant_id == merchant_id)
                )
                
                for detail in merchant_update_data.merchant_details:
                    merchant_detail = MerchantDetails(
                        merchant_id=merchant.merchant_id, 
                        **detail.dict(exclude_unset=True)  # Exclude unset fields
                    )
                    db.add(merchant_detail)
                
                # Commit the changes to the merchant details
                await db.commit()

            return json_response(
                message="Merchant Updated Successfully",
                status_code=200

            )
        
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        
    @staticmethod
    async def delete_merchant_service(db: AsyncSession, merchant_id: str):
        if not await MerchantRepository.delete_merchant(db, merchant_id):
            raise HTTPException(status_code=404, detail="Merchant not found")
        return json_response(
            message = "Merchant Deleted Successfully",
            data = {"merchant_id": merchant_id},
            status_code=200
        )
    



    @staticmethod
    async def initiate_merchant_purchase(db: AsyncSession, amount: float, merchant_id: str, user_id: str):
        try:
            user = await KYCRepository.get_user(db, user_id)

            user_external_id = user.external_id
            if not user_external_id:
                raise HTTPException(status_code=404, detail="User not found")

            # get merchant external id and discount
            merchant_external_id, merchant_discount = await MerchantRepository.get_merchant_external_id_discount(db, merchant_id)
            print(f"Merchant External ID: {merchant_external_id}, Discount: {merchant_discount}")

            if not merchant_external_id:
                raise HTTPException(status_code=404, detail="Merchant not found")
            
            # Calculate the discounted amount
            discount_amount = amount * (merchant_discount / 100)  # Discount as a percentage
            discounted_total = amount - discount_amount  # Total after discount

            # Calculate the amounts for merchant and admin based on the merchant's discount
            admin_amount = discounted_total * (merchant_discount / 100)  # Admin gets the merchant's discount
            merchant_amount = discounted_total - admin_amount  # The remaining amount goes to the merchant


            #   user_data = await TransactionRepository.get_user_details(db, user_id)

            hub_id = 'hub'
            investor_id = 'investor'


            await RewardService.distribute_rewards_main(db, admin_amount, user_id, hub_id, investor_id, merchant_id)

            #community_reward = await CommunityRepository.get_community_leader_reward_points(db, user_id)
            #print(f"Community reward: {community_reward}")

            # inject hub ID
            #hub_reward = await HubRepository.get_hub_user_reward_points(db, hub_id)
            #print(f"Hub reward: {hub_reward}")

            # inject investor ID
            #investor = await InvestorRepository.get_investor_user_reward_points(db, investor_id)
            #rint(f"Investor reward: {investor}")



            # Proceed with payment processing
            async with httpx.AsyncClient() as client:
                # Initiate transfer to the merchant
                transfer_payload_merchant = {
                    "from_user": user_external_id,
                    "to_user": merchant_external_id,
                    "amount": merchant_amount,
                    "coin": "peso",
                }

                transfer_payload_admin = {
                    "from_user": user_external_id,
                    "to_user": config('TW_MOTHERWALLET'),
                    "amount": admin_amount,
                    "coin": "peso",
                }

                response_merchant = await client.post(
                    url=f"{config('TW_API_URL')}/b2bapi/initiate_p2ptransfer",
                    headers={
                        "apikey": config('TW_API_KEY'),
                        "secretkey": config("TW_SECRET_KEY"),
                    },
                    json=transfer_payload_merchant
                )
                if response_merchant.status_code != 200:
                    raise HTTPException(status_code=500, detail="Merchant transfer initiation failed")
                
                # Initiate transfer to the admin
                response_admin = await client.post(
                    url=f"{config('TW_API_URL')}/b2bapi/initiate_p2ptransfer",
                    headers={
                        "apikey": config('TW_API_KEY'),
                        "secretkey": config("TW_SECRET_KEY"),
                    },
                    json=transfer_payload_admin
                )
                if response_admin.status_code != 200:
                    raise HTTPException(status_code=500, detail="Admin transfer initiation failed")


                # Process both transfers
                transaction_merchant = response_merchant.json()
                transaction_admin = response_admin.json()

                # Process merchant transaction
                response_merchant_process = await client.post(
                    url=f"{config('TW_API_URL')}/b2bapi/process_p2ptransfer",
                    headers={
                        "apikey": config('TW_API_KEY'),
                        "secretkey": config("TW_SECRET_KEY"),
                    },
                    json={
                        "Transaction_id": transaction_merchant['transaction_reference'],
                        #"otp": "example_otp_code",  # Use actual OTP if needed
                    }
                )

                # Process admin transaction
                response_admin_process = await client.post(
                    url=f"{config('TW_API_URL')}/b2bapi/process_p2ptransfer",
                    headers={
                        "apikey": config('TW_API_KEY'),
                        "secretkey": config("TW_SECRET_KEY"),
                    },
                    json={
                        "Transaction_id": transaction_admin['transaction_reference'],
                        #"otp": "example_otp_code",  # Use actual OTP if needed
                    }
                )


            # Return success message
            return json_response(
                message="Merchant purchase and admin commission successfully processed.",
                status_code=200,
                data={
                    "merchant_payment": response_merchant_process.json(),
                    "admin_payment": response_admin_process.json(),
                }
            )


        except HTTPException as http_error:
            return json_response(message=str(http_error.detail), status_code=http_error.status_code)


        except Exception as e:
            return json_response(
                message=f"Error initiating merchant purchase: {str(e)}",
                status_code=400
            )

        


'''
    @staticmethod
    async def create_merchant_service(db: AsyncSession, merchant_data: MerchantCreate, referrer_id: str):
        try:
            merchant_data_dict = merchant_data.dict()
            merchant_data_dict['merchant_id'] = str(uuid4())

            # Extract merchant details if present
            merchant_details = merchant_data_dict.pop('merchant_details', None)

            async with db.begin():  # Start a transaction
                # Create the merchant
                merchant = await MerchantRepository.create_merchant(db, merchant_data_dict)

                # Create merchant details if provided
                if merchant_details:
                    merchant_details = MerchantDetails(
                        merchant_id=merchant.merchant_id, **merchant_details
                    )
                    db.add(merchant_details)

                # Create the merchant referral
                await ReferralRepository.create_merchant_referral(
                    db,
                    referred_by=referrer_id,
                    referred_to=merchant.mobile_number
                )

            # Commit the transaction
            await db.commit()
            await db.refresh(merchant)

            return json_response(
                message="Merchant Created Successfully",
                data={
                    "merchant_id": merchant.merchant_id,
                    "user_id": merchant.merchant_id
                },
                status_code=200
            )

        except IntegrityError as e:
            await db.rollback()  # Rollback the transaction in case of error
            # Check if the error is related to a specific duplicate entry (e.g., unique constraint violation)
            if "UNIQUE constraint failed" in str(e):
                return json_response(
                    message="Merchant already exists with the given details",
                    status_code=400
                )
            return json_response(
                message=f"Database integrity error: {str(e)}",
                status_code=400
            )
        except Exception as e:
            await db.rollback()  # Rollback the transaction in case of error
            return json_response(
                message=f"Error creating merchant: {str(e)}",
                status_code=400
            )

    @staticmethod
    async def create_merchant(db: AsyncSession, merchant_data_dict: dict):
        try:
            # Create and add the merchant
            merchant = Merchant(**merchant_data_dict)
            db.add(merchant)

            await db.commit()  # Commit transaction
            await db.refresh(merchant)

            return merchant
        except IntegrityError as e:
            await db.rollback()
            if "UNIQUE constraint failed" in str(e):
                return json_response(
                    message="Merchant already exists with the given details",
                    status_code=400
                )
            return json_response(
                message=f"Error creating merchant: {str(e)}",
                    status_code=500
            )
        except Exception as e:
            await db.rollback()
            return json_response(
                message=f"Unexpected error creating merchant: {str(e)}",
                status_code=500
            )

    @staticmethod
    async def create_merchant_referral(db: AsyncSession, referred_by: str, referred_to: str) -> MerchantReferral:
        try:
            # Retrieve the user and merchant
            user = await db.execute(select(User).filter(User.user_id == referred_by))
            user = user.scalars().first()

            merchant = await db.execute(select(Merchant).filter(Merchant.mobile_number == referred_to))
            merchant = merchant.scalars().first()

            if not user or not merchant:
                return json_response(
                    message="User or Merchant not found",
                    status_code=404
                )

            # Create merchant referral
            merchant_referral = MerchantReferral(
                referral_id=str(uuid4()),  # Generate a unique referral ID
                referred_by=referred_by,
                referred_to=merchant.merchant_id
            )

            db.add(merchant_referral)
            await db.commit()
            await db.refresh(merchant_referral)

            return merchant_referral

        except IntegrityError as e:
            await db.rollback()
            if "UNIQUE constraint failed" in str(e):
                return json_response(
                    message="Referral already exists for this merchant",
                    status_code=400
                )
            return json_response(
                message=f"Database integrity error while creating referral: {str(e)}",
                status_code=400
            )
        except Exception as e:
            await db.rollback()
            return json_response(
                message=f"Unexpected error creating Merchant referral: {str(e)}",
                status_code=400
            )


'''