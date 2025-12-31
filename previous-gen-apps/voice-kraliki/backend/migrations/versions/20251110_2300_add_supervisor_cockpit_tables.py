"""Add supervisor cockpit tables for real-time monitoring and intervention.

Revision ID: 20251110_2300
Revises: 20251110_2200
Create Date: 2025-11-10 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251110_2300'
down_revision: Union[str, None] = '20251110_2200'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create supervisor cockpit tables."""

    # Create call_queue table
    op.create_table(
        'call_queue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=True),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('caller_phone', sa.String(length=50), nullable=True),
        sa.Column('caller_name', sa.String(length=200), nullable=True),
        sa.Column('direction', sa.String(length=20), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='waiting'),
        sa.Column('queue_position', sa.Integer(), nullable=True),
        sa.Column('estimated_wait_time', sa.Integer(), nullable=True),
        sa.Column('queued_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
        sa.Column('answered_at', sa.DateTime(), nullable=True),
        sa.Column('abandoned_at', sa.DateTime(), nullable=True),
        sa.Column('assigned_agent_id', sa.Integer(), nullable=True),
        sa.Column('required_skills', sa.JSON(), nullable=True),
        sa.Column('required_language', sa.String(length=10), nullable=True),
        sa.Column('caller_metadata', sa.JSON(), nullable=True),
        sa.Column('routing_attempts', sa.Integer(), nullable=True, server_default='0'),
        sa.ForeignKeyConstraint(['assigned_agent_id'], ['agent_profiles.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_call_queue_id'), 'call_queue', ['id'], unique=False)
    op.create_index(op.f('ix_call_queue_queued_at'), 'call_queue', ['queued_at'], unique=False)
    op.create_index(op.f('ix_call_queue_status'), 'call_queue', ['status'], unique=False)
    op.create_index('ix_call_queue_status_priority', 'call_queue', ['status', 'priority'], unique=False)
    op.create_index('ix_call_queue_team_status', 'call_queue', ['team_id', 'status'], unique=False)

    # Create active_calls table
    op.create_table(
        'active_calls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('call_sid', sa.String(length=100), nullable=True),
        sa.Column('queue_id', sa.Integer(), nullable=True),
        sa.Column('campaign_id', sa.Integer(), nullable=True),
        sa.Column('agent_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('direction', sa.String(length=20), nullable=True),
        sa.Column('caller_phone', sa.String(length=50), nullable=True),
        sa.Column('caller_name', sa.String(length=200), nullable=True),
        sa.Column('destination_phone', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='ringing'),
        sa.Column('started_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('connected_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('talk_time_seconds', sa.Integer(), nullable=True),
        sa.Column('hold_time_seconds', sa.Integer(), nullable=True),
        sa.Column('is_on_hold', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('hold_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('transfer_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('current_sentiment', sa.String(length=20), nullable=True),
        sa.Column('detected_intent', sa.String(length=100), nullable=True),
        sa.Column('detected_language', sa.String(length=10), nullable=True),
        sa.Column('transcription_url', sa.String(length=500), nullable=True),
        sa.Column('is_being_monitored', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('monitored_by_id', sa.Integer(), nullable=True),
        sa.Column('call_metadata', sa.JSON(), nullable=True),
        sa.Column('recording_url', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agent_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['monitored_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['queue_id'], ['call_queue.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_active_calls_agent_id'), 'active_calls', ['agent_id'], unique=False)
    op.create_index(op.f('ix_active_calls_call_sid'), 'active_calls', ['call_sid'], unique=True)
    op.create_index(op.f('ix_active_calls_id'), 'active_calls', ['id'], unique=False)
    op.create_index(op.f('ix_active_calls_started_at'), 'active_calls', ['started_at'], unique=False)
    op.create_index(op.f('ix_active_calls_status'), 'active_calls', ['status'], unique=False)
    op.create_index('ix_active_calls_agent_status', 'active_calls', ['agent_id', 'status'], unique=False)
    op.create_index('ix_active_calls_team_started', 'active_calls', ['team_id', 'started_at'], unique=False)

    # Create supervisor_interventions table
    op.create_table(
        'supervisor_interventions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('call_id', sa.Integer(), nullable=False),
        sa.Column('supervisor_id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=True),
        sa.Column('intervention_type', sa.String(length=50), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('was_successful', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('customer_notified', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('intervention_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agent_profiles.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['call_id'], ['active_calls.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['supervisor_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_supervisor_interventions_call_id'), 'supervisor_interventions', ['call_id'], unique=False)
    op.create_index(op.f('ix_supervisor_interventions_id'), 'supervisor_interventions', ['id'], unique=False)
    op.create_index(op.f('ix_supervisor_interventions_started_at'), 'supervisor_interventions', ['started_at'], unique=False)
    op.create_index('ix_interventions_supervisor_started', 'supervisor_interventions', ['supervisor_id', 'started_at'], unique=False)

    # Create performance_alerts table
    op.create_table(
        'performance_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=True, server_default='info'),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('agent_id', sa.Integer(), nullable=True),
        sa.Column('call_id', sa.Integer(), nullable=True),
        sa.Column('campaign_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_acknowledged', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_resolved', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('acknowledged_by_id', sa.Integer(), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('threshold_value', sa.Float(), nullable=True),
        sa.Column('actual_value', sa.Float(), nullable=True),
        sa.Column('metric_name', sa.String(length=100), nullable=True),
        sa.Column('alert_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['acknowledged_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['agent_id'], ['agent_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['call_id'], ['active_calls.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_performance_alerts_agent_id'), 'performance_alerts', ['agent_id'], unique=False)
    op.create_index(op.f('ix_performance_alerts_alert_type'), 'performance_alerts', ['alert_type'], unique=False)
    op.create_index(op.f('ix_performance_alerts_created_at'), 'performance_alerts', ['created_at'], unique=False)
    op.create_index(op.f('ix_performance_alerts_id'), 'performance_alerts', ['id'], unique=False)
    op.create_index(op.f('ix_performance_alerts_is_active'), 'performance_alerts', ['is_active'], unique=False)
    op.create_index(op.f('ix_performance_alerts_severity'), 'performance_alerts', ['severity'], unique=False)
    op.create_index(op.f('ix_performance_alerts_team_id'), 'performance_alerts', ['team_id'], unique=False)
    op.create_index('ix_alerts_active_severity', 'performance_alerts', ['is_active', 'severity'], unique=False)
    op.create_index('ix_alerts_team_active', 'performance_alerts', ['team_id', 'is_active'], unique=False)


def downgrade() -> None:
    """Drop supervisor cockpit tables."""
    op.drop_table('performance_alerts')
    op.drop_table('supervisor_interventions')
    op.drop_table('active_calls')
    op.drop_table('call_queue')
