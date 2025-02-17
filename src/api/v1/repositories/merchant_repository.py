from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models.merchant_model import Merchant, MerchantDetails
from uuid import uuid4
from models.user_model import User
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import delete, update
from sqlalchemy.exc import IntegrityError
from utils.responses import json_response

from api.v1.repositories.authentication_repository import AuthenticationRepository
from api.v1.services.otp_service import OTPService
from api.v1.schemas.authentication_schema import LoginRequest

from api.v1.services.otp_service import OTPService


from core.security import sign_jwt

from models.user_model import UserWallet, UserWalletExtension
from models.referral_model import MerchantReferral
from api.v1.repositories.user_repository import UserRepository
from models.wallet_model import Wallet

from api.v1.repositories.referral_repository import ReferralRepository


class MerchantRepository:

    @staticmethod
    async def get_all_merchants(db: AsyncSession):
        try:
            result = await db.execute(
                select(Merchant).options(
                    #load related merchant details
                    (selectinload(Merchant.merchant_details)) 
                )

            )

            merchants = result.scalars().all()

            return merchants
        except Exception as e:
            raise e


    @staticmethod
    async def create_merchant(db: AsyncSession, merchant_data_dict: dict):
        try:
            # Create and add the merchant
            merchant = Merchant(
                #merchant_id = str(uuid4()),
                **merchant_data_dict
            )
            db.add(merchant)

            await db.commit()
            await db.refresh(merchant)

            return merchant
        
        except IntegrityError as e:
            await db.rollback()
            if "UNIQUE constraint failed" in str(e):
                return json_response(
                    message = "Merchant already exists with the given details",
                    status_code = 400
                )
            return json_response(
                message= f"Error creating merchant: {str(e)}",
                    status_code=500
            )

        except Exception as e:
            await db.rollback()
            return json_response(
                message=f"Unexpected error creating merchant: {str(e)}",
                status_code=500
            )

        
    @staticmethod
    async def get_merchant(db: AsyncSession, merchant_id: str):
        result = await db.execute(
            select(Merchant).filter(Merchant.merchant_id == merchant_id).options(
                selectinload(Merchant.merchant_details)
            )
        )

        merchant = result.scalars().first()

        return merchant
    
    @staticmethod
    async def update_merchant_wallet(db: AsyncSession, merchant_id: str, additional_amount: float):
        try:
            # Step 1: Fetch the merchant
            result = await db.execute(
                select(Merchant).where(Merchant.merchant_id == merchant_id)
            )
            merchant = result.scalars().first()

            if not merchant:
                raise HTTPException(status_code=404, detail="Merchant not found")

            # Step 2: Calculate new wallet balance
            new_wallet_balance = merchant.merchant_wallet + additional_amount

            # Step 3: Update the merchant_wallet field
            stmt = (
                update(Merchant)
                .where(Merchant.merchant_id == merchant_id)
                .values(merchant_wallet=new_wallet_balance)
            )

            await db.execute(stmt)
            await db.commit()

            return {
                "merchant_id": merchant_id,
                "new_wallet_balance": float(new_wallet_balance),  # Convert Decimal to float for JSON response
                "message": "Merchant wallet updated successfully"
            }

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"Error updating merchant wallet: {str(e)}")

    
    @staticmethod
    async def get_merchant_external_id_discount(db: AsyncSession, merchant_id: str):
        try:
            # Retrieve both external_id and merchant discount
            result = await db.execute(
                select(
                    UserWalletExtension.external_id,
                    Merchant.discount  # Adjust this based on the actual column name for discount
                )
                .join(UserWallet, UserWallet.wallet_id == UserWalletExtension.wallet_id)
                .join(User, User.user_id == UserWallet.user_id)
                .join(Merchant, Merchant.mobile_number == User.mobile_number)
                .where(Merchant.merchant_id == merchant_id)
            )

            # Retrieve both external_id and merchant_discount as a tuple
            merchant_details = result.fetchone()  # Returns a tuple (external_id, discount)

            if merchant_details:
                external_id, discount = merchant_details
                return external_id, discount  # Return both the external_id and discount
            else:
                return None, None  # If no results are found

        except Exception as e:
            raise e



    @staticmethod
    async def get_merchant_referrer_reward_points(session: AsyncSession, merchant_id: str):
        result = await session.execute(
            select(Wallet.reward_points)
            .join(UserWallet, Wallet.wallet_id == UserWallet.wallet_id)
            .join(User, User.user_id == UserWallet.user_id)
            .join(MerchantReferral, MerchantReferral.referred_by == User.referral_id)  # Match user's referral_id
            .filter(MerchantReferral.referred_to == merchant_id)
        )
        reward_points = result.scalar()
        return reward_points
    

    @staticmethod
    async def get_merchant_referrer_reward_points2(db: AsyncSession, merchant_id: str):
        result = await db.execute(
            select(Wallet.reward_points)
            .join(UserWallet, Wallet.wallet_id == UserWallet.wallet_id)
            .join(User, User.user_id == UserWallet.user_id)
            .join(MerchantReferral, MerchantReferral.referred_by == User.referral_id)  # Match user's referral_id
            .filter(MerchantReferral.referred_to == merchant_id)
        )
        reward_points = result.scalar()
        return reward_points



    @staticmethod
    async def update_merchant_referrer_reward_points(db: AsyncSession, merchant_id: str, new_reward_points: float):
        try:
            # Fetch referrer ID
            referral = await db.execute(
                select(MerchantReferral).filter(MerchantReferral.referred_to == merchant_id)
            )
            referral = referral.scalar_one_or_none()
            if not referral:
                raise HTTPException(status_code=404, detail="Merchant referral not found.")

            referrer_id = referral.referred_by
            user = await UserRepository.get_user_by_referral_id(db, referrer_id)
            user_id = user.user_id
            print(f"Merchant referrer user id: {user_id}")

            # Fetch wallet ID for referrer
            result_wallet = await db.execute(
                select(UserWallet.wallet_id).where(UserWallet.user_id == user_id)
            )

            wallet_id = result_wallet.scalar_one_or_none()
            print("Merchant referrer wallet_id: ", wallet_id)
            if not wallet_id:
                raise HTTPException(status_code=404, detail="Wallet not found for merchant referrer")

            result = await db.execute(
                select(Wallet.reward_points)
                .where(Wallet.wallet_id == wallet_id)
            )
            current_reward_points = result.scalar_one_or_none() or 0  # Default to 0 if None

            # **Fix: Add instead of overwrite**
            stmt = (
                update(Wallet)
                .where(Wallet.wallet_id == wallet_id)
                .values(reward_points=current_reward_points + new_reward_points)  # ✅ Accumulate
            )

            await db.execute(stmt)
            await db.commit()

            return {"message": "Merchant referrer reward points updated successfully", "reward_points": new_reward_points, "user_id": user_id}

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error updating merchant referrer reward points: {str(e)}")



    async def get_merchant_reward_points(db: AsyncSession, merchant_id: str):
        result = await db.execute(
            select(Wallet.reward_points)
            .join(UserWallet, Wallet.wallet_id == UserWallet.wallet_id)
            .join(User, User.user_id == UserWallet.user_id)
            .join(Merchant, Merchant.mobile_number == User.mobile_number)  # Match merchant user
            .filter(Merchant.merchant_id == merchant_id)
        )
        merchant_reward_points = result.scalar()
        return merchant_reward_points

    @staticmethod
    async def get_merchant_direct_referrer_reward_points(db: AsyncSession, merchant_id: str):
        try:
            # Step 1: Get the user associated with the merchant
            result = await db.execute(
                select(User.user_id)
                .join(Merchant, Merchant.mobile_number == User.mobile_number)
                .where(Merchant.merchant_id == merchant_id)
            )
            user_id = result.scalar_one_or_none()
            print(f"Merchant user id: {user_id}")

            if not user_id:
                raise HTTPException(status_code=404, detail="User for merchant not found")

            # Step 2: Get the referrer (who referred this user)
            referrer_id = await ReferralRepository.get_referral(db, user_id)
            print(f"Merchant referrer id: {referrer_id}")
            if not referrer_id:
                raise HTTPException(status_code=404, detail="Referrer not found for this user")

            # Step 3: Get the referrer's wallet reward points
            result = await db.execute(
                select(Wallet.reward_points)
                .join(UserWallet, UserWallet.wallet_id == Wallet.wallet_id)
                .where(UserWallet.user_id == referrer_id)
            )
            referrer_reward_points = result.scalar_one_or_none()

            if referrer_reward_points is None:
                referrer_reward_points = 0  # Default to 0 if no reward points

            return referrer_reward_points

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error fetching merchant referrer reward points: {str(e)}")
        


    @staticmethod
    async def update_merchant_direct_referrer_reward_points(db: AsyncSession, merchant_id: str, new_reward_points: float):
        try:
            # Step 1: Get the user associated with the merchant
            result = await db.execute(
                select(User.user_id)
                .join(Merchant, Merchant.mobile_number == User.mobile_number)
                .where(Merchant.merchant_id == merchant_id)
            )
            user_id = result.scalar_one_or_none()

            print("Merchant direct referrer user ID:", user_id)

            if not user_id:
                raise HTTPException(status_code=404, detail="User for merchant not found")

            # Step 2: Get the referrer
            referrer_id = await ReferralRepository.get_referral(db, user_id)
            print(f"Merchant referrer ID: {referrer_id}")

            if not referrer_id:
                raise HTTPException(status_code=404, detail="Referrer not found for this user")

            # Step 3: Get the referrer's wallet ID & current reward points
            result = await db.execute(
                select(Wallet.wallet_id, Wallet.reward_points)
                .join(UserWallet, UserWallet.wallet_id == Wallet.wallet_id)
                .where(UserWallet.user_id == referrer_id)
            )

            wallet_data = result.first()
            if not wallet_data:
                raise HTTPException(status_code=404, detail="Wallet not found for referrer")

            wallet_id, current_points = wallet_data
            current_points = current_points or 0  # Default to 0 if None

            # **Fix: Add new points to existing points correctly**
            updated_reward_points = current_points + new_reward_points

            # Step 4: Update the referrer's reward points
            stmt = (
                update(Wallet)
                .where(Wallet.wallet_id == wallet_id)  # ✅ Use fetched wallet_id
                .values(reward_points=updated_reward_points)
            )

            await db.execute(stmt)
            await db.commit()

            return {
                "referrer_id": referrer_id,
                "reward_points": updated_reward_points,
                "user_id": referrer_id
            }

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"Error updating merchant referrer reward points: {str(e)}")

    @staticmethod
    async def update_merchant_direct_referrer_reward_points2(db: AsyncSession, merchant_id: str, new_reward_points: float):
        try:
            # Step 1: Get the user associated with the merchant
            result = await db.execute(
                select(User.user_id)
                .join(Merchant, Merchant.mobile_number == User.mobile_number)
                .where(Merchant.merchant_id == merchant_id)
            )
            user_id = result.scalar_one_or_none()

            print("Merchant direct referrerrrrr user id: ", user_id)

            if not user_id:
                raise HTTPException(status_code=404, detail="User for merchant not found")

            # Step 2: Get the referrer
            referrer_id = await ReferralRepository.get_referral(db, user_id)
            print(f"Merchant referrer iddd: {referrer_id}")

            if not referrer_id:
                raise HTTPException(status_code=404, detail="Referrer not found for this user")

            # Step 3: Get the referrer's current reward points
            result = await db.execute(
                select(Wallet.reward_points)
                .join(UserWallet, UserWallet.wallet_id == Wallet.wallet_id)
                .where(UserWallet.user_id == referrer_id)
            )
            current_points = result.scalar_one_or_none()

            if current_points is None:
                current_points = 0  # Default to 0 if no existing points

            # Step 4: Calculate new reward points
            new_reward_points = current_points + new_reward_points

            # Step 5: Update the referrer's reward points
            stmt = (
                update(Wallet)
                .where(Wallet.wallet_id == 
                    select(UserWallet.wallet_id)
                    .where(UserWallet.user_id == referrer_id)
                    .scalar_subquery()
                )
                .values(reward_points=new_reward_points)
            )

            await db.execute(stmt)
            await db.commit()

            return {
                "referrer_id": referrer_id,
                "reward_points": new_reward_points,
                "user_id": referrer_id
            }

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"Error updating merchant referrer reward points: {str(e)}")




    @staticmethod
    async def get_merchant_reward_points2(db: AsyncSession, merchant_id: str):
        try:
            # Query to retrieve the reward points of the merchant user from the Wallet table
            result = await db.execute(
                select(
                    Wallet.reward_points  # Select reward_points from Wallet
                )
                .join(User, User.mobile_number == Merchant.mobile_number)  # Join Merchant with User to get the user
                .join(UserWallet, UserWallet.user_id == User.user_id)  # Join UserWallet to get the user_wallet
                .join(Wallet, Wallet.wallet_id == UserWallet.wallet_id)  # Join Wallet to get the reward_points
                .where(Merchant.merchant_id == merchant_id)  # Filter by merchant_id
            )

            # Retrieve the reward points of the merchant's user
            reward_points = result.scalar_one_or_none()

            if reward_points is None:
                raise HTTPException(status_code=404, detail="User wallet not found for the merchant")

            return reward_points

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error fetching merchant reward points: {str(e)}")


    @staticmethod
    async def update_merchant_reward_points(db: AsyncSession, merchant_id: str, new_reward_points: float):
        try:
            # Fetch merchant user_id
            result = await db.execute(
                select(User.user_id)
                .join(Merchant, Merchant.mobile_number == User.mobile_number)
                .where(Merchant.merchant_id == merchant_id)
            )

            merchant_user_id = result.scalar_one_or_none()
            if not merchant_user_id:
                raise HTTPException(status_code=404, detail="Merchant user not found")

            # Fetch wallet ID
            result_wallet = await db.execute(
                select(UserWallet.wallet_id)
                .where(UserWallet.user_id == merchant_user_id)
            )

            wallet_id = result_wallet.scalar_one_or_none()
            if not wallet_id:
                raise HTTPException(status_code=404, detail="Wallet not found for the merchant")

            result = await db.execute(
                select(Wallet.reward_points)
                .where(Wallet.wallet_id == wallet_id)
            )
            current_reward_points = result.scalar_one_or_none() or 0  # Default to 0 if None

            # **Fix: Add instead of overwrite**
            stmt = (
                update(Wallet)
                .where(Wallet.wallet_id == wallet_id)
                .values(reward_points=current_reward_points + new_reward_points)  # ✅ Accumulate
            )
            await db.execute(stmt)
            await db.commit()

            return {"message": "Merchant reward points updated successfully", "reward_points": new_reward_points}

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error updating merchant reward points: {str(e)}")
        
        
    @staticmethod
    async def update_merchant(db: AsyncSession, merchant_id: str, merchant_data: dict, merchant_details_data: list = None):
        try:
            result = await db.execute(select(Merchant).filter(Merchant.merchant_id == merchant_id))
            merchant = result.scalars().first()
            if not merchant:
                raise HTTPException(status_code=404, detail="Merchant not found")
            
            for key, value in merchant_data.items():
                if value is not None:
                    setattr(merchant, key, value)

            await db.commit()


            if merchant_details_data:
                await MerchantRepository.update_merchant_details(db, merchant_id, merchant_details_data)

            return merchant
        
        except Exception as e:
            await db.rollback()
            raise e
        
    @staticmethod
    async def update_merchant_details(db: AsyncSession, merchant_id: str, merchant_details_data: list):
        try:
            result = await db.execute(select(Merchant).filter(Merchant.merchant_id == merchant_id))

            merchant = result.scalars().first()
            if not merchant:
                raise HTTPException(status_code=404, detail="Merchant not found")

            for detail in merchant_details_data:
                merchant_detail = MerchantDetails(merchant_id=merchant.merchant_id, **detail)
                db.add(merchant_detail)

            await db.commit()

            return merchant

        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def delete_merchant(db: AsyncSession, merchant_id: str):
        try:
            # Fetch the existing merchant by ID
            result = await db.execute(select(Merchant).filter(Merchant.merchant_id == merchant_id))
            merchant = result.scalars().first()
            
            if not merchant:
                raise HTTPException(status_code=404, detail="Merchant not found")
            
            # Delete all associated merchant details
            await db.execute(
                delete(MerchantDetails).where(MerchantDetails.merchant_id == merchant_id)
            )
            
            # Now delete the merchant
            await db.execute(
                delete(Merchant).where(Merchant.merchant_id == merchant_id)
            )
            
           
            await db.commit()

            return {"status": "success", "message": "Merchant and its details deleted successfully"}
        
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        



    @staticmethod
    async def initiate_login(db: AsyncSession, mobile_number: str):
        try: 
            user = await AuthenticationRepository.get_user_by_mobile_number(db, mobile_number)

            if user:
                otp_response = await OTPService.create_otp(db, mobile_number, otp_type="login")

                return json_response(
                    message = "OTP sent successfully",
                    data = {
                        "otp_code": otp_response.otp_code,
                        "expired_at": otp_response.expired_at.isoformat()
                    }
                )
            
            else:
                return json_response(
                    message = "user not found!",
                    data = {
                        "mobile_number": mobile_number
                    },
                    status_code=404
                )
            
        except Exception as e:
            raise e






        except Exception as e:
            raise e
        

    @staticmethod
    async def process_login(db: AsyncSession, data: LoginRequest, otp_code: str):

        mobile_number = data.mobile_number


        user = await AuthenticationRepository.get_user_by_mobile_number(db, mobile_number)

        is_valid_otp = await OTPService(db, mobile_number, otp_code)

        if is_valid_otp:
            access_token = sign_jwt(user.user_id)['access_token']

            return json_response(
                message = "You have sucessfully logged in!",
                data = {
                    "access_token": access_token,
                    "bearer": "bearer"
                },
                status_code=200
            )
        else:
            return json_response(
                message = "Invalid or expired OTP",
                status_code=400
            )











































