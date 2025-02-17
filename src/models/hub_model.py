from sqlalchemy import ForeignKey, Column, String, TIMESTAMP
from core.database import Base

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from uuid import uuid4



class Hub(Base):
    __tablename__ = 'hubs'

    hub_id = Column(String(36), default=lambda: str(uuid4()), primary_key=True, index=True)
    hub_name = Column(String(255), nullable=False)
    hub_address = Column(String(255), nullable=False)

    hub_user = Column(String(36), ForeignKey('users.mobile_number'), unique=True, nullable=False)

    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())

    user = relationship("User", back_populates="hub")