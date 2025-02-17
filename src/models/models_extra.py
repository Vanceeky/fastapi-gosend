class RewardHistory(Base):
    __tablename__ = "reward_history"

    id = Column(String(36), primary_key=True, index=True)
    
    reference_id = Column(String(36), unique=True, index=True)

    reward_points = Column(Float, nullable=False)

    reward_from = Column(String(36), nullable=False)
    
    receiver = Column(String(36), nullable=False)

    status = Column(Enum('PENDING', 'COMPLETED', 'FAILED'), nullable=False, server_default=text("'PENDING'"))

    reward_type = Column(String(50), nullable=False)

    description = Column(String(255), nullable=True)

    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())

    # Relationships to other tables
    activation = relationship("ActivationHistory", back_populates="reward", uselist=False)
    purchase = relationship("MerchantPurchaseHistory", back_populates="reward", uselist=False)
    transaction = relationship("Transaction", back_populates="reward", uselist=False)




class ActivationHistory(Base):
    __tablename__ = "activation_history"

    id = Column(Integer, primary_key=True, index=True)
    
    # User ID to be activated
    user_id = Column(String(36), nullable=False)
    receiver_id = Column(String(36), nullable=False)

    # Topwallet reference ID
    reference_id = Column(String(36), ForeignKey('reward_history.reference_id'), unique=True, index=True)

    amount = Column(Float, nullable=False)

    activated_in = Column(Enum('mobile', 'web'), server_default='mobile', default='mobile', nullable=False)

    details = Column(String(155), nullable=True)

    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())

    # Relationship with RewardHistory
    reward = relationship("RewardHistory", back_populates="activation", uselist=False)


class MerchantPurchaseHistory(Base):
    __tablename__ = "merchant_purchase_history"

    id = Column(String(36), primary_key=True, index=True)

    # Foreign keys
    merchant_id = Column(String(36), ForeignKey('merchants.merchant_id'), nullable=False)
    customer_id = Column(String(36), ForeignKey('users.user_id'), nullable=False)

    reference_id = Column(String(36), unique=True, index=True)

    details = Column(String(155), nullable=True)
    
    amount = Column(Float, nullable=False)

    status = Column(Enum('PENDING', 'COMPLETED', 'FAILED'), nullable=False, server_default=text("'PENDING'"))

    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'), default=func.now())

    # Relationship with RewardHistory
    reward = relationship("RewardHistory", back_populates="purchase", uselist=False)

    # Relationships
    merchant = relationship("Merchant", back_populates="purchases")
    customer = relationship("User", back_populates="purchases")