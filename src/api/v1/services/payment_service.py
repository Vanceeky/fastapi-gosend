import httpx

class PaymentProcessor:
    @staticmethod
    async def initiate_merchant_purchase(db: AsyncSession, merchant_id: str, user_id: str, total_amount: float):
        try:
            # Retrieve user data
            user = await KYCRepository.get_user(db, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            user_external_id = user.external_id

            # Retrieve merchant details
            merchant_external_id = await MerchantRepository.get_merchant_external_id(db, merchant_id)
            if not merchant_external_id:
                raise HTTPException(status_code=404, detail="Merchant not found")

            # Calculate 90% for merchant and 10% for admin
            merchant_amount = total_amount * 0.9  # 90% for the merchant
            admin_amount = total_amount * 0.1     # 10% for the admin

            # Prepare transfer payload for both merchant and admin
            transfer_payload_merchant = {
                "from_user": user_external_id,
                "to_user": merchant_external_id,
                "amount": merchant_amount,
                "coin": "peso",
            }

            # Assuming the admin's external ID is available
            admin_external_id = await UserRepository.get_admin_external_id(db)
            if not admin_external_id:
                raise HTTPException(status_code=404, detail="Admin not found")

            transfer_payload_admin = {
                "from_user": user_external_id,
                "to_user": admin_external_id,
                "amount": admin_amount,
                "coin": "peso",
            }

            # Step 1: Initiate both transfers
            async with httpx.AsyncClient() as client:
                # Initiate transfer to the merchant
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

                # Extract transaction references for processing later
                transaction_merchant = response_merchant.json()
                transaction_admin = response_admin.json()

                # Step 2: Process both transfers
                # Assuming you have OTP or other process data available for confirmation
                otp_code = "example_otp_code"  # You may get this from the user or another source

                # Process merchant transaction
                response_merchant_process = await client.post(
                    url=f"{config('TW_API_URL')}/b2bapi/process_p2ptransfer",
                    headers={
                        "apikey": config('TW_API_KEY'),
                        "secretkey": config("TW_SECRET_KEY"),
                    },
                    json={
                        "Transaction_id": transaction_merchant['transaction_reference'],
                        "otp": otp_code,
                    }
                )

                if response_merchant_process.status_code != 200:
                    raise HTTPException(status_code=500, detail="Merchant transaction processing failed")

                # Process admin transaction
                response_admin_process = await client.post(
                    url=f"{config('TW_API_URL')}/b2bapi/process_p2ptransfer",
                    headers={
                        "apikey": config('TW_API_KEY'),
                        "secretkey": config("TW_SECRET_KEY"),
                    },
                    json={
                        "Transaction_id": transaction_admin['transaction_reference'],
                        "otp": otp_code,
                    }
                )

                if response_admin_process.status_code != 200:
                    raise HTTPException(status_code=500, detail="Admin transaction processing failed")
                
            # Return success message with results for both transactions
            return json_response(
                message="Merchant and admin payments successfully processed.",
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
