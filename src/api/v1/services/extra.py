def distribute_rewards(purchase_amount, users):
    # Calculate the reward pool based on 10% of the purchase amount
    reward_pool = purchase_amount * 0.1

    # Calculate the admin allocation (30% of the reward pool)
    admin_allocation = reward_pool * 0.3

    # Define the reward distribution among different users
    distribution = {
        "Hub": reward_pool * 0.05,  # 5% for Hub
        "Community": reward_pool * 0.05,  # 5% for Community
        "Merchant": reward_pool * 0.1,  # 10% for Merchant
        "User": reward_pool * 0.1,  # 10% for User
        "Referrer of Merchant": reward_pool * 0.15,  # 15% for Referrer of Merchant
        "Investor": reward_pool * 0.05,  # 5% for Investor
        # Unilevel Referral structure with different levels of reward distribution
        "Unilevel Referral": {
            "Level 1": reward_pool * 0.06 * 0.8,  # 6% for Level 1, adjusted by 80%
            "Level 2": reward_pool * 0.05 * 0.8,  # 5% for Level 2, adjusted by 80%
            "Level 3": reward_pool * 0.04 * 0.8,  # 4% for Level 3, adjusted by 80%
            "Level 4": reward_pool * 0.03 * 0.8,  # 3% for Level 4, adjusted by 80%
            "Level 5": reward_pool * 0.02 * 0.8,  # 2% for Level 5, adjusted by 80%
        },
        "Unilevel Remainder to MotherWallet": reward_pool * 0.04,  # 4% remainder goes to Mother Wallet
        "Admin (Mother Wallet)": admin_allocation,  # 30% of the reward pool for Admin allocation
    }

    # Distribute rewards to the user wallets (direct allocations)
    users["Hub"] += distribution["Hub"]
    users["Community"] += distribution["Community"]
    users["Merchant"] += distribution["Merchant"]
    users["User"] += distribution["User"]
    users["Referrer of Merchant"] += distribution["Referrer of Merchant"]
    users["Investor"] += distribution["Investor"]
    users["Admin (Mother Wallet)"] += distribution["Admin (Mother Wallet)"] + distribution["Unilevel Remainder to MotherWallet"]

    # Distribute Unilevel Referral points (levels 1 to 5)
    for level, amount in distribution["Unilevel Referral"].items():
        users[level] += amount

    # Return the updated user wallet balances
    return users

# Initialize user wallets with all starting values set to 0
users = {
    "Hub": 0,
    "Community": 0,
    "Merchant": 0,
    "User": 0,
    "Referrer of Merchant": 0,
    "Investor": 0,
    "Level 1": 0,
    "Level 2": 0,
    "Level 3": 0,
    "Level 4": 0,
    "Level 5": 0,
    "Admin (Mother Wallet)": 0,
}

# Example usage with a purchase amount of 1000
purchase_amount = 1000
updated_users = distribute_rewards(purchase_amount, users)

# Print the updated user wallet balances
import pprint
pprint.pprint(updated_users)
