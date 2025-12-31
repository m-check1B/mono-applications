"""Add queue configuration and SLA metrics tables

Revision ID: 20251111_1200
Revises: 20251110_2300
Create Date: 2025-11-11 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251111_1200'
down_revision = '20251110_2300'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create queue_configs table
    op.create_table(
        'queue_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('campaign_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('routing_strategy', sa.String(length=50), nullable=False, server_default='fifo'),
        sa.Column('priority_weight', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('max_queue_size', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('max_wait_time_seconds', sa.Integer(), nullable=False, server_default='300'),
        sa.Column('sla_answer_time_seconds', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('sla_target_percentage', sa.Float(), nullable=False, server_default='0.80'),
        sa.Column('overflow_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('overflow_queue_id', sa.Integer(), nullable=True),
        sa.Column('overflow_threshold', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('require_skills_match', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('skill_match_threshold', sa.Float(), nullable=False, server_default='0.70'),
        sa.Column('enable_callback', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('callback_wait_threshold', sa.Integer(), nullable=False, server_default='180'),
        sa.Column('enable_estimated_wait', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('enable_position_announcements', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('music_on_hold_url', sa.String(length=500), nullable=True),
        sa.Column('announcement_urls', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('business_hours', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['overflow_queue_id'], ['queue_configs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_queue_configs_id'), 'queue_configs', ['id'], unique=False)

    # Create queue_sla_metrics table
    op.create_table(
        'queue_sla_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('queue_config_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('total_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('answered_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('abandoned_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('calls_within_sla', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('sla_compliance_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('average_wait_seconds', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('max_wait_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('median_wait_seconds', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('average_answer_seconds', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('abandon_rate_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('average_abandon_time_seconds', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('service_level_20s', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('service_level_30s', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('service_level_60s', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('average_handle_time_seconds', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('occupancy_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['queue_config_id'], ['queue_configs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_queue_sla_metrics_id'), 'queue_sla_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_queue_sla_metrics_period_start'), 'queue_sla_metrics', ['period_start'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_queue_sla_metrics_period_start'), table_name='queue_sla_metrics')
    op.drop_index(op.f('ix_queue_sla_metrics_id'), table_name='queue_sla_metrics')
    op.drop_table('queue_sla_metrics')
    op.drop_index(op.f('ix_queue_configs_id'), table_name='queue_configs')
    op.drop_table('queue_configs')
