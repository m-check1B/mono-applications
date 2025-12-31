"""Add events and time entries tables

Revision ID: 002
Revises: 001
Create Date: 2025-10-05 16:45:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('title_i18n', JSONB, nullable=True),
        sa.Column('description_i18n', JSONB, nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('all_day', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('google_event_id', sa.String(), nullable=True),
        sa.Column('google_calendar_id', sa.String(), nullable=True),
        sa.Column('task_id', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('attendees', JSONB, nullable=True),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('reminder_minutes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
    )
    op.create_index('ix_events_id', 'events', ['id'])
    op.create_index('ix_events_user_id', 'events', ['user_id'])
    op.create_index('ix_events_google_event_id', 'events', ['google_event_id'])
    op.create_index('ix_events_start_time', 'events', ['start_time'])

    # Create time_entries table
    op.create_table(
        'time_entries',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('task_id', sa.String(), nullable=True),
        sa.Column('project_id', sa.String(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('description_i18n', JSONB, nullable=True),
        sa.Column('billable', sa.String(), nullable=False, server_default='false'),
        sa.Column('hourly_rate', sa.Integer(), nullable=True),
        sa.Column('tags', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    )
    op.create_index('ix_time_entries_id', 'time_entries', ['id'])
    op.create_index('ix_time_entries_user_id', 'time_entries', ['user_id'])
    op.create_index('ix_time_entries_task_id', 'time_entries', ['task_id'])
    op.create_index('ix_time_entries_project_id', 'time_entries', ['project_id'])
    op.create_index('ix_time_entries_start_time', 'time_entries', ['start_time'])


def downgrade():
    # Drop time_entries table
    op.drop_index('ix_time_entries_start_time', table_name='time_entries')
    op.drop_index('ix_time_entries_project_id', table_name='time_entries')
    op.drop_index('ix_time_entries_task_id', table_name='time_entries')
    op.drop_index('ix_time_entries_user_id', table_name='time_entries')
    op.drop_index('ix_time_entries_id', table_name='time_entries')
    op.drop_table('time_entries')

    # Drop events table
    op.drop_index('ix_events_start_time', table_name='events')
    op.drop_index('ix_events_google_event_id', table_name='events')
    op.drop_index('ix_events_user_id', table_name='events')
    op.drop_index('ix_events_id', table_name='events')
    op.drop_table('events')
