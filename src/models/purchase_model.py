from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Enum, Float
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship
from core.database import Base
from uuid import uuid4



class MerchantPurchase(Base):
    __tablename__ = "merchant_purchase"

    id = Column(String(36), primary_key=True, default= lambda: str(uuid4()), index=True)

    transaction_id = Column(String(36), primary_key=True, index=True)
    

    merchant_id = Column(String(36), ForeignKey('merchants.merchant_id'), nullable=False)

    customer_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)

    #transaction_type = Column(String(50), nullable=False)

    reference_id = Column(String(36), unique=True, index=True)

    extra_metadata = Column(String(255), nullable=True)

    description = Column(String(255), nullable=True)

    amount = Column(Float, nullable=False)

    status = Column(Enum('PENDING', 'COMPLETED', 'FAILED'), nullable=False, server_default=text("'PENDING'"))

    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())

    # relationship
    merchant = relationship("Merchant", back_populates="purchases")
    customer = relationship("User", back_populates="purchases")
