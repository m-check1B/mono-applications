"""add ai billing fields to user

Revision ID: 007
Revises: 006
Create Date: 2025-11-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add AI billing and BYOK fields to user table
    op.add_column('user', sa.Column('openRouterApiKey', sa.String(), nullable=True))
    op.add_column('user', sa.Column('usageCount', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('user', sa.Column('isPremium', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('user', sa.Column('stripeCustomerId', sa.String(), nullable=True))
    op.add_column('user', sa.Column('stripeSubscriptionId', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove AI billing and BYOK fields from user table
    op.drop_column('user', 'stripeSubscriptionId')
    op.drop_column('user', 'stripeCustomerId')
    op.drop_column('user', 'isPremium')
    op.drop_column('user', 'usageCount')
    op.drop_column('user', 'openRouterApiKey')
