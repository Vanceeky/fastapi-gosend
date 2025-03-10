"""initial migration

Revision ID: 2d2722324ab3
Revises: 
Create Date: 2025-02-20 11:31:45.932779

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d2722324ab3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('community',
    sa.Column('community_id', sa.String(length=36), nullable=False),
    sa.Column('community_name', sa.String(length=255), nullable=False),
    sa.Column('reward_points', sa.DECIMAL(precision=10, scale=2), server_default='0.00', nullable=False),
    sa.Column('leader_mobile_number', sa.String(length=11), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['leader_mobile_number'], ['users.mobile_number'], ),
    sa.PrimaryKeyConstraint('community_id'),
    sa.UniqueConstraint('community_name'),
    sa.UniqueConstraint('leader_mobile_number')
    )
    op.create_table('transactions',
    sa.Column('transaction_id', sa.String(length=36), nullable=False),
    sa.Column('sender_id', sa.String(length=36), nullable=False),
    sa.Column('receiver_id', sa.String(length=36), nullable=False),
    sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=50), nullable=False),
    sa.Column('transaction_type', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('sender_name', sa.String(length=255), nullable=False),
    sa.Column('receiver_name', sa.String(length=255), nullable=False),
    sa.Column('status', sa.Enum('pending', 'completed', 'failed', 'refunded'), server_default='pending', nullable=False),
    sa.Column('transaction_reference', sa.String(length=36), nullable=True),
    sa.Column('extra_metadata', sa.String(length=255), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('transaction_id')
    )
    op.create_index(op.f('ix_transactions_receiver_id'), 'transactions', ['receiver_id'], unique=False)
    op.create_index(op.f('ix_transactions_sender_id'), 'transactions', ['sender_id'], unique=False)
    op.create_index(op.f('ix_transactions_transaction_id'), 'transactions', ['transaction_id'], unique=False)
    op.create_table('users',
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('mobile_number', sa.String(length=11), nullable=False),
    sa.Column('account_type', sa.Enum('MEMBER', 'MERCHANT', 'INVESTOR', 'HUB', 'LEADER', 'ADMIN'), nullable=False),
    sa.Column('referral_id', sa.String(length=12), nullable=True),
    sa.Column('mpin', sa.String(length=255), nullable=True),
    sa.Column('is_kyc_verified', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('is_activated', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('community_id', sa.String(length=36), nullable=True),
    sa.Column('status', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['community_id'], ['community.community_id'], ),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('referral_id')
    )
    op.create_index(op.f('ix_users_mobile_number'), 'users', ['mobile_number'], unique=True)
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)
    op.create_table('wallet_extensions',
    sa.Column('wallet_extension_id', sa.String(length=36), nullable=False),
    sa.Column('extension_name', sa.TEXT(), nullable=False),
    sa.Column('extension_type', sa.Enum('monetary'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('wallet_extension_id')
    )
    op.create_index(op.f('ix_wallet_extensions_extension_name'), 'wallet_extensions', ['extension_name'], unique=False)
    op.create_index(op.f('ix_wallet_extensions_wallet_extension_id'), 'wallet_extensions', ['wallet_extension_id'], unique=False)
    op.create_table('wallets',
    sa.Column('wallet_id', sa.String(length=36), nullable=False),
    sa.Column('public_address', sa.TEXT(), nullable=False),
    sa.Column('balance', sa.DECIMAL(precision=10, scale=2), server_default='0.00', nullable=False),
    sa.Column('reward_points', sa.DECIMAL(precision=10, scale=2), server_default='0.00', nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('wallet_id')
    )
    op.create_index(op.f('ix_wallets_public_address'), 'wallets', ['public_address'], unique=False)
    op.create_index(op.f('ix_wallets_wallet_id'), 'wallets', ['wallet_id'], unique=False)
    op.create_table('admin_accounts',
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('username', sa.String(length=255), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('mobile_number', sa.String(length=11), nullable=True),
    sa.Column('account_type', sa.Enum('SUPERADMIN', 'ADMIN', 'CUSTOMER_SUPPORT'), server_default=sa.text("'CUSTOMER_SUPPORT'"), nullable=False),
    sa.Column('account_url', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['mobile_number'], ['users.mobile_number'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('mobile_number'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_admin_accounts_user_id'), 'admin_accounts', ['user_id'], unique=False)
    op.create_table('commission_records',
    sa.Column('commission_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('transaction_type', sa.String(length=50), nullable=False),
    sa.Column('level', sa.String(length=50), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('commission_id')
    )
    op.create_index(op.f('ix_commission_records_commission_id'), 'commission_records', ['commission_id'], unique=False)
    op.create_table('distribution_history',
    sa.Column('distribution_id', sa.String(length=36), nullable=False),
    sa.Column('sponsor', sa.String(length=36), nullable=False),
    sa.Column('receiver', sa.String(length=36), nullable=False),
    sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('type', sa.TEXT(), nullable=False),
    sa.Column('transaction_id', sa.String(length=36), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['transaction_id'], ['transactions.transaction_id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('distribution_id', 'transaction_id')
    )
    op.create_index(op.f('ix_distribution_history_distribution_id'), 'distribution_history', ['distribution_id'], unique=False)
    op.create_index(op.f('ix_distribution_history_receiver'), 'distribution_history', ['receiver'], unique=False)
    op.create_index(op.f('ix_distribution_history_sponsor'), 'distribution_history', ['sponsor'], unique=False)
    op.create_index(op.f('ix_distribution_history_transaction_id'), 'distribution_history', ['transaction_id'], unique=False)
    op.create_table('hubs',
    sa.Column('hub_id', sa.String(length=36), nullable=False),
    sa.Column('hub_name', sa.String(length=255), nullable=False),
    sa.Column('hub_address', sa.String(length=255), nullable=False),
    sa.Column('hub_user', sa.String(length=36), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['hub_user'], ['users.mobile_number'], ),
    sa.PrimaryKeyConstraint('hub_id'),
    sa.UniqueConstraint('hub_user')
    )
    op.create_index(op.f('ix_hubs_hub_id'), 'hubs', ['hub_id'], unique=False)
    op.create_table('investors',
    sa.Column('investor_id', sa.String(length=36), nullable=False),
    sa.Column('investor_user', sa.String(length=11), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['investor_user'], ['users.mobile_number'], ),
    sa.PrimaryKeyConstraint('investor_id'),
    sa.UniqueConstraint('investor_user')
    )
    op.create_index(op.f('ix_investors_investor_id'), 'investors', ['investor_id'], unique=False)
    op.create_table('merchants',
    sa.Column('merchant_id', sa.String(length=36), nullable=False),
    sa.Column('mobile_number', sa.String(length=36), nullable=False),
    sa.Column('merchant_wallet', sa.DECIMAL(precision=10, scale=2), server_default='0.00', nullable=False),
    sa.Column('qr_code_url', sa.String(length=3000), nullable=True),
    sa.Column('business_name', sa.String(length=255), nullable=False),
    sa.Column('business_type', sa.String(length=100), nullable=False),
    sa.Column('discount', sa.Float(), nullable=True),
    sa.Column('status', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['mobile_number'], ['users.mobile_number'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('merchant_id'),
    sa.UniqueConstraint('mobile_number')
    )
    op.create_index(op.f('ix_merchants_merchant_id'), 'merchants', ['merchant_id'], unique=False)
    op.create_table('otp_records',
    sa.Column('otp_id', sa.String(length=36), nullable=False),
    sa.Column('mobile_number', sa.String(length=11), nullable=False),
    sa.Column('otp_code', sa.String(length=6), nullable=False),
    sa.Column('otp_type', sa.String(length=50), nullable=False),
    sa.Column('is_used', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('expired_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['mobile_number'], ['users.mobile_number'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('otp_id')
    )
    op.create_index(op.f('ix_otp_records_mobile_number'), 'otp_records', ['mobile_number'], unique=False)
    op.create_index(op.f('ix_otp_records_otp_id'), 'otp_records', ['otp_id'], unique=False)
    op.create_table('referrals',
    sa.Column('referral_id', sa.String(length=36), nullable=False),
    sa.Column('referred_by', sa.String(length=36), nullable=False),
    sa.Column('referred_to', sa.String(length=36), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['referred_by'], ['users.user_id'], onupdate='cascade', ondelete='cascade'),
    sa.ForeignKeyConstraint(['referred_to'], ['users.user_id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('referral_id')
    )
    op.create_index(op.f('ix_referrals_referral_id'), 'referrals', ['referral_id'], unique=False)
    op.create_index(op.f('ix_referrals_referred_by'), 'referrals', ['referred_by'], unique=False)
    op.create_index(op.f('ix_referrals_referred_to'), 'referrals', ['referred_to'], unique=False)
    op.create_table('reward_history',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('reference_id', sa.String(length=36), nullable=False),
    sa.Column('reward_source_type', sa.String(length=50), nullable=False),
    sa.Column('reward_points', sa.Float(), nullable=False),
    sa.Column('reward_from', sa.String(length=36), nullable=True),
    sa.Column('receiver', sa.String(length=36), nullable=True),
    sa.Column('reward_type', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['receiver'], ['users.user_id'], ),
    sa.ForeignKeyConstraint(['reward_from'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reward_history_id'), 'reward_history', ['id'], unique=False)
    op.create_index(op.f('ix_reward_history_reference_id'), 'reward_history', ['reference_id'], unique=False)
    op.create_table('user_address',
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('house_number', sa.TEXT(), nullable=True),
    sa.Column('street_name', sa.TEXT(), nullable=True),
    sa.Column('barangay', sa.TEXT(), nullable=True),
    sa.Column('city', sa.TEXT(), nullable=True),
    sa.Column('province', sa.TEXT(), nullable=True),
    sa.Column('region', sa.TEXT(), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_user_address_user_id'), 'user_address', ['user_id'], unique=False)
    op.create_table('user_details',
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=False),
    sa.Column('middle_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=False),
    sa.Column('suffix_name', sa.String(length=50), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_user_details_user_id'), 'user_details', ['user_id'], unique=False)
    op.create_table('user_wallets',
    sa.Column('wallet_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('is_primary', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.ForeignKeyConstraint(['wallet_id'], ['wallets.wallet_id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('wallet_id')
    )
    op.create_index(op.f('ix_user_wallets_user_id'), 'user_wallets', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_wallets_wallet_id'), 'user_wallets', ['wallet_id'], unique=False)
    op.create_table('merchant_details',
    sa.Column('merchant_id', sa.String(length=36), nullable=False),
    sa.Column('latitude', sa.String(length=255), nullable=False),
    sa.Column('longitude', sa.String(length=255), nullable=False),
    sa.Column('contact_number', sa.String(length=13), nullable=False),
    sa.Column('business_email', sa.String(length=255), nullable=False),
    sa.Column('region', sa.String(length=100), nullable=False),
    sa.Column('province', sa.String(length=100), nullable=False),
    sa.Column('municipality_city', sa.String(length=100), nullable=False),
    sa.Column('barangay', sa.String(length=100), nullable=False),
    sa.Column('street', sa.String(length=100), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['merchant_id'], ['merchants.merchant_id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('merchant_id')
    )
    op.create_index(op.f('ix_merchant_details_merchant_id'), 'merchant_details', ['merchant_id'], unique=False)
    op.create_table('merchant_purchase',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('transaction_id', sa.String(length=36), nullable=False),
    sa.Column('merchant_id', sa.String(length=36), nullable=False),
    sa.Column('customer_id', sa.String(length=36), nullable=False),
    sa.Column('reference_id', sa.String(length=36), nullable=True),
    sa.Column('extra_metadata', sa.String(length=255), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'COMPLETED', 'FAILED'), server_default=sa.text("'PENDING'"), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['users.user_id'], ),
    sa.ForeignKeyConstraint(['merchant_id'], ['merchants.merchant_id'], ),
    sa.PrimaryKeyConstraint('id', 'transaction_id')
    )
    op.create_index(op.f('ix_merchant_purchase_id'), 'merchant_purchase', ['id'], unique=False)
    op.create_index(op.f('ix_merchant_purchase_reference_id'), 'merchant_purchase', ['reference_id'], unique=True)
    op.create_index(op.f('ix_merchant_purchase_transaction_id'), 'merchant_purchase', ['transaction_id'], unique=False)
    op.create_table('merchant_referrals',
    sa.Column('referral_id', sa.String(length=36), nullable=False),
    sa.Column('referred_by', sa.String(length=12), nullable=False),
    sa.Column('referred_to', sa.String(length=36), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['referred_by'], ['users.referral_id'], onupdate='cascade', ondelete='cascade'),
    sa.ForeignKeyConstraint(['referred_to'], ['merchants.merchant_id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('referral_id')
    )
    op.create_index(op.f('ix_merchant_referrals_referral_id'), 'merchant_referrals', ['referral_id'], unique=False)
    op.create_index(op.f('ix_merchant_referrals_referred_by'), 'merchant_referrals', ['referred_by'], unique=False)
    op.create_index(op.f('ix_merchant_referrals_referred_to'), 'merchant_referrals', ['referred_to'], unique=False)
    op.create_table('user_wallet_extensions',
    sa.Column('user_wallet_extension_id', sa.String(length=36), nullable=False),
    sa.Column('extension_id', sa.String(length=36), nullable=False),
    sa.Column('wallet_id', sa.String(length=36), nullable=False),
    sa.Column('external_id', sa.TEXT(), nullable=False),
    sa.ForeignKeyConstraint(['extension_id'], ['wallet_extensions.wallet_extension_id'], onupdate='cascade', ondelete='cascade'),
    sa.ForeignKeyConstraint(['wallet_id'], ['user_wallets.wallet_id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('user_wallet_extension_id')
    )
    op.create_index(op.f('ix_user_wallet_extensions_extension_id'), 'user_wallet_extensions', ['extension_id'], unique=False)
    op.create_index(op.f('ix_user_wallet_extensions_external_id'), 'user_wallet_extensions', ['external_id'], unique=False)
    op.create_index(op.f('ix_user_wallet_extensions_user_wallet_extension_id'), 'user_wallet_extensions', ['user_wallet_extension_id'], unique=False)
    op.create_index(op.f('ix_user_wallet_extensions_wallet_id'), 'user_wallet_extensions', ['wallet_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_wallet_extensions_wallet_id'), table_name='user_wallet_extensions')
    op.drop_index(op.f('ix_user_wallet_extensions_user_wallet_extension_id'), table_name='user_wallet_extensions')
    op.drop_index(op.f('ix_user_wallet_extensions_external_id'), table_name='user_wallet_extensions')
    op.drop_index(op.f('ix_user_wallet_extensions_extension_id'), table_name='user_wallet_extensions')
    op.drop_table('user_wallet_extensions')
    op.drop_index(op.f('ix_merchant_referrals_referred_to'), table_name='merchant_referrals')
    op.drop_index(op.f('ix_merchant_referrals_referred_by'), table_name='merchant_referrals')
    op.drop_index(op.f('ix_merchant_referrals_referral_id'), table_name='merchant_referrals')
    op.drop_table('merchant_referrals')
    op.drop_index(op.f('ix_merchant_purchase_transaction_id'), table_name='merchant_purchase')
    op.drop_index(op.f('ix_merchant_purchase_reference_id'), table_name='merchant_purchase')
    op.drop_index(op.f('ix_merchant_purchase_id'), table_name='merchant_purchase')
    op.drop_table('merchant_purchase')
    op.drop_index(op.f('ix_merchant_details_merchant_id'), table_name='merchant_details')
    op.drop_table('merchant_details')
    op.drop_index(op.f('ix_user_wallets_wallet_id'), table_name='user_wallets')
    op.drop_index(op.f('ix_user_wallets_user_id'), table_name='user_wallets')
    op.drop_table('user_wallets')
    op.drop_index(op.f('ix_user_details_user_id'), table_name='user_details')
    op.drop_table('user_details')
    op.drop_index(op.f('ix_user_address_user_id'), table_name='user_address')
    op.drop_table('user_address')
    op.drop_index(op.f('ix_reward_history_reference_id'), table_name='reward_history')
    op.drop_index(op.f('ix_reward_history_id'), table_name='reward_history')
    op.drop_table('reward_history')
    op.drop_index(op.f('ix_referrals_referred_to'), table_name='referrals')
    op.drop_index(op.f('ix_referrals_referred_by'), table_name='referrals')
    op.drop_index(op.f('ix_referrals_referral_id'), table_name='referrals')
    op.drop_table('referrals')
    op.drop_index(op.f('ix_otp_records_otp_id'), table_name='otp_records')
    op.drop_index(op.f('ix_otp_records_mobile_number'), table_name='otp_records')
    op.drop_table('otp_records')
    op.drop_index(op.f('ix_merchants_merchant_id'), table_name='merchants')
    op.drop_table('merchants')
    op.drop_index(op.f('ix_investors_investor_id'), table_name='investors')
    op.drop_table('investors')
    op.drop_index(op.f('ix_hubs_hub_id'), table_name='hubs')
    op.drop_table('hubs')
    op.drop_index(op.f('ix_distribution_history_transaction_id'), table_name='distribution_history')
    op.drop_index(op.f('ix_distribution_history_sponsor'), table_name='distribution_history')
    op.drop_index(op.f('ix_distribution_history_receiver'), table_name='distribution_history')
    op.drop_index(op.f('ix_distribution_history_distribution_id'), table_name='distribution_history')
    op.drop_table('distribution_history')
    op.drop_index(op.f('ix_commission_records_commission_id'), table_name='commission_records')
    op.drop_table('commission_records')
    op.drop_index(op.f('ix_admin_accounts_user_id'), table_name='admin_accounts')
    op.drop_table('admin_accounts')
    op.drop_index(op.f('ix_wallets_wallet_id'), table_name='wallets')
    op.drop_index(op.f('ix_wallets_public_address'), table_name='wallets')
    op.drop_table('wallets')
    op.drop_index(op.f('ix_wallet_extensions_wallet_extension_id'), table_name='wallet_extensions')
    op.drop_index(op.f('ix_wallet_extensions_extension_name'), table_name='wallet_extensions')
    op.drop_table('wallet_extensions')
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_index(op.f('ix_users_mobile_number'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_transactions_transaction_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_sender_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_receiver_id'), table_name='transactions')
    op.drop_table('transactions')
    op.drop_table('community')
    # ### end Alembic commands ###
