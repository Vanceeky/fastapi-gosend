from uuid import uuid4
from fastapi import HTTPException
import json
import httpx
from decouple import config

class TransactionService:
    @staticmethod
    async def create_distribution(
        db, sponsor_id, receiver_id, amount, distribution_type, transaction_id
    ):
        """Helper function to create a distribution history."""
        try:
            await TransactionRepository.create_distribution_history(
                distribution_id=str(uuid4().hex),
                sponsor=sponsor_id,
                receiver=receiver_id,
                amount=amount,
                type=distribution_type,
                transaction_id=transaction_id,
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error creating distribution: {str(e)}")

    @staticmethod
    async def process_sponsor_distribution(db, user_id, transaction_id):
        """Handles sponsor, rebate, and admin distribution logic."""
        sponsor_distribution_reward = 0.60
        rebate_distribution_reward = 0.60
        admin_distribution_reward = 3.8

        try:
            user_referrer = await ReferralRepository.get_referral(db, user_id)

            # Sponsor distribution
            await TransactionService.create_distribution(
                db=db,
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
            raise HTTPException(status_code=400, detail="Error in sponsor distribution: " + str(e))

    @staticmethod
    async def process_cashout(db, transaction_data, otp_code, user_id):
        try:
            # Fetch transaction and user
            transaction = await TransactionRepository.get_transaction(db, transaction_data.transaction_reference)
            if not transaction:
                raise HTTPException(status_code=404, detail="Transaction not found")

            user = await TransactionRepository.get_user(db, user_id)
            if not otp_code:
                raise HTTPException(status_code=400, detail="OTP code is required")

            if transaction.status == 'completed':
                return {
                    "message": "Transaction already completed",
                    "data": transaction.dict(exclude_unset=True),
                    "status_code": 400
                }

            # Prepare metadata
            metadata = json.loads(transaction.extra_metadata)
            metadata.update({
                "phone": user.mobile_number,
                "amount": str(metadata.get('amount')),
            })

            # Process P2P transfer
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

                p2p_response = await client.post(p2p_url, headers=headers, json=p2p_payload)
                if p2p_response.status_code != 200:
                    error_data = p2p_response.json() if p2p_response.headers.get("content-type") == "application/json" else {"message": p2p_response.text.strip()}
                    return {"message": "Transaction failed", "data": error_data, "status_code": p2p_response.status_code}

            # Bank withdrawal
            async with httpx.AsyncClient() as client:
                withdraw_url = f"{config('TW_API_URL')}/b2bapi/self_bank_withdraw"
                withdraw_payload = {
                    "full_name": metadata['full_name'],
                    "phone": user.mobile_number,
                    "account_number": metadata['account_number'],
                    "bank_code": metadata['bank_code'],
                    "channel": metadata['channel'],
                    "amount": str(metadata['amount']),
                    "order_number": str(transaction.transaction_id),
                }

                withdraw_response = await client.post(withdraw_url, headers=headers, json=withdraw_payload)
                if withdraw_response.status_code != 200:
                    error_data = withdraw_response.json() if withdraw_response.headers.get("content-type") == "application/json" else {"message": withdraw_response.text.strip()}
                    return {"message": "Transaction failed during bank withdrawal", "data": error_data, "status_code": withdraw_response.status_code}

            # Update transaction status
            transaction.status = 'Completed'

            # Process sponsor distribution
            await TransactionService.process_sponsor_distribution(db, user_id, transaction.transaction_id)

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Error processing cashout: {str(e)}")
