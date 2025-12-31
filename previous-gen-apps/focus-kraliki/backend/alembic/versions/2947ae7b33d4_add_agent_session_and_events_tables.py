"""add_agent_session_and_events_tables

Revision ID: 2947ae7b33d4
Revises: 010
Create Date: 2025-11-16 10:46:21.205733

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2947ae7b33d4'
down_revision = '011_add_command_history'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create agent_session table
    op.create_table(
        'agent_session',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('userId', sa.String(), nullable=False),
        sa.Column('telemetryId', sa.String(), nullable=True),
        sa.Column('sessionUuid', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', name='agentsessionstatus'), nullable=False),
        sa.Column('goal', sa.Text(), nullable=False),
        sa.Column('structuredGoal', sa.JSON(), nullable=True),
        sa.Column('context', sa.JSON(), nullable=True),
        sa.Column('escalationReason', sa.JSON(), nullable=True),
        sa.Column('toolCallCount', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('lastToolCall', sa.String(), nullable=True),
        sa.Column('lastToolCallAt', sa.DateTime(), nullable=True),
        sa.Column('progressPercent', sa.Float(), nullable=True),
        sa.Column('currentStep', sa.String(), nullable=True),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('errorMessage', sa.Text(), nullable=True),
        sa.Column('startedAt', sa.DateTime(), nullable=True),
        sa.Column('completedAt', sa.DateTime(), nullable=True),
        sa.Column('createdAt', sa.DateTime(), nullable=False),
        sa.Column('updatedAt', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['userId'], ['user.id']),
        sa.ForeignKeyConstraint(['telemetryId'], ['request_telemetry.id']),
    )
    op.create_index(op.f('ix_agent_session_userId'), 'agent_session', ['userId'], unique=False)
    op.create_index(op.f('ix_agent_session_telemetryId'), 'agent_session', ['telemetryId'], unique=False)
    op.create_index(op.f('ix_agent_session_sessionUuid'), 'agent_session', ['sessionUuid'], unique=True)

    # Create agent_session_event table
    op.create_table(
        'agent_session_event',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('sessionId', sa.String(), nullable=False),
        sa.Column('eventType', sa.Enum('STARTED', 'TOOL_CALL', 'PROGRESS_UPDATE', 'ERROR', 'COMPLETED', name='agentsessioneventtype'), nullable=False),
        sa.Column('eventData', sa.JSON(), nullable=True),
        sa.Column('toolName', sa.String(), nullable=True),
        sa.Column('toolInput', sa.JSON(), nullable=True),
        sa.Column('toolOutput', sa.JSON(), nullable=True),
        sa.Column('toolError', sa.Text(), nullable=True),
        sa.Column('toolDurationMs', sa.Integer(), nullable=True),
        sa.Column('createdAt', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['sessionId'], ['agent_session.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_agent_session_event_sessionId'), 'agent_session_event', ['sessionId'], unique=False)
    op.create_index(op.f('ix_agent_session_event_eventType'), 'agent_session_event', ['eventType'], unique=False)
    op.create_index(op.f('ix_agent_session_event_toolName'), 'agent_session_event', ['toolName'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_agent_session_event_toolName'), table_name='agent_session_event')
    op.drop_index(op.f('ix_agent_session_event_eventType'), table_name='agent_session_event')
    op.drop_index(op.f('ix_agent_session_event_sessionId'), table_name='agent_session_event')
    op.drop_table('agent_session_event')

    op.drop_index(op.f('ix_agent_session_sessionUuid'), table_name='agent_session')
    op.drop_index(op.f('ix_agent_session_telemetryId'), table_name='agent_session')
    op.drop_index(op.f('ix_agent_session_userId'), table_name='agent_session')
    op.drop_table('agent_session')

    op.execute('DROP TYPE agentsessioneventtype')
    op.execute('DROP TYPE agentsessionstatus')
