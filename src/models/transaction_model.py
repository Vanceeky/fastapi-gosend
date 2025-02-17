from sqlalchemy import Column, String, TIMESTAMP, Enum, DECIMAL, TEXT, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
from core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String(36), primary_key=True, index=True)
    
    sender_id = Column(String(36), nullable=False, index=True)
    receiver_id = Column(String(36), nullable=False, index=True)
    amount = Column(DECIMAL(10, 2), nullable=False)

    currency = Column(String(50), nullable=False)

    transaction_type = Column(String(50), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)

    sender_name = Column(String(255), nullable=False)
    receiver_name = Column(String(255), nullable=False)

    status = Column(Enum('pending', 'completed', 'failed', 'refunded'), nullable=False, server_default='pending', default='pending')

    transaction_reference = Column(String(36), nullable=True)
    extra_metadata = Column(String(255), nullable=True)

    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())

    # Relationship with RewardHistory
    #reward = relationship("RewardHistory", back_populates="transaction", uselist=False)


class Distribution(Base):
    __tablename__ = "distribution_history"

    distribution_id = Column(String(36), primary_key=True, index=True)
    sponsor = Column(String(36), nullable=False, index=True)
    receiver = Column(String(36), nullable=False, index=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    type = Column(TEXT, nullable=False)
    transaction_id = Column(String(36), ForeignKey('transactions.transaction_id', ondelete="cascade", onupdate="cascade"), primary_key=True, index=True, nullable=False)


    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())

