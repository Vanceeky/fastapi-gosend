from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

# RewardHistory model
class RewardHistory(Base):
    __tablename__ = "reward_history"

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String, unique=True, index=True)
    reward_points = Column(Float, nullable=False)
    reward_date = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships to other tables
    activation = relationship("ActivationHistory", back_populates="reward", uselist=False)
    purchase = relationship("MerchantPurchaseHistory", back_populates="reward", uselist=False)
    transaction = relationship("TransactionH", back_populates="reward", uselist=False)

# ActivationHistory model
class ActivationHistory(Base):
    __tablename__ = "activation_history"

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String, unique=True, index=True)
    details = Column(String, nullable=True)

    # Foreign key to RewardHistory
    reward_id = Column(Integer, ForeignKey("reward_history.id"))
    reward = relationship("RewardHistory", back_populates="activation")

# PurchaseHistory model
class PurchaseHistory(Base):
    __tablename__ = "purchase_history"

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String, unique=True, index=True)
    details = Column(String, nullable=True)

    # Foreign key to RewardHistory
    reward_id = Column(Integer, ForeignKey("reward_history.id"))
    reward = relationship("RewardHistory", back_populates="purchase")

# TransactionHistory model
class TransactionHistory(Base):
    __tablename__ = "transaction_history"

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String, unique=True, index=True)
    details = Column(String, nullable=True)

    # Foreign key to RewardHistory
    reward_id = Column(Integer, ForeignKey("reward_history.id"))
    reward = relationship("RewardHistory", back_populates="transaction")
