"""add voice, workflow, and ai conversation tables

Revision ID: 004
Revises: 003
Create Date: 2025-11-10 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create voice_recording table
    op.create_table('voice_recording',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('userId', sa.String(), nullable=False),
        sa.Column('sessionId', sa.String(), nullable=True),
        sa.Column('audioUrl', sa.String(), nullable=True),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('mimetype', sa.String(), nullable=False),
        sa.Column('transcript', sa.String(), nullable=True),
        sa.Column('language', sa.String(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('processedResult', sa.JSON(), nullable=True),
        sa.Column('intent', sa.String(), nullable=True),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('createdAt', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['userId'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_voice_recording_id'), 'voice_recording', ['id'], unique=False)

    # Create workflow_template table
    op.create_table('workflow_template',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('userId', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('icon', sa.String(), nullable=True),
        sa.Column('steps', sa.JSON(), nullable=False),
        sa.Column('totalEstimatedMinutes', sa.Integer(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('isPublic', sa.Boolean(), nullable=False),
        sa.Column('isSystem', sa.Boolean(), nullable=False),
        sa.Column('usageCount', sa.Integer(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('createdAt', sa.DateTime(), nullable=False),
        sa.Column('updatedAt', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['userId'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_template_id'), 'workflow_template', ['id'], unique=False)

    # Create ai_conversation table
    op.create_table('ai_conversation',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('userId', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('messages', sa.JSON(), nullable=False),
        sa.Column('context', sa.JSON(), nullable=True),
        sa.Column('summary', sa.String(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('primaryModel', sa.String(), nullable=True),
        sa.Column('totalTokens', sa.Integer(), nullable=False),
        sa.Column('totalCost', sa.Float(), nullable=False),
        sa.Column('isActive', sa.Boolean(), nullable=False),
        sa.Column('isArchived', sa.Boolean(), nullable=False),
        sa.Column('createdAt', sa.DateTime(), nullable=False),
        sa.Column('updatedAt', sa.DateTime(), nullable=False),
        sa.Column('lastMessageAt', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['userId'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_conversation_id'), 'ai_conversation', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_ai_conversation_id'), table_name='ai_conversation')
    op.drop_table('ai_conversation')

    op.drop_index(op.f('ix_workflow_template_id'), table_name='workflow_template')
    op.drop_table('workflow_template')

    op.drop_index(op.f('ix_voice_recording_id'), table_name='voice_recording')
    op.drop_table('voice_recording')
