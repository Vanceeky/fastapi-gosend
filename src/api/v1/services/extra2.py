from sqlalchemy.ext.asyncio import AsyncSession

async def distribute_rewards_to_users(db: AsyncSession, purchase_amount: float, repo):
    reward_pool = purchase_amount * 0.1
    admin_allocation = reward_pool * 0.3

    distribution = {
        "Hub": reward_pool * 0.05,
        "Community": reward_pool * 0.05,
        "Merchant": reward_pool * 0.1,
        "User": reward_pool * 0.1,
        "Referrer of Merchant": reward_pool * 0.15,
        "Investor": reward_pool * 0.05,
        "Unilevel Remainder to MotherWallet": reward_pool * 0.04,
        "Admin (Mother Wallet)": admin_allocation,
    }

    # Get users from your repository
    hub = await repo.get_hub(db)
    community = await repo.get_community(db)
    merchant = await repo.get_merchant(db)
    investor = await repo.get_investor(db)
    referrer = await repo.get_referrer_of_merchant(db)
    
    # Directly update their wallet balances if they exist
    if hub: hub.wallet_balance += distribution["Hub"]
    if community: community.wallet_balance += distribution["Community"]
    if merchant: merchant.wallet_balance += distribution["Merchant"]
    if investor: investor.wallet_balance += distribution["Investor"]
    if referrer: referrer.wallet_balance += distribution["Referrer of Merchant"]
    
    # Handle the admin wallet
    admin_wallet = await repo.get_admin_wallet(db)  # Assuming you have a function for this
    if admin_wallet:
        admin_wallet.wallet_balance += (
            distribution["Admin (Mother Wallet)"] + distribution["Unilevel Remainder to MotherWallet"]
        )

    # Commit changes
    await db.commit()

    # Call your Unilevel function separately
    await distribute_unilevel_rewards(db, purchase_amount)
