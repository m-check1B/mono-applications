"""rename metadata to item_metadata

Revision ID: 008
Revises: 007
Create Date: 2025-11-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename metadata column to item_metadata in knowledge_item table
    # This fixes the SQLAlchemy reserved attribute conflict
    op.alter_column('knowledge_item', 'metadata', new_column_name='item_metadata')


def downgrade() -> None:
    # Rename item_metadata back to metadata
    op.alter_column('knowledge_item', 'item_metadata', new_column_name='metadata')
