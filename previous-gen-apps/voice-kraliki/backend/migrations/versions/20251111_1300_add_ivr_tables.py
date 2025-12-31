"""Add IVR (Interactive Voice Response) tables

Revision ID: 20251111_1300
Revises: 20251111_1200
Create Date: 2025-11-11 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251111_1300'
down_revision = '20251111_1200'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ivr_flows table
    op.create_table(
        'ivr_flows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=True),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('entry_node_id', sa.String(length=100), nullable=False),
        sa.Column('nodes', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('default_language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('max_retries', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('timeout_seconds', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('inter_digit_timeout', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('default_voice', sa.String(length=50), nullable=True),
        sa.Column('default_tts_provider', sa.String(length=50), nullable=True),
        sa.Column('invalid_input_message', sa.Text(), nullable=True),
        sa.Column('timeout_message', sa.Text(), nullable=True),
        sa.Column('error_node_id', sa.String(length=100), nullable=True),
        sa.Column('total_sessions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completed_sessions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('abandoned_sessions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('average_duration_seconds', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ivr_flows_id'), 'ivr_flows', ['id'], unique=False)
    op.create_index(op.f('ix_ivr_flows_name'), 'ivr_flows', ['name'], unique=False)
    op.create_index('ix_ivr_flows_active_name', 'ivr_flows', ['is_active', 'name'], unique=False)

    # Create ivr_sessions table
    op.create_table(
        'ivr_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('flow_id', sa.Integer(), nullable=False),
        sa.Column('call_sid', sa.String(length=100), nullable=False),
        sa.Column('caller_phone', sa.String(length=50), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='in_progress'),
        sa.Column('current_node_id', sa.String(length=100), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('variables', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('node_history', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('input_history', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('exit_node_id', sa.String(length=100), nullable=True),
        sa.Column('exit_reason', sa.String(length=100), nullable=True),
        sa.Column('transferred_to', sa.String(length=100), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.ForeignKeyConstraint(['flow_id'], ['ivr_flows.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ivr_sessions_id'), 'ivr_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_ivr_sessions_call_sid'), 'ivr_sessions', ['call_sid'], unique=True)
    op.create_index(op.f('ix_ivr_sessions_flow_id'), 'ivr_sessions', ['flow_id'], unique=False)
    op.create_index(op.f('ix_ivr_sessions_started_at'), 'ivr_sessions', ['started_at'], unique=False)
    op.create_index('ix_ivr_sessions_flow_started', 'ivr_sessions', ['flow_id', 'started_at'], unique=False)

    # Create ivr_analytics table
    op.create_table(
        'ivr_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('flow_id', sa.Integer(), nullable=False),
        sa.Column('node_id', sa.String(length=100), nullable=False),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('total_visits', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('unique_sessions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_inputs', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('valid_inputs', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('invalid_inputs', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('timeout_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('transition_counts', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('average_duration_seconds', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('abandoned_from_node', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['flow_id'], ['ivr_flows.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ivr_analytics_id'), 'ivr_analytics', ['id'], unique=False)
    op.create_index(op.f('ix_ivr_analytics_flow_id'), 'ivr_analytics', ['flow_id'], unique=False)
    op.create_index(op.f('ix_ivr_analytics_node_id'), 'ivr_analytics', ['node_id'], unique=False)
    op.create_index(op.f('ix_ivr_analytics_period_start'), 'ivr_analytics', ['period_start'], unique=False)
    op.create_index('ix_ivr_analytics_flow_node_period', 'ivr_analytics', ['flow_id', 'node_id', 'period_start'], unique=False)


def downgrade() -> None:
    # Drop ivr_analytics table
    op.drop_index('ix_ivr_analytics_flow_node_period', table_name='ivr_analytics')
    op.drop_index(op.f('ix_ivr_analytics_period_start'), table_name='ivr_analytics')
    op.drop_index(op.f('ix_ivr_analytics_node_id'), table_name='ivr_analytics')
    op.drop_index(op.f('ix_ivr_analytics_flow_id'), table_name='ivr_analytics')
    op.drop_index(op.f('ix_ivr_analytics_id'), table_name='ivr_analytics')
    op.drop_table('ivr_analytics')

    # Drop ivr_sessions table
    op.drop_index('ix_ivr_sessions_flow_started', table_name='ivr_sessions')
    op.drop_index(op.f('ix_ivr_sessions_started_at'), table_name='ivr_sessions')
    op.drop_index(op.f('ix_ivr_sessions_flow_id'), table_name='ivr_sessions')
    op.drop_index(op.f('ix_ivr_sessions_call_sid'), table_name='ivr_sessions')
    op.drop_index(op.f('ix_ivr_sessions_id'), table_name='ivr_sessions')
    op.drop_table('ivr_sessions')

    # Drop ivr_flows table
    op.drop_index('ix_ivr_flows_active_name', table_name='ivr_flows')
    op.drop_index(op.f('ix_ivr_flows_name'), table_name='ivr_flows')
    op.drop_index(op.f('ix_ivr_flows_id'), table_name='ivr_flows')
    op.drop_table('ivr_flows')
