from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.repositories.admin_accounts_repository import AdminAccountRepository
from api.v1.schemas.admin_accounts_schema import AdminAccountCreate, AdminLoginRequest

from utils.responses import json_response
from uuid import uuid4
from fastapi import HTTPException
from core.security import hash_password, verify_password, sign_jwt

from api.v1.repositories.user_repository import UserRepository


class AdminAccountService:

    @staticmethod
    async def create_admin_account(db: AsyncSession, admin_account_data: AdminAccountCreate, account_type: str):
        try:
            # Ensure the account type is SUPERADMIN or ADMIN
            if account_type not in ['SUPERADMIN', 'ADMIN']:
                raise HTTPException(status_code=403, detail="Permission denied: Only SUPERADMIN or ADMIN can create an admin account.")

            # If mobile_number is provided, check if it exists in the 'users' table
            if admin_account_data.mobile_number:
                user = await AdminAccountRepository.get_user_by_mobile_number(db, admin_account_data.mobile_number)
                if not user:
                    raise HTTPException(status_code=400, detail="Mobile number does not exist in users table")

            # Proceed with creating the admin account
            admin_account_data = admin_account_data.dict()
            admin_account_data['user_id'] = str(uuid4())  # Ensure a unique ID for the admin account
            admin_account_data['password'] = hash_password(admin_account_data['password'])
            admin_account_data['account_url'] = str(uuid4())

            admin_account = await AdminAccountRepository.create_admin_account(db, admin_account_data)

            return json_response(
                message="Admin account created successfully",
                data={"user_id": admin_account.user_id},
                status_code=201
            )

        except Exception as e:
            return json_response(
                message=str(e),
                status_code=500
            )

    @staticmethod
    async def create_admin_account2(db: AsyncSession, admin_account_data: AdminAccountCreate):
        try:
            # If mobile_number is provided, check if it exists in the 'users' table
            if admin_account_data.mobile_number:
                user = await AdminAccountRepository.get_user_by_mobile_number(db, admin_account_data.mobile_number)
                if not user:
                    raise HTTPException(status_code=400, detail="Mobile number does not exist in users table")

            # Proceed with creating the admin account
            admin_account_data = admin_account_data.dict()
            admin_account_data['user_id'] = str(uuid4())  # Ensure a unique ID for the admin account
            admin_account_data['password'] = hash_password(admin_account_data['password'])
            admin_account_data['account_url'] = str(uuid4())

            admin_account = await AdminAccountRepository.create_admin_account(db, admin_account_data)

            return json_response(
                message="Admin account created successfully",
                data={"user_id": admin_account.user_id},
                status_code=201
            )

        except Exception as e:
            return json_response(
                message=str(e),
                status_code=500
            )

    @staticmethod
    async def initiate_login(db: AsyncSession, account_url: str, login_request: AdminLoginRequest):
        try:
            admin_account = await AdminAccountRepository.get_admin_account(db, account_url)
            
            mobile_number = admin_account.mobile_number
            
            user = await UserRepository.get_user_by_mobile(db, mobile_number)
            
            if not admin_account:
                return json_response(
                    message="Admin account not found",
                    status_code=404
                )
            
            hashed_password = admin_account.password

            is_valid = verify_password(login_request.password, hashed_password)

            if not is_valid:
                return json_response(
                    message="Invalid password",
                    status_code=401
                )
            
            access_token = sign_jwt(user.user_id, admin_account.account_type)["access_token"]
            
            return json_response(
                message="Login successful",
                data = {
                    "access_token": access_token,
                    "account_type": admin_account.account_type
                },
                status_code=200
            )
            

        
        except Exception as e:
            return json_response(
                message=str(e),
                status_code=500
            )