from sqlalchemy import Column, String, ForeignKey, Integer, Float, Enum, TIMESTAMP
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship

from core.database import Base

from uuid import uuid4



class ActivationHistory(Base):
    __tablename__ = "activation_history"

    transaction_id = Column(String(20), primary_key=True, index=True)

    # User ID to be activated
    user_id = Column(String(36), nullable=False)

    # The user who performed the activation
    activated_by = Column(String(36), nullable=False)  # New field

    # Receiver ID, ADMIN DEFAULT
    receiver_id = Column(String(36), nullable=False)

    # topwallet reference id
    reference_id = Column(String(36), nullable=False, index=True)  # No ForeignKey constraint

    amount = Column(Float, nullable=False)

    sender_name = Column(String(255), nullable=False)
    receiver_name = Column(String(255), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)

    activated_in = Column(Enum('mobile', 'web'), server_default='mobile', default='mobile', nullable=False)

    status = Column(Enum('pending', 'completed', 'failed', 'refunded'), nullable=False, server_default='pending', default='pending')


    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())
