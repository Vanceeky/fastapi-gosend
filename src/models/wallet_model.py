from sqlalchemy import (Boolean,
                        Column,
                        DECIMAL,
                        Enum,
                        ForeignKey,
                        String,
                        TEXT,
                        TIMESTAMP)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text

from core.database import Base


class Wallet(Base):
    __tablename__ = "wallets"
    
    wallet_id = Column(String(36), primary_key=True, index=True)
    public_address = Column(TEXT, nullable=False, index=True)
    balance = Column(DECIMAL(10, 2), nullable=False, server_default="0.00", default=0.00)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    
    user_wallets = relationship("UserWallet", back_populates="wallets") 

class WalletExtensions(Base):
    __tablename__ = "wallet_extensions"
    
    wallet_extension_id = Column(String(36), primary_key=True, index=True)
    extension_name = Column(TEXT, nullable=False, index=True)
    extension_type = Column(Enum("monetary"), nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    
    user_wallet_extensions = relationship("UserWalletExtension", back_populates="wallet_extensions")
    