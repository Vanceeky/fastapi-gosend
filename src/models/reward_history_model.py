from uuid import uuid4
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Enum, Float
from sqlalchemy.sql import func, text
from core.database import Base


class RewardHistory(Base):
    __tablename__ = "reward_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()), index=True)

    reference_id = Column(String(36), nullable=False, index=True)  # No ForeignKey constraint
    reward_source_type = Column(String(50), nullable=False)  # Store the model type (e.g., 'merchant_purchase')

    reward_points = Column(Float, nullable=False)
    reward_from = Column(String(36), nullable=False)
    receiver = Column(String(36), nullable=False)

    #status = Column(Enum('PENDING', 'COMPLETED', 'FAILED'), nullable=False, server_default=text("'PENDING'"))

    reward_type = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)

    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())
