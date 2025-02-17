from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, DECIMAL
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.sql import func, text



class Community(Base):
    __tablename__ = 'community'

    community_id = Column(String(36), nullable=False, primary_key=True)
    community_name = Column(String(255), unique=True, nullable=False)
    reward_points = Column(DECIMAL(10, 2), nullable=False, server_default="0.00", default=0.00)
    
    # Leader is identified by their mobile_number
    leader_mobile_number = Column(String(11), ForeignKey('users.mobile_number'), unique=True, nullable=False)

    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())

    # Relationship to the leader (a single User)
    leader = relationship("User", foreign_keys=[leader_mobile_number], back_populates="led_community")

    # Relationship to all users in the community
    users = relationship("User", back_populates="community", foreign_keys="[User.community_id]")