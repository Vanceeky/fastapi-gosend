from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Enum
from core.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
from uuid import uuid4



class AdminAccount(Base):
    __tablename__ = 'admin_accounts'
    user_id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid4()))

    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    mobile_number = Column(String(11), ForeignKey('users.mobile_number', ondelete="cascade", onupdate="cascade"), unique=True, nullable=True)

    account_type = Column(Enum('SUPERADMIN', 'ADMIN', 'CUSTOMER_SUPPORT'), nullable=False, server_default=text("'CUSTOMER_SUPPORT'"))

    account_url = Column(String(36), nullable=True)

    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())

    
    #relationships
    user = relationship("User", back_populates="admin_account")