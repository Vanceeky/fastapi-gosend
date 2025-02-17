from sqlalchemy import (Boolean, Column, ForeignKey, String, TEXT, TIMESTAMP, Integer, Enum)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
from core.database import Base
from models.investor_model import Investor

#from models.merchant_purchase_history_model import MerchantPurchaseHistory



class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String(36), primary_key=True, index=True)
    mobile_number = Column(String(11), unique=True, nullable=False, index=True)

    account_type = Column(Enum('MEMBER', 'MERCHANT', 'INVESTOR', 'HUB', 'LEADER', 'ADMIN'), default='MEMBER', nullable=False)
    referral_id = Column(String(12), unique=True, nullable=True)

    #email_address = Column(String(128), unique=True, nullable=False, index=True)
    #hashed_password = Column(TEXT, nullable=False)
    mpin = Column(String(255), nullable=True)

    is_kyc_verified = Column(Boolean, nullable=False, server_default=text('false'), default=False)

    is_activated = Column(Boolean, nullable=False, server_default=text('false'), default=False)
    community_id = Column(String(36), ForeignKey("community.community_id"), nullable=True)


    status = Column(Boolean, nullable=False, server_default=text('false'), default=False)
    
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())
    
    user_address = relationship("UserAddress", back_populates="users", uselist=False)
    user_details = relationship("UserDetail", back_populates="users", uselist=False)
    user_wallets = relationship("UserWallet", back_populates="users", uselist=True)
    merchants = relationship("Merchant", back_populates="user")
    
    # Define the back relationship from User to Referral
    referred_by = relationship("Referral", foreign_keys="[Referral.referred_by]", back_populates="referred_by_user", uselist=True)
    referred_to = relationship("Referral", foreign_keys="[Referral.referred_to]", back_populates="referred_to_user", uselist=True)
    
    # Merchant referrals relationships
    merchant_referred_by = relationship("MerchantReferral", foreign_keys="[MerchantReferral.referred_by]", back_populates="referred_by_user", uselist=True)
    
    #community = relationship("Community", back_populates="user", uselist=False, foreign_keys=[community_id])

    # Relationship to the community the user belongs to
    community = relationship("Community", back_populates="users", foreign_keys=[community_id])

    # Relationship to the community the user leads (if they are a leader)
    led_community = relationship("Community", back_populates="leader", foreign_keys="[Community.leader_mobile_number]", uselist=False)

    investor = relationship("Investor", back_populates="user", uselist=False)
    
    hub = relationship('Hub', back_populates="user", uselist=False)
    
    earned_commissions = relationship("Commission", foreign_keys="[Commission.user_id]", back_populates="user")

    # Relationship to purchases
    purchases = relationship("MerchantPurchase", back_populates="customer")

    # relationship to admin accounts
    admin_account = relationship("AdminAccount", back_populates="user")
    


    
class UserAddress(Base):
    __tablename__ = "user_address"
    
    user_id = Column(String(36), ForeignKey('users.user_id', ondelete="cascade", onupdate="cascade"), primary_key=True, index=True)
    house_number = Column(TEXT, nullable=True)
    street_name = Column(TEXT, nullable=True)
    barangay = Column(TEXT, nullable=True)
    city = Column(TEXT, nullable=True)
    province = Column(TEXT, nullable=True)
    region = Column(TEXT, nullable=True)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    
    users = relationship("User", back_populates="user_address")
    
class UserDetail(Base):
    __tablename__ = "user_details"
    
    user_id = Column(String(36), ForeignKey('users.user_id', ondelete="cascade", onupdate="cascade"), primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    suffix_name = Column(String(50), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    
    users = relationship("User", back_populates="user_details")
    
class UserWallet(Base):
    __tablename__ = "user_wallets"
    
    wallet_id = Column(String(36), ForeignKey('wallets.wallet_id', ondelete="cascade", onupdate="cascade"), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey('users.user_id'), nullable=False, index=True)
    is_primary = Column(Boolean, nullable=False, server_default=text('false'), default=False)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    
    users = relationship("User", back_populates="user_wallets")
    wallets = relationship("Wallet", back_populates="user_wallets", uselist=True)
    extensions = relationship("UserWalletExtension", back_populates="user_wallets", uselist=True)
    
class UserWalletExtension(Base):
    __tablename__ = "user_wallet_extensions"
    
    user_wallet_extension_id = Column(String(36), primary_key=True, index=True)

    extension_id = Column(String(36), ForeignKey('wallet_extensions.wallet_extension_id', ondelete="cascade", onupdate="cascade"), nullable=False, index=True)

    wallet_id = Column(String(36), ForeignKey('user_wallets.wallet_id', ondelete="cascade", onupdate="cascade"), nullable=False, index=True)

    external_id = Column(TEXT, nullable=False, index=True)



    user_wallets = relationship("UserWallet", back_populates="extensions")
    wallet_extensions = relationship("WalletExtensions", back_populates="user_wallet_extensions", uselist=True)