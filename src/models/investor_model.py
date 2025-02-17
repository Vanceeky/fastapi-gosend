from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from core.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
from uuid import uuid4

class Investor(Base):
    __tablename__ = "investors"

    investor_id = Column(String(36), default=lambda: str(uuid4()), primary_key=True, index=True)
    
    # Ensure this matches the existing column in the database
    investor_user = Column(String(11), ForeignKey('users.mobile_number'), unique=True, nullable=False)

    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())

    user = relationship("User", back_populates="investor")
