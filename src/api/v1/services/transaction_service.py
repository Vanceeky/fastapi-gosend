
from sqlalchemy.ext.asyncio import AsyncSession 
from api.v1.repositories.kyc_repository import KYCRepository
from api.v1.repositories.transaction_repository import TransactionRepository


from utils.responses import json_response
from api.v1.schemas.transaction_schema import TransactionCreate, ProcessTransaction, MerchantData, ProcessQrphTransaction
from models.transaction_model import Transaction
from utils.extra import mask_name

from decouple import config
import httpx
from uuid import uuid4
from fastapi import HTTPException
import json
import pytz
from datetime import timezone, datetime


from api.v1.services.referral_service import ReferralService
from api.v1.repositories.referral_repository import ReferralRepository


class TransactionService:
    @staticmethod
    async def bank_list(db: AsyncSession):
        url = f"{config('TW_API_URL')}/b2bapi/get_banks_list"

        async with httpx.AsyncClient() as client: 
            headers = {
                "apikey": config('TW_API_KEY'),
                "secretkey": config("TW_SECRET_KEY"),
            }

            response = await client.post(
                url,
                headers=headers
            )

           # print(response.json())

            if not response.json().get("success"): 
                return json_response(
                    message="Failed to fetch bank list",
                    data=response.json(),
                    status_code=400
                )
            else:
                return json_response(
                    message="Successfully fetched list of banks",
                    data=response.json(),
                    status_code=200
                )

    @staticmethod
    async def initiate_cashout(db: AsyncSession, transaction_data: TransactionCreate, user_id: str):
        try:
            user = await KYCRepository.get_user(db, user_id)
            
            external_id = user.external_id

            user_data = await TransactionRepository.get_user_details(db, user_id)

            url = f"{config('TW_API_URL')}/b2bapi/initiate_p2ptransfer"

            async with httpx.AsyncClient() as client:
                headers = {
                    "apikey": config('TW_API_KEY'),
                    "secretkey": config("TW_SECRET_KEY"),
                }


                transfer_payload = {
                    "from_user": external_id,
                    "to_user": config("TW_MOTHERWALLET"),
                    "amount": float(transaction_data.amount) + float(15),
                    "coin": "peso",
                }

                response = await client.post(
                    url,
                    headers=headers,
                    json=transfer_payload,
                )

                print(f"Response: {response.text}")

                if response.status_code != 200:
                    try:
                        error_data = response.json()
                    except Exception:
                        error_data = {"message": response.text.strip()}

                    return json_response(
                        message="Transaction failed",
                        data=error_data,
                        status_code=response.status_code,
                    )
                else:

                    try:
                        transaction = Transaction(
                            transaction_id=f"TRX{str(uuid4().hex)}",
                            sender_id=external_id,
                            receiver_id=transaction_data.account_number,
                            amount=transaction_data.amount,
                            currency='peso',
                            transaction_type='debit',
                            title='Withdraw',
                            description=f"You have cashed out ₱{transaction_data.amount}",
                            sender_name=str(mask_name(user_data.first_name + ' ' + user_data.last_name + ".")),

                            receiver_name=str(mask_name(transaction_data.full_name)),
                            transaction_reference=response.json()['Transaction_id'],
                            #extra_metadata=str(transaction_data)
                        )

                        db.add(transaction)
                        await db.commit()
                        await db.refresh(transaction)

                    except Exception as e:
                        db.rollback()
                        raise HTTPException(status_code=400, detail=str(e))

                    # successful response
                    return json_response(
                        message="Successfully Initiated Cashout",
                        data=response.json(),
                        status_code=200,
                    )


        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


    @staticmethod
    async def process_cashout(db: AsyncSession, transaction_data: ProcessTransaction, otp_code: str, user_id: str):
        try:

            # fetch transacton and user
            transaction = await TransactionRepository.get_transaction(db, transaction_data.transaction_reference)

            user = await TransactionRepository.get_user(db, user_id)

            if not transaction:
                raise HTTPException(status_code=404, detail="Transaction not found")

            if not otp_code:
                raise HTTPException(status_code=400, detail="OTP code is required")
            
            if transaction.status == 'completed':
                return json_response(
                    message="Transaction already completed",
                    data=transaction.dict(exclude_unset=True),
                    status_code=400
                )

            #prepare metadata
            metadata_raw = transaction.extra_metadata
            metadata_json = json.loads(metadata_raw)
            metadata_json['phone'] = user.mobile_number
            metadata_json['amount'] = str(metadata_json['amount'])


            # process p2p transfer
            async with httpx.AsyncClient() as client:
                p2p_url = f"{config('TW_API_URL')}/b2bapi/process_p2ptransfer"
                p2p_payload = {
                    "Transaction_id": transaction.transaction_reference,
                    "otp": otp_code,
                }

                headers = {
                    "apikey": config('TW_API_KEY'),
                    "secretkey": config("TW_SECRET_KEY"),
                }
                
                p2p_response = await client.post(
                    url = p2p_url, headers = headers, json = p2p_payload
                )

                if p2p_response.status_code != 200:
                    try:
                        error_data = p2p_response.json() 
                    except Exception as e:
                        error_data = {
                            "message": p2p_response.text.strip()
                        }

                    return json_response(
                        message =  "Transaction failed",
                        data = error_data,
                        status_code =  p2p_response.status_code
                    )
                


            # process bank withdrawal
            async with httpx.AsyncClient() as client:
                withdraw_url = f"{config('TW_API_URL')}/b2bapi/self_bank_withdraw"
                
                withdraw_payload = {
                    "full_name": metadata_json['full_name'],
                    "phone": user.mobile_number,
                    "account_number": metadata_json['account_number'],
                    "bank_code": metadata_json['bank_code'],
                    "channel": metadata_json['channel'],
                    "amount": str(metadata_json['amount']),
                    "order_number": str(transaction.transaction_id)
                }

                withdraw_response = await client.post(
                    url = withdraw_url,
                    headers = headers,
                    json = withdraw_payload
                )

                if withdraw_response != 200:
                    try:
                        error_data = withdraw_response.json()
                    except Exception as e:
                        error_data = {
                            "message": withdraw_response.text.strip()
                        }


            await TransactionService.process_sponsor_distribution(db, user_id, transaction.transaction_id)

            transaction.status = "Completed"

            await db.commit()

        
            # Prepare final response
            tz_utc8 = pytz.timezone("Asia/Manila")
            metadata_json['amount'] = float(metadata_json['amount'])
            metadata_json['transaction_amount'] = metadata_json['amount']

            response = {
                "amount": metadata_json['amount'],
                "transaction_amount": metadata_json['transaction_amount'],
                "transaction_id": transaction.transaction_id,
                "transaction_fee": 15.0,
                "user_rebate": 0.60,
                "transaction_timestamp": transaction.created_at.replace(
                    tzinfo=timezone.utc
                ).astimezone(tz_utc8).strftime('%Y-%m-%d %H:%M:%S'),
            }

            # Final response
            return json_response(
                message="Successfully processed cashout",
                data=response,
                status_code=200
            )


        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing cashout: {str(e)}")

    

    @staticmethod
    async def initiate_qrph_transfer(db: AsyncSession, merchant_data: MerchantData, user_id: str):
        try:
            user = await KYCRepository.get_user(db, user_id )

            external_id = user.external_id

            qrph_payload = {
                "userid": external_id,
                "disburse_id": merchant_data.disburse_id,
                "merchant_name": merchant_data.merchant_name,
                "amount": str(merchant_data.amount),
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url = f"{config('TW_API_URL')}/b2bapi/Initiate_disbursement",
                    headers = {
                        "apikey": config('TW_API_KEY'),
                        "secretkey": config("TW_SECRET_KEY"),
                    },
                    json = qrph_payload
                )

                if response.status_code == 400:
                    return json_response(
                        message = response.text,
                        data = response.json(),
                        status_code = response.status_code
                    )
                
                if response.status_code == 200:
                    return json_response(
                        message = response.text,
                        data = {
                            "merchant_name": merchant_data.merchant_name,
                            "disburse_id": merchant_data.disburse_id,
                            "transaction_amount": merchant_data.amount,
                            "transaction_reference": response.json()['Transaction_id'],
                        },
                        status_code = response.status_code
                    )
                
        except Exception as e:
            return json_response(
                message = str(e),
                data = {},
                status_code = 400
            )


    @staticmethod
    async def process_qrph_transfer(db: AsyncSession, transaction_data: ProcessQrphTransaction, otp_code: str, user_id: str):
        try:
            transaction = await TransactionRepository.get_transaction(db, transaction_data.transaction_reference)

            if not otp_code:
                return json_response(
                    message="OTP code is required",
                    data={},
                    status_code=400
                )
            
            if transaction:
                return json_response(
                    message = "Successfully processed QRPH transfer",
                    data = {
                        "disburse_id": transaction_data.disburse_id,
                        "transaction_reference": transaction_data.transaction_reference,
                        "transaction_amount": transaction.amount,
                        "transaction_date": transaction.created_at
                    }
                )
        except Exception as e:
            return json_response(
                message = str(e),
                data = {},
                status_code = 400
            )
            




    @staticmethod
    async def resend_tw_otp(db: AsyncSession, transaction_data: ProcessTransaction, user_id: str):
        
        transaction = await TransactionRepository.get_transaction(db, transaction_data.transaction_reference)

        payload = {
            "Transaction_id": transaction.transaction_reference
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url = f"{config('TW_API_URL')}/b2bapi/resend_otp_tid/",
                headers = {
                    "apikey": config('TW_API_KEY'),
                    "secretkey": config("TW_SECRET_KEY"),
                },
                data = payload
            )

            if response.status_code == 400:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"message": response.text.strip() or "Invalid request format"}
                return json_response(
                    message="Bad Request",
                    data=error_data,
                    status_code=400
                )

            # Handle 200 status code
            if response.status_code == 200:
           
                return json_response(
                    message="OTP sent successfully",
                    data=response.json(),
                    status_code=200
                )


    @staticmethod
    async def process_sponsor_distribution(db, user_id, transaction_id):
        sponsor_distribution_reward = 0.60 # percentage
        rebate_distribution_reward = 0.60 # percentage
        admin_distribution_reward = 3.8 # percentage

        try:
            user_referrer = await ReferralRepository.get_referral(db, user_id)

            # sponsor distribution
            await TransactionRepository.create_distribution_history(
                db,
                sponsor_id=user_id,
                receiver_id=user_referrer,
                amount=sponsor_distribution_reward,
                distribution_type="Bank Transfer Rewards",
                transaction_id=transaction_id,

            )

            # User rebate distribution
            await TransactionService.create_distribution(
                db=db,
                sponsor_id=user_id,
                receiver_id=user_id,
                amount=rebate_distribution_reward,
                distribution_type="User Rebate",
                transaction_id=transaction_id,
            )

            # Admin distribution
            await TransactionService.create_distribution(
                db=db,
                sponsor_id=user_id,
                receiver_id=config("TW_MOTHERWALLET"),
                amount=admin_distribution_reward,
                distribution_type="Bank Transfer Reward",
                transaction_id=transaction_id,
            )

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail = f"Error in sponsor Distribution: {str(e)}")




    