from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime



class CommunityCreate(BaseModel):
    community_name: str
    leader_mobile_number: str

    class Config:
        orm_mode = True
        from_attributes = True


class CommunityResponse(BaseModel):
    community_id: str
    community_name: str
    leader_mobile_number: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class LeaderAddress(BaseModel):
    house_number: Optional[str]
    street_name: Optional[str]
    barangay: Optional[str]
    city: Optional[str]
    province: Optional[str]
    region: Optional[str]

class LeaderDetails(BaseModel):
    user_id: str
    mobile_number: str
    email_address: str
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    suffix_name: Optional[str]
    address: Optional[LeaderAddress]

class CommunityWithLeaderDetailsResponse(BaseModel):
    community_id: str
    community_name: str
    leader_mobile_number: LeaderDetails
    created_at: datetime
    updated_at: datetime


# Schema for a community member
# Schema for a community member
class CommunityMember(BaseModel):
    user_id: str
    mobile_number: str
    account_type: str
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    suffix_name: Optional[str]
    is_activated: bool
    is_kyc_verified: bool

# Schema for the community leader (same structure as a member)
class CommunityLeader(BaseModel):
    user_id: str
    mobile_number: str
    account_type: str
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    suffix_name: Optional[str]
    is_activated: bool
    is_kyc_verified: bool

# Schema for the full community response
class CommunityMembersResponse(BaseModel):
    community_name: str
    leader: Optional[CommunityLeader]  # Leader is optional in case no leader is set
    members: List[CommunityMember] = []  # Defaults to an empty list if no members exist


class LeaderSchema(BaseModel):
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    suffix: Optional[str]

class CommunitySchema(BaseModel):
    community_id: str
    community_name: str
    leader_name: str
    reward_points: float
    number_of_members: int
    date_added: str

    class Config:
        orm_mode = True
        from_attributes = True  # Allows conversion from SQLAlchemy models