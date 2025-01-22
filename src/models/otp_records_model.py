from sqlalchemy import Column, String, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from core.database import Base



class OTPRecord(Base):
    __tablename__ = 'otp_records'

    otp_id = Column(String(36), primary_key=True, index=True)
    mobile_number = Column(String(11), ForeignKey('users.mobile_number', ondelete="cascade", onupdate="cascade"), nullable=False, index=True)

    otp_code = Column(String(6), nullable=False)
    otp_type = Column(String(50), nullable=False)
    is_used = Column(Boolean, nullable=False, server_default=text('false'), default=False)
    expired_at = Column(TIMESTAMP, nullable=False)

    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())

    