from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from utils.responses import json_response
from api.v1.repositories.user_repository import UserRepository
from models.user_model import UserDetail, UserWallet, UserWalletExtension
from api.v1.schemas.user_schema import UserCreate, UserUpdate, UserResponse, UserAddressCreate, UserDetailCreate, ProcessAccountInput, ProcessMemberActivation, InitiateMemberActivation, UserDetailSchema, MemberSchema, MemberAddressSchema
from uuid import uuid4
from core.security import hash_password
from decouple import config
import httpx

from api.v1.repositories.wallet_repository import WalletRepository
from api.v1.repositories.kyc_repository import KYCRepository
from api.v1.repositories.transaction_repository import TransactionRepository
from models.transaction_model import Transaction
from api.v1.services.referral_service import ReferralService
from models.wallet_model import Wallet
from api.v1.schemas.referral_schema import ReferralCreate   

from utils.extra import mask_name

from api.v1.services.unilevel_services import UnilevelService
from api.v1.services.commission_service import CommissionService
from api.v1.schemas.transaction_schema import TransactionDetails
from api.v1.services.referral_service import ReferralService
from api.v1.repositories.referral_repository import ReferralRepository
from models.activation_history_model import ActivationHistory

from api.v1.repositories.account_activation_repository import ActivationHistoryRepository
from typing import List

from api.v1.schemas.reward_schema import RewardInput

from api.v1.repositories.reward_distribution_repository import RewardDistributionRepository
from uuid import uuid4

def datetime_to_str(dt: datetime) -> str:
 
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)


