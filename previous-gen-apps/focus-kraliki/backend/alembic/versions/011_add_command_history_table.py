"""add command history table

Revision ID: 011_add_command_history
Revises: 010_add_persona_and_privacy_preferences
Create Date: 2025-11-16 10:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '011_add_command_history'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums if they don't exist (with exception handling)
    import sqlalchemy as sa

    conn = op.get_bind()

    # Check if commandsource type exists
    result = conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'commandsource')"))
    if not result.scalar():
        conn.execute(sa.text("CREATE TYPE commandsource AS ENUM ('assistant_voice', 'assistant_text', 'deterministic_api', 'ii_agent', 'workflow', 'direct_api')"))

    # Check if commandstatus type exists
    result = conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'commandstatus')"))
    if not result.scalar():
        conn.execute(sa.text("CREATE TYPE commandstatus AS ENUM ('pending', 'in_progress', 'completed', 'failed', 'cancelled')"))

    # Create command_history table
    op.create_table(
        'command_history',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('userId', sa.String(), nullable=False),
        sa.Column('source', sa.Enum(
            'assistant_voice',
            'assistant_text',
            'deterministic_api',
            'ii_agent',
            'workflow',
            'direct_api',
            name='commandsource',
            create_type=False
        ), nullable=False),
        sa.Column('command', sa.Text(), nullable=False),
        sa.Column('intent', sa.String(), nullable=True),
        sa.Column('status', sa.Enum(
            'pending',
            'in_progress',
            'completed',
            'failed',
            'cancelled',
            name='commandstatus',
            create_type=False
        ), nullable=False),
        sa.Column('startedAt', sa.DateTime(), nullable=False),
        sa.Column('completedAt', sa.DateTime(), nullable=True),
        sa.Column('durationMs', sa.Float(), nullable=True),
        sa.Column('context', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('telemetryId', sa.String(), nullable=True),
        sa.Column('agentSessionId', sa.String(), nullable=True),
        sa.Column('conversationId', sa.String(), nullable=True),
        sa.Column('model', sa.String(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('command_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['userId'], ['user.id'], ),
        sa.ForeignKeyConstraint(['telemetryId'], ['request_telemetry.id'], ),
        sa.ForeignKeyConstraint(['conversationId'], ['ai_conversation.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for common queries
    op.create_index('ix_command_history_userId', 'command_history', ['userId'])
    op.create_index('ix_command_history_source', 'command_history', ['source'])
    op.create_index('ix_command_history_intent', 'command_history', ['intent'])
    op.create_index('ix_command_history_status', 'command_history', ['status'])
    op.create_index('ix_command_history_startedAt', 'command_history', ['startedAt'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_command_history_startedAt', table_name='command_history')
    op.drop_index('ix_command_history_status', table_name='command_history')
    op.drop_index('ix_command_history_intent', table_name='command_history')
    op.drop_index('ix_command_history_source', table_name='command_history')
    op.drop_index('ix_command_history_userId', table_name='command_history')

    # Drop table
    op.drop_table('command_history')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS commandstatus')
    op.execute('DROP TYPE IF EXISTS commandsource')
