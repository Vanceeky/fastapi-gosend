from sqlalchemy.ext.asyncio import AsyncSession
from utils.responses import json_response
from api.v1.schemas.payQR_schema import PayQR, ProcessPayTransaction
from api.v1.repositories.user_repository import UserRepository

from api.v1.services.kyc_service import KYCRepository
from api.v1.repositories.merchant_repository import MerchantRepository
from fastapi import HTTPException

import httpx
from decouple import config

from models.purchase_model import MerchantPurchase
from uuid import uuid4
from api.v1.repositories.purchase_repository import PurchaseRepository
from api.v1.services.reward_distribution_service import RewardService


class PayQRService:

    @staticmethod
    async def pay_qr(db: AsyncSession, pay_qr_data: PayQR, user_id: str):
        try:
            user = await UserRepository.get_user(db, user_id)

            if not user:
                return json_response(
                    message="User not found",
                    status_code=404
                )
            
            target_url = {
                f"https://gosendit.net/paynow.php?"
                f"user_id={user_id}&"
                f"merchant_id={pay_qr_data.merchant_id}&"
                f"amount={pay_qr_data.amount}"
            }
            
            return json_response(
                message = "Successfully fetched PayQR URL",
                data = {
                    "url": target_url
                },
                status_code = 200
            )
        
        except Exception as e:
            print(e)
            return json_response(
                message = "Something went wrong",
                status_code = 500
            )
        


    @staticmethod
    async def pay_merchant_qr(db: AsyncSession, pay_qr_data: PayQR, user_id: str):
        try:
            # Retrieve the customer using user_id instead of passing customer_id
            customer = await KYCRepository.get_user(db, user_id)

            customer_external_id = customer.external_id
            if not customer_external_id:
                raise HTTPException(status_code=404, detail="Customer not found")

            # Get merchant details
            merchant_external_id, merchant_discount = await MerchantRepository.get_merchant_external_id_discount(db, pay_qr_data.merchant_id)
            print(f"Merchant External ID: {merchant_external_id}, Discount: {merchant_discount}")

            if not merchant_external_id:
                raise HTTPException(status_code=404, detail="Merchant not found")

            # Initiate payment
            async with httpx.AsyncClient() as client:
                transfer_payload_merchant = {
                    "from_user": customer_external_id,  # Now correctly derived
                    "to_user": "42F44B760E357DTOP",
                    "amount": pay_qr_data.amount,
                    "coin": "peso",
                }

                response = await client.post(
                    url=f"{config('TW_API_URL')}/b2bapi/initiate_p2ptransfer",
                    headers={
                        "apikey": config('TW_API_KEY'),
                        "secretkey": config("TW_SECRET_KEY"),
                    },
                    json=transfer_payload_merchant
                )

                if response.status_code != 200:
                    try:
                        error_data = response.json()
                    except Exception:
                        error_data = {"message": response.text.strip()}

                    return json_response(
                        message=response.text,
                        data=error_data,
                        status_code=response.status_code
                    )
                else:
                    merchant_purchase = MerchantPurchase(
                        transaction_id=f"TRX{str(uuid4().hex)}",
                        merchant_id=pay_qr_data.merchant_id,
                        customer_id=user_id,  # Use user_id here
                        amount=pay_qr_data.amount,
                        reference_id=response.json()["Transaction_id"],
                        description=f"You have paid {float(pay_qr_data.amount)} to {pay_qr_data.merchant_id}",
                    )

                    db.add(merchant_purchase)
                    await db.commit()
                    await db.refresh(merchant_purchase)

                    return json_response(
                        message="Successfully initiated merchant payment",
                        data=response.json(),
                        status_code=200
                    )

        except Exception as e:
            return json_response(
                message=f"Error initiating merchant payment: {str(e)}",
                status_code=500
            )


    @staticmethod
    async def process_pay_qr(db: AsyncSession, process_pay_qr_data: ProcessPayTransaction, user_id: str):
        try:

            result = await PurchaseRepository.get_merchant_purchase(db, process_pay_qr_data.reference_id)
            '''
            if result.status == "COMPLETED":
                return json_response(
                    message="Transaction already processed.",
                    data={"reference_id": result.reference_id, "status": result.status},
                    status_code=400
                )
            '''

            reference_id = result.reference_id
            merchant_id = result.merchant_id
            amount = result.amount

            print(f"Reference ID: {reference_id}, Merchant ID: {merchant_id}, Amount: {amount}")

            merchant_discount = await PurchaseRepository.get_merchant_discount(db, merchant_id)
        
            print(f"Received user ID: {user_id}")

            if not reference_id:
                raise HTTPException(status_code=404, detail="Merchant payment not found")
            
            # Calculate the discounted amount
            discount_amount = amount * (merchant_discount / 100)  # Discount as a percentage
            discounted_total = amount - discount_amount  # Total after discount

            # Assign amounts
            admin_amount = discount_amount  # Admin gets the discount amount
            merchant_amount = discounted_total  # Merchant gets the remaining amount

            hub_id = 'abc38b99-43bd-43c1-8fe1-9d60049cecb5'
            investor_id = '176e53d0-bce7-4c78-95f4-66a93fa7fe99'

            await RewardService.distribute_rewards_main(db, admin_amount, user_id, hub_id, investor_id, merchant_id, reference_id)
            
            result.status = "COMPLETED"

           # await MerchantRepository.update_merchant_wallet(db, merchant_id, merchant_amount)


            await db.commit()
            await db.refresh(result)

            return json_response(
                message="Successfully processed merchant payment",
                data={
                    "reference_id": reference_id,
                    "merchant_id": merchant_id,
                    "amount": amount,
                    "admin_amount": admin_amount,
                    "merchant_amount": merchant_amount,
                },
                status_code=200
            )




        except Exception as e:
            return json_response(
                message = f"Error processing merchant payment: {str(e)}",
                status_code = 500
            )
        
