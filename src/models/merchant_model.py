from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, Enum, Boolean, Float, DECIMAL
from sqlalchemy.orm import relationship
from core.database import Base

from sqlalchemy.sql import func, text
from uuid import uuid4


class Merchant(Base):
    __tablename__ = 'merchants'

    merchant_id = Column(String(36), primary_key=True, default= lambda: str(uuid4()), index=True)

    mobile_number = Column(String(36), ForeignKey('users.mobile_number', ondelete="cascade", onupdate="cascade"), unique=True, nullable=False)
    merchant_wallet = Column(DECIMAL(10, 2), nullable=False, server_default="0.00", default=0.00)
    qr_code_url = Column(String(3000), nullable=True)  # Nullable to handle merchants without a QR code

    business_name = Column(String(255), nullable=False)
    business_type = Column(String(100), nullable=False)

    discount = Column(Float, nullable=True)

    status = Column(Boolean, nullable=False, server_default=text('false'), default=False)

    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())

    user = relationship("User", back_populates="merchants")

    merchant_details = relationship("MerchantDetails", back_populates="merchant")
    merchant_referrals = relationship("MerchantReferral", foreign_keys="[MerchantReferral.referred_to]", back_populates="referred_to_merchant")

    # Relationship to purchases
    purchases = relationship("MerchantPurchase", back_populates="merchant")


class MerchantDetails(Base):
    __tablename__ = 'merchant_details'

    merchant_id = Column(String(36), ForeignKey('merchants.merchant_id', ondelete="cascade", onupdate="cascade"), primary_key=True, index=True)

    latitude = Column(String(255), nullable=False)
    longitude = Column(String(255), nullable=False)

    contact_number = Column(String(13), nullable=False)
    business_email = Column(String(255), nullable=False)
   # password = Column(String(1000), nullable=False)

    region = Column(String(100), nullable=False)
    province = Column(String(100), nullable=False)
    municipality_city = Column(String(100), nullable=False)
    barangay = Column(String(100), nullable=False)
    street = Column(String(100), nullable=True)

    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())

    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())

    merchant = relationship("Merchant", back_populates="merchant_details")
    #merchant_referrals = relationship("MerchantReferral", foreign_keys="[MerchantReferral.referred_to]", back_populates="referred_to_merchant")