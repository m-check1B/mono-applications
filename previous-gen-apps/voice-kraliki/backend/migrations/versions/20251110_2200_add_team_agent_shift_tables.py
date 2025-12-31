"""Add team, agent, and shift management tables

Revision ID: 20251110_2200
Revises: 20251110_2100
Create Date: 2025-11-10 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251110_2200'
down_revision: Union[str, None] = '20251110_2100'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create teams table
    op.create_table('teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_team_id', sa.Integer(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('manager_id', sa.Integer(), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'),
        sa.Column('working_hours', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('working_days', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('total_agents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('active_agents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_calls_handled', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('average_handle_time', sa.Float(), nullable=True),
        sa.Column('satisfaction_score', sa.Float(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['parent_team_id'], ['teams.id']),
        sa.ForeignKeyConstraint(['manager_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teams_id'), 'teams', ['id'], unique=False)

    # Create team_members table
    op.create_table('team_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='agent'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('joined_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_team_members_id'), 'team_members', ['id'], unique=False)

    # Create agent_profiles table
    op.create_table('agent_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('employee_id', sa.String(length=50), nullable=True),
        sa.Column('display_name', sa.String(length=200), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('extension', sa.String(length=10), nullable=True),
        sa.Column('current_status', sa.String(length=50), nullable=False, server_default='offline'),
        sa.Column('status_since', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_activity_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('skills', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('languages', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('max_concurrent_calls', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('total_calls_handled', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_talk_time_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('average_handle_time_seconds', sa.Integer(), nullable=True),
        sa.Column('average_wait_time_seconds', sa.Integer(), nullable=True),
        sa.Column('satisfaction_score', sa.Float(), nullable=True),
        sa.Column('calls_today', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('adherence_score', sa.Float(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('first_call_resolution_rate', sa.Float(), nullable=True),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('available_for_calls', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('auto_answer', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('max_call_duration_seconds', sa.Integer(), nullable=True),
        sa.Column('preferred_campaigns', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
        sa.UniqueConstraint('employee_id')
    )
    op.create_index(op.f('ix_agent_profiles_id'), 'agent_profiles', ['id'], unique=False)

    # Create shifts table
    op.create_table('shifts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('shift_date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='scheduled'),
        sa.Column('actual_start_time', sa.DateTime(), nullable=True),
        sa.Column('actual_end_time', sa.DateTime(), nullable=True),
        sa.Column('clock_in_time', sa.DateTime(), nullable=True),
        sa.Column('clock_out_time', sa.DateTime(), nullable=True),
        sa.Column('break_duration_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('actual_break_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('recurrence_pattern', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['agent_id'], ['agent_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shifts_id'), 'shifts', ['id'], unique=False)
    op.create_index(op.f('ix_shifts_shift_date'), 'shifts', ['shift_date'], unique=False)

    # Create agent_performance table
    op.create_table('agent_performance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('period_date', sa.Date(), nullable=False),
        sa.Column('period_type', sa.String(length=20), nullable=False, server_default='daily'),
        sa.Column('total_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('answered_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('missed_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('outbound_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('inbound_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_talk_time', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_hold_time', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_wait_time', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_after_call_work', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_idle_time', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('average_handle_time', sa.Integer(), nullable=True),
        sa.Column('average_talk_time', sa.Integer(), nullable=True),
        sa.Column('average_speed_to_answer', sa.Integer(), nullable=True),
        sa.Column('customer_satisfaction_score', sa.Float(), nullable=True),
        sa.Column('net_promoter_score', sa.Float(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('first_call_resolution_rate', sa.Float(), nullable=True),
        sa.Column('calls_per_hour', sa.Float(), nullable=True),
        sa.Column('occupancy_rate', sa.Float(), nullable=True),
        sa.Column('utilization_rate', sa.Float(), nullable=True),
        sa.Column('scheduled_hours', sa.Float(), nullable=False, server_default='0'),
        sa.Column('actual_hours', sa.Float(), nullable=False, server_default='0'),
        sa.Column('adherence_percentage', sa.Float(), nullable=True),
        sa.Column('dispositions', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['agent_id'], ['agent_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_performance_id'), 'agent_performance', ['id'], unique=False)
    op.create_index(op.f('ix_agent_performance_period_date'), 'agent_performance', ['period_date'], unique=False)

    # Create team_performance table
    op.create_table('team_performance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('period_date', sa.Date(), nullable=False),
        sa.Column('period_type', sa.String(length=20), nullable=False, server_default='daily'),
        sa.Column('total_agents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('active_agents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('agents_on_call', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('calls_answered', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('calls_abandoned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('average_wait_time_seconds', sa.Integer(), nullable=True),
        sa.Column('service_level_percentage', sa.Float(), nullable=True),
        sa.Column('average_csat', sa.Float(), nullable=True),
        sa.Column('average_quality_score', sa.Float(), nullable=True),
        sa.Column('average_fcr_rate', sa.Float(), nullable=True),
        sa.Column('total_handle_time_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('average_handle_time_seconds', sa.Integer(), nullable=True),
        sa.Column('occupancy_rate', sa.Float(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_team_performance_id'), 'team_performance', ['id'], unique=False)
    op.create_index(op.f('ix_team_performance_period_date'), 'team_performance', ['period_date'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_team_performance_period_date'), table_name='team_performance')
    op.drop_index(op.f('ix_team_performance_id'), table_name='team_performance')
    op.drop_table('team_performance')

    op.drop_index(op.f('ix_agent_performance_period_date'), table_name='agent_performance')
    op.drop_index(op.f('ix_agent_performance_id'), table_name='agent_performance')
    op.drop_table('agent_performance')

    op.drop_index(op.f('ix_shifts_shift_date'), table_name='shifts')
    op.drop_index(op.f('ix_shifts_id'), table_name='shifts')
    op.drop_table('shifts')

    op.drop_index(op.f('ix_agent_profiles_id'), table_name='agent_profiles')
    op.drop_table('agent_profiles')

    op.drop_index(op.f('ix_team_members_id'), table_name='team_members')
    op.drop_table('team_members')

    op.drop_index(op.f('ix_teams_id'), table_name='teams')
    op.drop_table('teams')
