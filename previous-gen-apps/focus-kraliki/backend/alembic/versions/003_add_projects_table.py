"""Add projects table

Revision ID: 003
Revises: 002
Create Date: 2025-10-05 18:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    """Create projects table with i18n support."""
    op.create_table(
        'project',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('name_i18n', JSONB, nullable=True),
        sa.Column('description_i18n', JSONB, nullable=True),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('icon', sa.String(), nullable=True),
        sa.Column('userId', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['userId'], ['user.id'], ),
    )

    op.create_index('ix_project_id', 'project', ['id'])
    op.create_index('ix_project_userId', 'project', ['userId'])


def downgrade():
    """Drop projects table."""
    op.drop_index('ix_project_userId', table_name='project')
    op.drop_index('ix_project_id', table_name='project')
    op.drop_table('project')
