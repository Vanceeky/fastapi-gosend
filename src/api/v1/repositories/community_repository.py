from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import update

from models.community_model import Community
from api.v1.schemas.community_schema import CommunityCreate, CommunitySchema, LeaderSchema
from sqlalchemy.exc import IntegrityError

from utils.responses import json_response
from fastapi import HTTPException

from models.user_model import User, UserWallet, UserDetail
from models.wallet_model import Wallet
from typing import Dict, Any

import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommunityRepository:

    @staticmethod
    async def is_community_name_exists(db: AsyncSession, community_name: str) -> bool:
        result = await db.execute(
            select(Community).where(Community.community_name == community_name)
        )
        return result.scalar() is not None

    @staticmethod
    async def is_leader_in_another_community(db: AsyncSession, leader_id: str) -> bool:
        result = await db.execute(
            select(Community).where(Community.leader_mobile_number == leader_id)
        )
        return result.scalar() is not None

    @staticmethod
    async def is_leader_exists(db: AsyncSession, leader_id: str) -> bool:
        result = await db.execute(
            select(User).where(User.mobile_number == leader_id)
        )
        return result.scalar() is not None


    @staticmethod
    async def update_leader_role(db: AsyncSession, leader_mobile_number: str):
        try:
            result = await db.execute(
                select(User).where(User.mobile_number == leader_mobile_number)
            )
            leader = result.scalar()

            if not leader:
                raise HTTPException(status_code=404, detail="Leader not found")
            
            """
            if leader.account_type == "LEADER":
                return json_response(
                    message="User is already a leader",
                    status_code=200
                )
            """

            leader.account_type = "LEADER"
            await db.commit()
            await db.refresh(leader)

            return True

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def create_community(db: AsyncSession, community_data: CommunityCreate):
        try:
   
            if await CommunityRepository.is_community_name_exists(db, community_data['community_name']):
                raise HTTPException(status_code=400, detail="Community name already exists")

            if await CommunityRepository.is_leader_in_another_community(db, community_data['leader_mobile_number']):
                raise HTTPException(status_code=400, detail="Leader is already assigned to another community")
            
            if not await CommunityRepository.is_leader_exists(db, community_data['leader_mobile_number']):
                raise HTTPException(status_code=400, detail="Leader does not exist")

            if not await CommunityRepository.update_leader_role(db, community_data['leader_mobile_number']):
                raise HTTPException(status_code=400, detail="Leader role update failed")
            

            community = Community(**community_data)
            db.add(community)

            await db.commit()
            await db.refresh(community)

            return community

        except IntegrityError as e:
            await db.rollback()
            if "UNIQUE constraint failed" in str(e):
                raise HTTPException(status_code=400, detail="Community already exists")
        
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))



    @staticmethod
    async def get_all_communities(db: AsyncSession):
        try:
            query = (
                select(Community)
                .options(
                    joinedload(Community.leader).joinedload(User.user_details),  # Load leader details
                    selectinload(Community.users)  # ✅ Use selectinload for large collections
                )
            )
            result = await db.execute(query)
            communities = result.scalars().all()  # ✅ Apply .unique()

            return [
                CommunitySchema(
                    community_id=community.community_id,
                    community_name=community.community_name,
                    leader=LeaderSchema(
                        first_name=community.leader.user_details.first_name if community.leader else None,
                        middle_name=community.leader.user_details.middle_name if community.leader else None,
                        last_name=community.leader.user_details.last_name if community.leader else None,
                        suffix=community.leader.user_details.suffix_name if community.leader else None,
                    ) if community.leader else None,
                    reward_points=float(community.reward_points),
                    number_of_members=len(community.users) + (1 if community.leader else 0),  # ✅ Count members + leader
                    date_added=community.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                )
                for community in communities
            ]

        except Exception as e:
            print(f"Error fetching communities: {e}")
            return None




    async def get_community_with_leader(db: AsyncSession, community_id: str):
        result = await db.execute(
            select(Community).where(Community.community_id == community_id).options(joinedload(Community.user))
        )
        community = result.scalar()
        if not community:
            raise HTTPException(status_code=404, detail="Community not found")

        # Access leader information via the `user` relationship
        leader_info = {
            "leader_id": community.user.user_id,
            "username": community.user.username,
            "email": community.user.email
        }

        return {
            "community_id": community.community_id,
            "community_name": community.community_name,
            "leader": leader_info,
            "created_at": community.created_at,
            "updated_at": community.updated_at
        }
    
    async def get_community_with_leader_details(db: AsyncSession, community_id: str):
        result = await db.execute(
            select(Community)
            .where(Community.community_id == community_id)
            .options(
                joinedload(Community.user)  # Load leader (User)
                .joinedload(User.user_details),  # Load leader's details (UserDetail)
                joinedload(Community.user).joinedload(User.user_address)  # Load leader's address (UserAddress)
            )
        )
        community = result.scalar()
        if not community:
            raise HTTPException(status_code=404, detail="Community not found")

        # Construct leader's full details
        leader_info = {
            "user_id": community.user.user_id,
            "mobile_number": community.user.mobile_number,
            "email_address": community.user.email_address,
            "first_name": community.user.user_details.first_name if community.user.user_details else None,
            "middle_name": community.user.user_details.middle_name if community.user.user_details else None,
            "last_name": community.user.user_details.last_name if community.user.user_details else None,
            "suffix_name": community.user.user_details.suffix_name if community.user.user_details else None,
            "address": {
                "house_number": community.user.user_address.house_number if community.user.user_address else None,
                "street_name": community.user.user_address.street_name if community.user.user_address else None,
                "barangay": community.user.user_address.barangay if community.user.user_address else None,
                "city": community.user.user_address.city if community.user.user_address else None,
                "province": community.user.user_address.province if community.user.user_address else None,
                "region": community.user.user_address.region if community.user.user_address else None,
            }
        }

        return {
            "community_id": community.community_id,
            "community_name": community.community_name,
            "leader": leader_info,
            "created_at": community.created_at,
            "updated_at": community.updated_at
        }
    


    # MAIN 
    @staticmethod
    async def get_community_leader_reward_points(db: AsyncSession, community_id: str):
        try:
            result = await db.execute(
                select(Wallet.reward_points)
                .join(UserWallet, Wallet.wallet_id == UserWallet.wallet_id)
                .join(User, User.user_id == UserWallet.user_id)
                .join(Community, Community.leader_mobile_number == User.mobile_number)
                .filter(Community.community_id == community_id)
            )
            reward_points = result.scalar()
            return reward_points
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error fetching community leader reward points: {str(e)}")

    @staticmethod
    async def get_community_leader_reward_points2(db: AsyncSession, community_id: str):
        try:
            # Query to retrieve the reward points of the community leader from the Wallet table
            result = await db.execute(
                select(
                    Wallet.reward_points  # Select reward_points from Wallet
                )
                .join(User, User.mobile_number == Community.leader)  # Join Community with User to get the leader
                .join(UserWallet, UserWallet.user_id == User.user_id)  # Join UserWallet to get the user_wallet
                .join(Wallet, Wallet.wallet_id == UserWallet.wallet_id)  # Join Wallet to get the reward_points
                .where(Community.community_id == community_id)
            )

            # Retrieve the reward points of the community leader
            reward_points = result.scalar_one_or_none()

            return reward_points if reward_points is not None else 0  # Return 0 if no reward points are found

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error fetching community leader reward points: {str(e)}")
        
    @staticmethod
    async def update_community_leader_reward_points(db: AsyncSession, community_id: str, new_points: float):
        # Find the leader by community_id (from the Community table)
        result = await db.execute(
            select(User.user_id, Wallet.wallet_id, Wallet.reward_points)  # Fetch existing points too
            .join(Community, Community.leader_mobile_number == User.mobile_number)
            .join(UserWallet, UserWallet.user_id == User.user_id)
            .join(Wallet, Wallet.wallet_id == UserWallet.wallet_id)
            .filter(Community.community_id == community_id)
        )

        leader = result.fetchone()

        if not leader:
            return {"status": "error", "message": "Leader not found for the given community."}

        leader_user_id, wallet_id, current_reward_points = leader
        current_reward_points = current_reward_points or 0  # Default to 0 if None

        # **Fix: Add new points to existing points instead of overwriting**
        updated_points = current_reward_points + new_points

        await db.execute(
            update(Wallet)
            .where(Wallet.wallet_id == wallet_id)
            .values(reward_points=updated_points)  # ✅ Accumulate
        )
        await db.commit()

        return {"status": "success", "message": "Leader's reward points updated.", "reward_points": updated_points, "user_id": leader_user_id}


    @staticmethod
    async def update_community_leader_reward_points2(db: AsyncSession, community_id: str, new_points: float):
        # Find the leader by community_id (from the Community table)
        result = await db.execute(
            select(User.user_id, Wallet.wallet_id)
            .join(Community, Community.leader_mobile_number == User.mobile_number)
            .join(UserWallet, UserWallet.user_id == User.user_id)
            .join(Wallet, Wallet.wallet_id == UserWallet.wallet_id)
            .filter(Community.community_id == community_id)
        )

        leader = result.fetchone()
        
        leader_user_id, wallet_id = leader
        
        if leader_user_id:
            # Update the reward points for the leader's wallet
            await db.execute(
                update(Wallet)
                .where(Wallet.wallet_id == wallet_id)
                .values(reward_points=new_points)
            )
            await db.commit()
            return {"status": "success", "message": "Leader's reward points updated.", "reward_points": new_points, "user_id": leader_user_id}
        else:
            return {"status": "error", "message": "Leader not found for the given community."}

    @staticmethod
    async def update_community_leader_reward_points2(db: AsyncSession, community_id: str, new_reward_points: float):
        try:
            # First, retrieve the wallet_id of the community leader
            result = await db.execute(
                select(User.user_id)
                .join(Community, Community.leader == User.mobile_number)
                .where(Community.community_id == community_id)
            )

            leader_user_id = result.scalar_one_or_none()

            if not leader_user_id:
                raise HTTPException(status_code=404, detail="Community leader not found")

            # Retrieve the wallet ID of the community leader
            result_wallet = await db.execute(
                select(UserWallet.wallet_id)
                .where(UserWallet.user_id == leader_user_id)
            )

            wallet_id = result_wallet.scalar_one_or_none()

            if not wallet_id:
                raise HTTPException(status_code=404, detail="Wallet not found for the community leader")

            # Update the reward_points in the Wallet table
            stmt = (
                update(Wallet)
                .where(Wallet.wallet_id == wallet_id)
                .values(reward_points=new_reward_points)
            )

            # Execute the update statement
            await db.execute(stmt)
            await db.commit()

            return {"message": "Reward points updated successfully", 'user_id': leader_user_id}

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error updating community leader reward points: {str(e)}")
        



    @staticmethod
    async def get_community_members(db: AsyncSession, community_id: str):
        try:
            query = (
                select(Community)
                .options(
                    joinedload(Community.leader),  # Load leader details
                    joinedload(Community.users)  # Load all members
                )
                .filter(Community.community_id == community_id)
            )

            result = await db.execute(query)
            community = result.scalars().first()

            if not community:
                return None

            return {
                "community_name": community.community_name,
                "leader": {
                    "user_id": community.leader.user_id,
                    "mobile_number": community.leader.mobile_number,
                    "account_type": community.leader.account_type
                } if community.leader else None,
                "members": [
                    {
                        "user_id": member.user_id,
                        "mobile_number": member.mobile_number,
                        "account_type": member.account_type
                    }
                    for member in community.users
                ]
            }

        except Exception as e:
            print(f"Error fetching community members: {e}")
            return None








