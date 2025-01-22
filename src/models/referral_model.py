from sqlalchemy import Column, TIMESTAMP, String, ForeignKey, Float, Integer
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.sql import func, text
from models.user_model import User




class Referral(Base):
    __tablename__ = 'referrals'

    referral_id = Column(String(36), primary_key=True, index=True)
    
    referred_by = Column(String(36), ForeignKey('users.user_id', ondelete="cascade", onupdate="cascade"), nullable=False, index=True) # user who referred
    
    referred_to = Column(String(36), ForeignKey('users.user_id', ondelete="cascade", onupdate="cascade"), nullable=False, index=True) # user who was referred

    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())

    referred_by_user = relationship("User", foreign_keys=[referred_by], back_populates="referred_by", uselist=False)
    referred_to_user = relationship("User", foreign_keys=[referred_to], back_populates="referred_to", uselist=False)


class Commission(Base):
    __tablename__ = "commission_records"

    commission_id = Column(String(36), primary_key=True, index=True)

    user_id = Column(String(36), ForeignKey('users.user_id', ondelete="cascade", onupdate="cascade"), nullable=False) # use who earns the commission

    transaction_type = Column(String(50), nullable=False)
    level = Column(String(50), nullable=False)
    
    amount = Column(Float, nullable=False)

    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())

    # Specify the foreign_keys explicitly to resolve ambiguity
    user = relationship("User", back_populates="earned_commissions", foreign_keys=[user_id])
    



class MerchantReferral(Base):
    __tablename__ = 'merchant_referrals'

    referral_id = Column(String(36), primary_key=True, index=True, nullable=False)

    # User who referred
    referred_by = Column(String(12), ForeignKey('users.referral_id', ondelete="cascade", onupdate="cascade"), nullable=False, index=True)

    # Merchant who was referred
    referred_to = Column(String(36), ForeignKey('merchants.merchant_id', ondelete="cascade", onupdate="cascade"), nullable=False, index=True)

    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())

    referred_by_user = relationship("User", back_populates="merchant_referred_by")
    referred_to_merchant = relationship("Merchant", back_populates="merchant_referrals")