class UserService:


    @staticmethod
    async def get_member_info(db: AsyncSession, user_id: str):
        return await UserRepository.get_member_info(db, user_id)
    



    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate, referral_code: str = None):
        try:

            referral_id = str(uuid4())

            user_data = user_data.dict()
            user_data["user_id"] = str(uuid4()) 
            user_data["referral_id"] = referral_id[:8]
            user_data["hashed_password"] = hash_password(user_data["password"])  
            user_data.pop("password", None)  

            address_data = user_data.pop("user_address", None)  
            details_data = user_data.pop("user_details", None)  


            # create the user
            user = await UserRepository.create_user(db, user_data, address_data, details_data)
            print(f"User created: {user}")  
            

            # create wallet for the user
            wallet =  Wallet(wallet_id=str(uuid4()), public_address=str(uuid4().hex))
            print(f"Wallet ID: {wallet.wallet_id}")
            db.add(wallet)
            await db.commit()
            await db.refresh(wallet)

            # link user to the wallet
            user_wallet = UserWallet(user_id=user_data['user_id'], wallet_id=wallet.wallet_id, is_primary=True)
            db.add(user_wallet)
            await db.commit()

            # TopWallet API
            async with httpx.AsyncClient() as client:
                # Send data to TopWallet API
                payload = {
                    "member_name": f"{details_data['first_name']} {details_data['last_name']}",
                    "phone": user_data["mobile_number"],
                    "member_email": user_data["email_address"],
                    "dob": "01/01/2000",
                    "address": {
                        "region": address_data["region"],
                        "province": address_data["province"],
                        "city": address_data["city"],
                        "houseno": address_data["house_number"],
                        "barangay": address_data["barangay"],
                        "user_politician": address_data.get("user_politician", "false"),
                        "user_familymember_politician": address_data.get("user_familymember_politician", "false"),
                    },
                }

                headers = {
                    "apikey": config('TW_API_KEY'),
                    "secretkey": config("TW_SECRET_KEY"),
                }

                response = await client.post(
                    url = f"{config('TW_API_URL')}/b2bapi/user_on_board",
                    json=payload,
                    headers=headers,
                )

                if response.status_code != 200:
                    # Log the response for debugging purposes
                    print(f"TopWallet API response: {response.text}")
                    response_data = response.json() if response.content else {}
                    await db.rollback()
                    return json_response(
                        message="Failed to onboard user to TopWallet",
                        data=response_data,
                        status_code=response.status_code,
                    )

                # Extract external ID from the response
                response_data = response.json()
                external_id = response_data.get("userid")

                if not external_id:
                    raise HTTPException(status_code=400, detail="External ID not received from TopWallet")

            # Link external ID to user's wallet extension
            extension_name = "TopWallet"
            user_wallet_extension = await WalletRepository().get_wallet_extension(db, extension_name)
            print("User Wallet Extension:", user_wallet_extension)
            extension_id = user_wallet_extension.wallet_extension_id
            print("Extension ID:", extension_id)

            user_wallet_extension = UserWalletExtension(
                user_wallet_extension_id=str(uuid4()),
                extension_id=extension_id,
                wallet_id=user_wallet.wallet_id,
                external_id=external_id,
            )

            db.add(user_wallet_extension)
            await db.commit()
            await db.refresh(user_wallet_extension)


         
            #referral = await ReferralRepository.create_referral(db, referred_by=referral_code, referred_to=user_data['user_id'])
            ##if referral:
            #   print("referral_object", referral)
            ##else:
            #    print("referral_object_failed")


            return json_response(
                message="User created successfully and onboarded to TopWallet",
                data={
                    "user_id": user_data['user_id'],
                    "TopWallet ID": external_id
                },
                status_code=201,
            )

        except Exception as e:
            await db.rollback()
            print(f"Error creating user: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error creating user: {str(e)}")




    @staticmethod
    async def get_user(db: AsyncSession, user_id: str):

        user = await UserRepository.get_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user_address = UserAddressCreate.from_orm(user.user_address) if user.user_address else None
        user_details = UserDetailCreate.from_orm(user.user_details) if user.user_details else None

        user_wallets = []
        for user_wallet in user.user_wallets:
            wallet = user_wallet.wallets[0]
            user_wallets.append({"wallet_id": wallet.wallet_id, "public_address": wallet.public_address})

        return json_response(
            message="User fetched successfully",
            data=UserResponse(
                user_id=user.user_id,
                mobile_number=user.mobile_number,
                #email_address=user.email_address,
                status=user.status,
                created_at=user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                updated_at=user.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                user_address=user_address,
                user_details=user_details,
                user_wallets=user_wallets
            ).dict()
        )

    @staticmethod
    async def get_all_users(db: AsyncSession):
        """
        Fetches all users, including their address, details, and wallet.

        Args:
            db (AsyncSession): The database session.

        Returns:
            JSON response containing the list of users.
        """
        users = await UserRepository.get_all_users(db)
        if not users:
            raise HTTPException(status_code=404, detail="No users found")

        user_responses = []
        for user in users:
            user_address = UserAddressCreate.from_orm(user.user_address) if user.user_address else None
            user_details = UserDetailCreate.from_orm(user.user_details) if user.user_details else None

            user_wallets = []
            for user_wallet in user.user_wallets:
                wallet = user_wallet.wallets[0]
                user_wallets.append({"wallet_id": wallet.wallet_id, "public_address": wallet.public_address})

            user_responses.append(
                UserResponse(
                    user_id=user.user_id,
                    mobile_number=user.mobile_number,
                    email_address=user.email_address,
                    status=user.status,
                    created_at=user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    updated_at=user.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                    user_address=user_address,
                    user_details=user_details,
                    user_wallets=user_wallets
                ).dict()
            )

        return json_response(message="Users fetched successfully", data=user_responses)

    @staticmethod
    async def update_user(db: AsyncSession, user_id: str, user_data: UserUpdate):

        try:
            user_data_dict = user_data.dict(exclude_unset=True)

            existing_user = await UserRepository.get_user(db, user_id)
            if not existing_user:
                raise HTTPException(status_code=404, detail="User not found")

            for key, value in user_data_dict.items():
                if value is not None and key not in ["user_address", "user_details"]:
                    setattr(existing_user, key, value)

            if 'user_address' in user_data_dict and user_data_dict['user_address']:
                address_data = user_data_dict.pop('user_address')
                await UserRepository.update_user_address(db, user_id, address_data)

            if 'user_details' in user_data_dict and user_data_dict['user_details']:
                details_data = user_data_dict.pop('user_details')

                if existing_user.user_details:
                    for key, value in details_data.items():
                        setattr(existing_user.user_details, key, value)
                else:
                    new_user_detail = UserDetail(user_id=user_id, **details_data)
                    db.add(new_user_detail)

            await db.commit()

            existing_user.created_at = datetime_to_str(existing_user.created_at)
            existing_user.updated_at = datetime_to_str(existing_user.updated_at)

            user_address = UserAddressCreate.from_orm(existing_user.user_address) if existing_user.user_address else None
            user_details = UserDetailCreate.from_orm(existing_user.user_details) if existing_user.user_details else None

            user_wallets = []
            for user_wallet in existing_user.user_wallets:
                wallet = user_wallet.wallets[0]
                user_wallets.append({"wallet_id": wallet.wallet_id, "public_address": wallet.public_address})

            return json_response(
                message="User updated successfully",
                data=UserResponse(
                    user_id=existing_user.user_id,
                    mobile_number=existing_user.mobile_number,
                    email_address=existing_user.email_address,
                    status=existing_user.status,
                    created_at=existing_user.created_at,
                    updated_at=existing_user.updated_at,
                    user_address=user_address,
                    user_details=user_details,
                    user_wallets=user_wallets
                ).dict()
            )

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"Error updating user: {str(e)}")

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: str):

        if not await UserRepository.delete_user(db, user_id):
            raise HTTPException(status_code=404, detail="User not found")

        return json_response(message="User deleted successfully", data={"user_id": user_id})




    @staticmethod
    async def get_user_balancee(db: AsyncSession, user_id: str):
        try:
            user = await KYCRepository.get_user(db, user_id)
            external_id = user.external_id

            print(f"external id: {external_id}")
    
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url = f"{config('TW_API_URL')}/b2bapi/get_profile",
                    headers = {
                        "apikey": config('TW_API_KEY'),
                        "secretkey": config("TW_SECRET_KEY"),
                    },
                    json = {
                        'userid': external_id
                    }
                )


                if response.status_code != 200:
                    try:
                        error_data = response.json()
                    except Exception:
                        error_data = {"message": response.text.strip()}

                    return json_response(
                        message = response.text,
                        data = error_data,
                        status_code=response.status_code
                    )
                else:
                    #data = response.json()
                    return json_response(
                        status_code=200,
                        data = response.json,
                        message = "User balance fetched successfully"
                    )

            #return external_id
        
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error fetching user balance: {str(e)}")


    @staticmethod
    async def initiate_account_activation(db: AsyncSession, user_id: str):
        try:

            user = await KYCRepository.get_user(db, user_id)
            
            external_id = user.external_id

            user_data = await TransactionRepository.get_user_details(db, user_id)


            if not user:
                return json_response(
                    message="Account data not found. Please contact customer service for assistance.",
                    data={"user_id": user_id},
                    status_code = 404
                )
            

            async with httpx.AsyncClient() as client:
                transfer_payload = {
                    "from_user": external_id,
                    "to_user": config("TW_MOTHERWALLET"),
                    "amount": float(150),
                    "coin": "peso"
                }
                response = await client.post(
                    url = f"{config('TW_API_URL')}/b2bapi/initiate_p2ptransfer",
                    headers = {
                        "apikey": config('TW_API_KEY'),
                        "secretkey": config("TW_SECRET_KEY"),
                    },
                    json = transfer_payload
                )

                if response.status_code != 200:
                    try:
                        error_data = response.json()
                    except Exception:
                        error_data = {"message": response.text.strip()}

                    return json_response(
                        message = response.text,
                        data = error_data,
                        status_code=response.status_code
                    )
                
                else:

                    try:
                        transaction = Transaction(
                            transaction_id=f"TRX{str(uuid4().hex)}",
                            sender_id=user_id, # changed external id to user id
                            receiver_id = config("TW_MOTHERWALLET"),
                            amount=float(150),
                            currency = "peso",
                            transaction_type = "debit",
                            title = "Activation",
                            description = f"You have paid {float(150)} pesos for account activation",
                            sender_name = str(mask_name(user_data.first_name + ' ' + user_data.last_name + ".")),
                            receiver_name = config("TW_MOTHERWALLET"),
                            transaction_reference=response.json()['Transaction_id'],
                        )

                        db.add(transaction)
                        await db.commit()
                        await db.refresh(transaction)

                        return json_response(
                            message = "Account activation initiated successfully",
                            data = response.json(), # transaction reference
                            #data = transaction.transaction_id,
                            status_code = 200
                        )   


                    except Exception as e:
                        await db.rollback()
                        return json_response(
                            message = "Error creating transaction",
                            data = str(e),
                            status_code = 500
                        )
            
        except Exception as e:
            return json_response(
                message = "Error activating account",
                data = str(e),
                status_code = 500
            )
        

    @staticmethod
    async def process_account_activation(db: AsyncSession, process_account_data: ProcessAccountInput, user_id: str):
        try:
            # fetch the transaction details
            transaction = await TransactionRepository.get_transaction(db, process_account_data.transaction_reference)
            
            if not transaction:
                return json_response(
                    message="Transaction not found",
                    data={"transaction_reference": process_account_data.transaction_reference},
                    status_code=404
                )

            # processing transaction with TW API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=f"{config('TW_API_URL')}/b2bapi/process_p2ptransfer",
                    headers={
                        "apikey": config('TW_API_KEY'),
                        "secretkey": config("TW_SECRET_KEY"),
                    },
                    json={
                        "Transaction_id": transaction.transaction_reference,
                       # "otp": process_account_data.otp_code
                    }
                )

                # Handle non-200 responses
                if response.status_code != 200:
                    return json_response(
                        message="Error from external API",
                        data={"error": response.text},
                        status_code=response.status_code
                    )

                # check for empty response body
                try:
                    response_data = response.json()
                    
                except ValueError:
                    return json_response(
                        message="Invalid JSON response from external API",
                        data={"response_text": response.text},
                        status_code=500
                    )
                #print("API Response Status Code:", response.status_code)
                #print("API Response JSON:", response_data)


            user = await UserRepository.get_user(db, user_id)
            if not user:
                return json_response(
                    message="User not found",
                    data={"user_id": user_id},
                    status_code=404
                )

            # Update the user's status to active
            user.status = True
            user.is_activated = True
            db.add(user)

            # Mark the transaction as completed
            transaction.status = "Completed"
            db.add(transaction)
            # Trigger unilevel logic and commissions
            #await ReferralService.create_commission(db, referred_to=user_id)
            

            await db.commit()
            await db.refresh(user)

            # account activation reward
            await CommissionService.account_activation_reward(db, user_id, transaction.transaction_id)

            # add admin distribution reward function


            return json_response(
                message="Account activated successfully",
                #data={"user_id": user_id},
                status_code=200
            )
        
        

        except Exception as e:
            await db.rollback()
            return json_response(
                message="Error processing account activation",
                data=str(e),
                status_code=500
            )






    @staticmethod
    async def get_user_upline_service(db: AsyncSession, user_id: str):
        return await UserRepository.get_upline(db, user_id)
    
    @staticmethod
    async def get_user_upline_service(db: AsyncSession, user_id: str):
        upline_data = await UserRepository.get_upline(db, user_id)

        if not upline_data:
            return json_response(
                status_code=404,
                data=None,  # Returning `None` instead of `[]` for consistency
                message="No user or upline found"
            )

        return json_response(
            status_code=200,
            data={
                "user": upline_data.user.model_dump(),  # ✅ Include user details
                "uplines": [user.model_dump() for user in upline_data.uplines]  # ✅ Include downlines
            },
            message="Downlines fetched successfully"
        )
    
    @staticmethod
    async def get_user_downline_service(db: AsyncSession, user_id: str):
        downline_data = await UserRepository.get_downline(db, user_id)

        if not downline_data:
            return json_response(
                status_code=404,
                data=None,  # Returning `None` instead of `[]` for consistency
                message="No user or downlines found"
            )

        return json_response(
            status_code=200,
            data={
                "user": downline_data.user.model_dump(),  # ✅ Include user details
                "downlines": [user.model_dump() for user in downline_data.downlines]  # ✅ Include downlines
            },
            message="Downlines fetched successfully"
        )




    # main -> authenticated user downlines
    @staticmethod
    async def get_user_downline_members(db: AsyncSession, user_id: str):
        downlines = await UserRepository.get_user_downline(db, user_id)

        if not downlines:
            return json_response(
                status_code=404,
                data=[],
                message="No downlines found"
            )
        
        return json_response(
            status_code=200,
            data=[user.model_dump() for user in downlines],  # Ensure it's JSON-serializable
            message="Downlines fetched successfully"
        )


    @staticmethod
    async def initiate_member_activation2(db: AsyncSession, account_data: InitiateMemberActivation, activated_by: str):
        try:

            user = await KYCRepository.get_user(db, activated_by)
            
            external_id = user.external_id

            user_data = await TransactionRepository.get_user_details(db, account_data.user_id)

            if not user:
                return json_response(
                    message="Account data not found. Please contact customer service for assistance.",
                    data={"user_id": account_data.user_id},
                    status_code = 404
                )
            

            async with httpx.AsyncClient() as client:
                transfer_payload = {
                    "from_user": external_id,
                    "to_user": config("TW_MOTHERWALLET"),
                    "amount": float(175),
                    "coin": "peso"
                }
                response = await client.post(
                    url = f"{config('TW_API_URL')}/b2bapi/initiate_p2ptransfer",
                    headers = {
                        "apikey": config('TW_API_KEY'),
                        "secretkey": config("TW_SECRET_KEY"),
                    },
                    json = transfer_payload
                )

                if response.status_code != 200:
                    try:
                        error_data = response.json()
                    except Exception:
                        error_data = {"message": response.text.strip()}

                    return json_response(
                        message = response.text,
                        data = error_data,
                        status_code=response.status_code
                    )
                
                else:
                    try:
                        activation_history = ActivationHistory(
                            transaction_id=f"TRX{uuid4().hex[:17]}",  # Ensures length is exactly 20

                            user_id = account_data.user_id,
                            receiver_id = config("ADMIN_STAGING"), # CHANGED IT INTO TW_MOTHERWALLET
                            activated_by = activated_by,
                            amount=float(175),
                           # currency = "peso",
                           # transaction_type = "debit",
                            title = "Account Activation",
                            description = f"You have paid {float(175)} pesos for member account activation",
                            activated_in = "web",
                            sender_name = str(mask_name(user_data.first_name + ' ' + user_data.last_name + ".")),
                            receiver_name = "ADMIN MOTHERWALLET",
                            reference_id=response.json()['Transaction_id'],
                        )

                        db.add(activation_history)
                        await db.commit()
                        await db.refresh(activation_history)

                        return json_response(
                            message = "Account activation initiated successfully",
                            data = response.json(), # transaction reference
                            #data = transaction.transaction_id,
                            status_code = 200
                        )   


                    except Exception as e:
                        await db.rollback()
                        return json_response(
                            message = "Error creating transaction",
                            data = str(e),
                            status_code = 500
                        )


        except Exception as e:
            return json_response(
                message=f"Error fetching user topwallet id: {str(e)}",
                data={"user_id":account_data.user_id},
                status_code = 404
            )
        


    @staticmethod
    async def process_member_activation2(db: AsyncSession, process_account_data: ProcessMemberActivation, user_id: str):
        try:

            activation_history = await ActivationHistoryRepository.get_activation_history(db, process_account_data.reference_id)

            if not activation_history:
                return json_response(
                    message="Activation history not found. Please contact customer service for assistance.",
                    status_code = 404
                )
            
            
            user = await UserRepository.get_user(db, activation_history.user_id)

            if not user:
                return json_response(
                    message="User not found. Please contact customer service for assistance.",
                    status_code = 404
                )
            

            user.status = True
            user.is_activated = True

            db.add(user)

            
            activation_history.status = "Completed"
            db.add(activation_history)
            await db.commit()
            await db.refresh(activation_history)

            return json_response(
                message="Account activation processed successfully",
                status_code = 200
            )
            

        except Exception as e:
            return json_response(
                message=f"Error fetching user topwallet id: {str(e)}",
                
                status_code = 404
            )
        


    @staticmethod
    async def get_users_by_activation_status(db: AsyncSession, is_activated: bool) -> List[UserDetailSchema]:
        try:
            users = await UserRepository.get_users_by_activation_status(db, is_activated)
            return [
                UserDetailSchema(
                    user_id=user.user_id,
                    name=", ".join(filter(None, [user.user_details.last_name, " ".join(filter(None, [user.user_details.first_name, user.user_details.middle_name, user.user_details.suffix_name]))])),
                    mobile_number=user.mobile_number,
                    community_name=user.community.community_name if user.community else None
                )
                for user in users
            ]

        except Exception as e:
            print("Error fetching users by activation status:", str(e))
            raise e
        

    @staticmethod
    async def initiate_member_activation(db: AsyncSession, user_data: InitiateMemberActivation, activated_by: str):
        try:
            # Fetch activator's external ID
            activator_external_id = await UserRepository.get_user_external_id(db, activated_by)
            
            # Fetch user details
            user_info = await UserRepository.get_user_name(db, user_data.user_id)
            if not user_info:
                return json_response(
                    message="User not found",
                    status_code=404
                )

            # Fetch wallet balance
            user_balance = await UserRepository.get_user_wallet_balance(db, activated_by)
            print("User_balance:", user_balance)

            #user_data = await UserRepository.get_user_data(db, user_data.user_id)
            #if not user_data.is_kyc_verified:
            #    return json_response(
            #        message="User is not KYC verified",
            #        status_code=400
            #    )

            # 4. Ensure the user has at least 175 pesos
            activation_amount = 175
            if user_balance < activation_amount:
                return json_response(
                    message="Insufficient balance for activation",
                    data={
                        "current_balance": float(user_balance),  # Convert Decimal to float here
                        "required_balance": activation_amount
                    },
                    status_code=400
                )

            
            # Check if the user has at least 175 pesos
            if user_balance is None or float(user_balance) < 175:
                return json_response(
                    message="Insufficient wallet balance. Minimum required: 175 pesos.",
                    status_code=400
                )

            async with httpx.AsyncClient() as client:
                transfer_payload = {
                    "from_user": activator_external_id,
                    "to_user": config("TW_MOTHERWALLET"),
                    "amount": float(activation_amount),
                    "coin": "peso",
                }

                response = await client.post(
                    url=f"{config('TW_API_URL')}/b2bapi/initiate_p2ptransfer",
                    headers={
                        "apikey": config('TW_API_KEY'),
                        "secretkey": config("TW_SECRET_KEY"),
                    },
                    json=transfer_payload
                )

                if response.status_code != 200:
                    try:
                        error_data = response.json()
                    except Exception:
                        error_data = {"message": response.text.strip()}

                    return json_response(
                        message="Failed to initiate transfer",
                        data=error_data,
                        status_code=response.status_code
                    )

                # Save activation history if successful
                try:
                    activation_history = ActivationHistory(
                        transaction_id=f"TRX{uuid4().hex[:17]}",  # Ensures length is exactly 20
                        user_id=user_data.user_id,
                        receiver_id=config("ADMIN_STAGING"),  # Changed to TW_MOTHERWALLET
                        activated_by=activated_by,
                        amount=175.0,
                        title="Account Activation",
                        description="You have paid 175 pesos for member account activation",
                        activated_in="web",
                        sender_name=str(mask_name(f"{user_info["first_name"]} {user_info["last_name"]}.")),
                        receiver_name="ADMIN MOTHERWALLET",
                        reference_id=response.json().get('Transaction_id'),
                    )

                    db.add(activation_history)
                    await db.commit()
                    await db.refresh(activation_history)

                    return json_response(
                        message="Account activation initiated successfully",
                        data=response.json(),  # Transaction reference
                        status_code=200
                    )

                except Exception as e:
                    await db.rollback()
                    return json_response(
                        message="Error creating transaction",
                        data=str(e),
                        status_code=500
                    )

        except Exception as e:
            return json_response(
                message="Error fetching user data",
                data={"error": str(e)},
                status_code=500
            )



    @staticmethod
    async def process_member_activation(db: AsyncSession, process_account_data: ProcessMemberActivation, activated_by: str):
        try:
            activation_history = await ActivationHistoryRepository.get_activation_history(db, process_account_data.reference_id)

            if not activation_history:
                return json_response(
                    message="Activation history not found. Please contact customer service for assistance.",
                    status_code = 404
                )
            
            user = await UserRepository.get_user_data(db, activation_history.user_id)
            if not user:
                return json_response(
                    message="User not found. Please contact customer service for assistance.",
                    status_code = 404
                )
            
            user.status = True
            user.is_activated = True

            db.add(user)

            
            activation_history.status = "Completed"
            db.add(activation_history)
            await db.commit()
            await db.refresh(activation_history)

            # Deduct 175 pesos from the user's wallet

            await UnilevelService.distribute_activation_unilevel_rewards(db, activation_history.user_id, activation_history.reference_id)

            await UserRepository.update_user_reward_points(db, activated_by, 25)  # ✅ Pass only the increment

            reward_history_data = RewardInput(
                    id=str(uuid4()),
                    reference_id=activation_history.reference_id,
                    reward_source_type="Activation Reward",
                    reward_points=25,
                    reward_from=activation_history.user_id,
                    receiver=activated_by,
                    reward_type=f"Account Activation",
                    description=f"Account activation reward of {25} points credited to {activated_by}",
            )
            await RewardDistributionRepository.create_reward_distribution_history(db, reward_history_data)


            reward_history_data = RewardInput(
                id = str(uuid4()),
                reference_id = activation_history.reference_id,
                reward_source_type = "Account Activation",
                reward_points = 95, 
                reward_from = activation_history.user_id,
                receiver = config("ADMIN_STAGING"),  # Extract user_id from the result
                reward_type = f"Account Activation",
                description = f"Admin received 95 reward points"  # 🔥 Use `distribution[key]`
            )

            await RewardDistributionRepository.create_reward_distribution_history(db, reward_history_data)

            await RewardDistributionRepository.create_admin_reward_distribution_history(db, reward_history_data)
            await UserRepository.update_user_reward_points(db, config("ADMIN_STAGING"), 95)  # ✅ Pass only the increment

            user_balance = await UserRepository.get_user_wallet_balance(db, activated_by)

            new_balance = user_balance - 175

            # 2. Update wallet balance in the database
            await UserRepository.update_user_wallet_balance(db, activated_by, new_balance)




            return json_response(
                message="Account activation processed successfully",
                data={"new_wallet_balance": float(new_balance)},  # Convert Decimal to float
                status_code=200
            )
            

        except Exception as e:
            return json_response(
                message=f"Error fetching user topwallet id: {str(e)}",
                
                status_code = 404
            )
        

            


    @staticmethod
    async def get_members_list(db: AsyncSession):
        try:
            users_data = await UserRepository.get_member_details(db)

            if not users_data:  # Handle empty result
                return []  # Return empty list if no users found

            users_list = [
                MemberSchema(
                    user_id=user["user_id"],
                    # Format name as "firstname, middlename, lastname, suffix"
                    name=f"{user['first_name']}, {user['middle_name'] or ''} {user['last_name']}, {user['suffix_name'] or ''}".strip(),
                    mobile_number=user["mobile_number"],
                    wallet_balance=float(user["wallet_balance"]) if user["wallet_balance"] is not None else 0.0,
                    reward_points=float(user["reward_points"]) if user["reward_points"] is not None else 0.0,
                    account_type=user["account_type"],
                    community_name=user["community_name"],
                    # Format address as "house number, streetname, barangay, city, province, region"
                    address=f"{user['house_number'] or ''}, {user['street_name'] or ''}, {user['barangay'] or ''}, {user['city'] or ''}, {user['province'] or ''}, {user['region'] or ''}".strip(),
                    is_kyc_verified=user["is_kyc_verified"],
                    is_activated=user["is_activated"],
                    date_created=str(user["date_created"]),
                )
                for user in users_data
            ]

            return users_list
        except Exception as e:
            return json_response(
                message=str(e),
                status_code=500
            )




    