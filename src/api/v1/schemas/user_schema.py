from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from utils.responses import datetime_to_str


class UserAddressCreate(BaseModel):
    """
    Pydantic schema for creating a user address.

    Attributes:
        house_number (Optional[str]): The house number of the user.
        street_name (Optional[str]): The street name of the user.
        barangay (Optional[str]): The barangay of the user.
        city (Optional[str]): The city where the user resides.
        province (Optional[str]): The province where the user resides.
        region (Optional[str]): The region where the user resides.
    """
    house_number: Optional[str] = None
    street_name: Optional[str] = None
    barangay: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    region: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True

class UserDetailCreate(BaseModel):
    """
    Pydantic schema for creating user details.

    Attributes:
        first_name (str): The user's first name.
        middle_name (Optional[str]): The user's middle name.
        last_name (str): The user's last name.
        suffix_name (Optional[str]): The user's suffix name, if any.
    """
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    suffix_name: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True

class UserCreate(BaseModel):
    """
    Pydantic schema for creating a user.

    Attributes:
        mobile_number (str): The user's mobile number.
        email_address (str): The user's email address.
        password (str): The user's password.
        user_address (Optional[UserAddressCreate]): The address of the user (optional).
        user_details (Optional[UserDetailCreate]): The details of the user (optional).
    """
    mobile_number: str
    email_address: str
    password: str
    user_address: Optional[UserAddressCreate] = None
    user_details: Optional[UserDetailCreate] = None

    
    #referrer_id: Optional[str] = None
   # unilevel: Optional[int] = None

    class Config:
        orm_mode = True
        from_attributes = True

class UserAddressUpdate(BaseModel):
    """
    Pydantic schema for updating a user address.

    Attributes:
        house_number (Optional[str]): The house number of the user.
        street_name (Optional[str]): The street name of the user.
        barangay (Optional[str]): The barangay of the user.
        city (Optional[str]): The city where the user resides.
        province (Optional[str]): The province where the user resides.
        region (Optional[str]): The region where the user resides.
    """
    house_number: Optional[str] = None
    street_name: Optional[str] = None
    barangay: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    region: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True

class UserDetailUpdate(BaseModel):
    """
    Pydantic schema for updating user details.

    Attributes:
        first_name (Optional[str]): The user's first name.
        middle_name (Optional[str]): The user's middle name.
        last_name (Optional[str]): The user's last name.
        suffix_name (Optional[str]): The user's suffix name.
    """
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    suffix_name: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True

class UserUpdate(BaseModel):
    """
    Pydantic schema for updating a user.

    Attributes:
        mobile_number (Optional[str]): The user's mobile number.
        email_address (Optional[str]): The user's email address.
        password (Optional[str]): The user's password.
        mpin (Optional[str]): The user's MPIN (optional).
        status (Optional[bool]): The user's status (active/inactive).
        user_address (Optional[UserAddressUpdate]): The address of the user (optional).
        user_details (Optional[UserDetailUpdate]): The details of the user (optional).
    """
    # mobile_number: Optional[str] = None
    email_address: Optional[str] = None
    password: Optional[str] = None
    # mpin: Optional[str] = None
    # status: Optional[bool] = None
    user_address: Optional[UserAddressUpdate] = None
    user_details: Optional[UserDetailUpdate] = None

    class Config:
        orm_mode = True
        from_attributes = True

class UserWalletResponse(BaseModel):
    """
    Pydantic schema for user wallet response.

    Attributes:
        wallet_id (str): The wallet ID associated with the user.
        public_address (str): The public address of the wallet.
    """
    wallet_id: str
    public_address: str

    class Config:
        orm_mode = True
        from_attributes = True

