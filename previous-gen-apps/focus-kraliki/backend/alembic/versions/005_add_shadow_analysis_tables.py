"""add shadow analysis tables

Revision ID: 005
Revises: 004
Create Date: 2025-11-11 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create shadow_profile table
    op.create_table('shadow_profile',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('archetype', sa.String(length=50), nullable=False),
        sa.Column('unlock_day', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('total_days', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('insights_data', sa.JSON(), nullable=True),
        sa.Column('patterns', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shadow_profile_id'), 'shadow_profile', ['id'], unique=False)
    op.create_index(op.f('ix_shadow_profile_user_id'), 'shadow_profile', ['user_id'], unique=False)

    # Create shadow_insight table
    op.create_table('shadow_insight',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('profile_id', sa.String(), nullable=False),
        sa.Column('day', sa.Integer(), nullable=False),
        sa.Column('insight_type', sa.String(length=50), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('unlocked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('unlocked_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['profile_id'], ['shadow_profile.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shadow_insight_id'), 'shadow_insight', ['id'], unique=False)
    op.create_index(op.f('ix_shadow_insight_profile_id'), 'shadow_insight', ['profile_id'], unique=False)
    op.create_index(op.f('ix_shadow_insight_day'), 'shadow_insight', ['day'], unique=False)
    op.create_index(op.f('ix_shadow_insight_unlocked'), 'shadow_insight', ['unlocked'], unique=False)


def downgrade() -> None:
    # Drop shadow_insight table
    op.drop_index(op.f('ix_shadow_insight_unlocked'), table_name='shadow_insight')
    op.drop_index(op.f('ix_shadow_insight_day'), table_name='shadow_insight')
    op.drop_index(op.f('ix_shadow_insight_profile_id'), table_name='shadow_insight')
    op.drop_index(op.f('ix_shadow_insight_id'), table_name='shadow_insight')
    op.drop_table('shadow_insight')

    # Drop shadow_profile table
    op.drop_index(op.f('ix_shadow_profile_user_id'), table_name='shadow_profile')
    op.drop_index(op.f('ix_shadow_profile_id'), table_name='shadow_profile')
    op.drop_table('shadow_profile')
