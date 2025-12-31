"""add_file_search_store_table

Revision ID: efc5b5c84ee7
Revises: 008
Create Date: 2025-11-14 11:26:30.039530

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'efc5b5c84ee7'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create file_search_store table
    op.create_table(
        'file_search_store',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('organizationId', sa.String(), nullable=False),
        sa.Column('userId', sa.String(), nullable=True),
        sa.Column('store_name', sa.String(), nullable=False),
        sa.Column('kind', sa.String(), nullable=False),
        sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updatedAt', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_file_search_store_org_kind', 'file_search_store', ['organizationId', 'kind'])
    op.create_index('idx_file_search_store_name', 'file_search_store', ['store_name'], unique=True)
    op.create_index(op.f('ix_file_search_store_id'), 'file_search_store', ['id'], unique=False)
    op.create_index(op.f('ix_file_search_store_organizationId'), 'file_search_store', ['organizationId'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_file_search_store_organizationId'), table_name='file_search_store')
    op.drop_index(op.f('ix_file_search_store_id'), table_name='file_search_store')
    op.drop_index('idx_file_search_store_name', table_name='file_search_store')
    op.drop_index('idx_file_search_store_org_kind', table_name='file_search_store')

    # Drop table
    op.drop_table('file_search_store')