class UserResponse(BaseModel):
    """
    Pydantic schema for returning user data in responses.

    Attributes:
        user_id (str): The user's unique identifier.
        mobile_number (str): The user's mobile number.
        email_address (str): The user's email address.
        status (bool): The user's status (active/inactive).
        created_at (str): The timestamp when the user was created (as a string).
        updated_at (str): The timestamp when the user was last updated (as a string).
        user_address (Optional[UserAddressCreate]): The address of the user (optional).
        user_details (Optional[UserDetailCreate]): The details of the user (optional).
        user_wallets (Optional[List[UserWalletResponse]]): A list of user wallets (optional).
    """
    user_id: str
    mobile_number: str
   # email_address: str
    status: bool
    created_at: str
    updated_at: str
    user_address: Optional[UserAddressCreate] = None
    user_details: Optional[UserDetailCreate] = None
    user_wallets: Optional[List[UserWalletResponse]] = []

    class Config:
        orm_mode = True
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        """
        Converts the SQLAlchemy object to the Pydantic response model.

        Args:
            obj: The SQLAlchemy object to convert.

        Returns:
            UserResponse: The converted user response object.
        """
        obj_dict = obj.__dict__

        if 'created_at' in obj_dict:
            obj_dict['created_at'] = datetime_to_str(obj_dict['created_at'])
        if 'updated_at' in obj_dict:
            obj_dict['updated_at'] = datetime_to_str(obj_dict['updated_at'])

        if 'user_wallets' in obj_dict:
            obj_dict['user_wallets'] = [
                UserWalletResponse(
                    wallet_id=user_wallet.wallet_id,
                    public_address=user_wallet.wallets[0].public_address
                )
                for user_wallet in obj_dict['user_wallets']
            ]

        return super().from_orm(obj)




class ProcessAccountInput(BaseModel):
    transaction_reference: str
   # otp_code: str




class User(BaseModel):
    user_id: str
    mobile_number: str
    account_type: str

class UplineResponse(BaseModel):
    user: User
    uplines: List[User]

class DownlineResponse(BaseModel):
    user: User
    downlines: List[User]


class UserSchema(BaseModel):
    user_id: str
    mobile_number: str
    account_type: str
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    suffix: Optional[str]
    status: str  # "activated" or "not activated"


class ReferralDownlineSchema(BaseModel):
    user: UserSchema
    downlines: List[UserSchema]

class ReferralUplineSchema(BaseModel):
    user: UserSchema
    uplines: List[UserSchema]


class InitiateMemberActivation(BaseModel):
    user_id: str
   # otp_code: str

class ProcessMemberActivation(BaseModel):
    reference_id: str
    otp_code: Optional[str]


class UserDetailSchema(BaseModel):
    user_id: str
    name: str  # Full name formatted as "LastName, FirstName MiddleName Suffix"
    mobile_number: str
    community_name: Optional[str] = None

    class Config:
        from_attributes = True  # Enables ORM mode



class MemberAddressSchema(BaseModel):
    house_number: Optional[str] = None
    street_name: Optional[str] = None
    barangay: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    region: Optional[str] = None

class MemberSchema(BaseModel):
    user_id: str
    name: str  # Formatted as "firstname, middlename, lastname, suffix"
    mobile_number: str
    wallet_balance: float
    reward_points: float
    account_type: str
    community_name: Optional[str] = None
    address: str  # Formatted as "house number, streetname, barangay, city, province, region"
    is_kyc_verified: bool
    is_activated: bool
    date_created: str

    class Config:
        from_attributes = True  # Enables ORM mode




class UserInfoResponse(BaseModel):
    user_id: str
    referral_id: str
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    suffix_name: Optional[str] = None
    mobile_number: str
    wallet_balance: Optional[float] = 0.0
    reward_points: Optional[int] = 0
    account_type: str
    community_id: Optional[str] = None
    community_name: Optional[str] = None
    house_number: Optional[str] = None
    street_name: Optional[str] = None
    barangay: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    region: Optional[str] = None
    is_kyc_verified: bool
    is_activated: bool
    date_created: datetime

    class Config:
        from_attributes = True  # Allows conversion from ORM models
