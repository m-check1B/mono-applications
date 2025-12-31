"""Add AI insights tables

Revision ID: 20251013_1200
Revises: 0c1264374ebd
Create Date: 2025-10-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251013_1200'
down_revision = '0c1264374ebd'
branch_labels = None
depends_on = None


def upgrade():
    # Create conversation_insights table
    op.create_table('conversation_insights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('intent', sa.String(length=100), nullable=False),
        sa.Column('intent_category', sa.String(length=50), nullable=False),
        sa.Column('intent_confidence', sa.Float(), nullable=False),
        sa.Column('intent_keywords', sa.JSON(), nullable=False),
        sa.Column('intent_context', sa.Text(), nullable=True),
        sa.Column('intent_urgency', sa.String(length=20), nullable=False),
        sa.Column('sentiment_score', sa.String(length=20), nullable=False),
        sa.Column('sentiment_confidence', sa.Float(), nullable=False),
        sa.Column('sentiment_emotions', sa.JSON(), nullable=False),
        sa.Column('sentiment_key_phrases', sa.JSON(), nullable=False),
        sa.Column('sentiment_trajectory', sa.JSON(), nullable=False),
        sa.Column('clarity_score', sa.Float(), nullable=False),
        sa.Column('engagement_score', sa.Float(), nullable=False),
        sa.Column('resolution_probability', sa.Float(), nullable=False),
        sa.Column('customer_satisfaction_prediction', sa.Float(), nullable=False),
        sa.Column('handling_time_estimate', sa.Integer(), nullable=False),
        sa.Column('complexity_score', sa.Float(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('key_topics', sa.JSON(), nullable=False),
        sa.Column('action_items', sa.JSON(), nullable=False),
        sa.Column('ai_providers_used', sa.JSON(), nullable=False),
        sa.Column('processing_time_ms', sa.Float(), nullable=True),
        sa.Column('model_versions', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['call_sessions.session_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_insights_id'), 'conversation_insights', ['id'], unique=False)
    op.create_index(op.f('ix_conversation_insights_session_id'), 'conversation_insights', ['session_id'], unique=False)

    # Create agent_suggestions table
    op.create_table('agent_suggestions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('insight_id', sa.Integer(), nullable=False),
        sa.Column('suggestion_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('suggested_response', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('agent_feedback', sa.Text(), nullable=True),
        sa.Column('implemented_at', sa.DateTime(), nullable=True),
        sa.Column('ai_provider', sa.String(length=50), nullable=True),
        sa.Column('model_version', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['insight_id'], ['conversation_insights.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_suggestions_id'), 'agent_suggestions', ['id'], unique=False)

    # Create conversation_transcripts table
    op.create_table('conversation_transcripts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('raw_transcript', sa.Text(), nullable=False),
        sa.Column('formatted_transcript', sa.Text(), nullable=True),
        sa.Column('speaker_labels', sa.JSON(), nullable=False),
        sa.Column('timestamps', sa.JSON(), nullable=False),
        sa.Column('word_count', sa.Integer(), nullable=False),
        sa.Column('speaker_count', sa.Integer(), nullable=False),
        sa.Column('language_detected', sa.String(length=10), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('transcription_provider', sa.String(length=50), nullable=True),
        sa.Column('processing_time_ms', sa.Float(), nullable=True),
        sa.Column('transcript_metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['call_sessions.session_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_transcripts_id'), 'conversation_transcripts', ['id'], unique=False)
    op.create_index(op.f('ix_conversation_transcripts_session_id'), 'conversation_transcripts', ['session_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_conversation_transcripts_session_id'), table_name='conversation_transcripts')
    op.drop_index(op.f('ix_conversation_transcripts_id'), table_name='conversation_transcripts')
    op.drop_table('conversation_transcripts')
    op.drop_index(op.f('ix_agent_suggestions_id'), table_name='agent_suggestions')
    op.drop_table('agent_suggestions')
    op.drop_index(op.f('ix_conversation_insights_session_id'), table_name='conversation_insights')
    op.drop_index(op.f('ix_conversation_insights_id'), table_name='conversation_insights')
    op.drop_table('conversation_insights')