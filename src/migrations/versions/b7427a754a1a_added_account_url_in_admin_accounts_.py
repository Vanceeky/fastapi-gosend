"""added account url in admin accounts model

Revision ID: b7427a754a1a
Revises: 6cbb153afaac
Create Date: 2025-02-06 13:42:37.695679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7427a754a1a'
down_revision: Union[str, None] = '6cbb153afaac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('admin_accounts', sa.Column('account_url', sa.String(length=36), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('admin_accounts', 'account_url')
    # ### end Alembic commands ###
