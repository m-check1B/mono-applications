"""Initial migration with production models

Revision ID: 0c1264374ebd
Revises: 
Create Date: 2025-10-13 11:06:25.440001+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c1264374ebd'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply migration."""
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('organization', sa.String(length=255), nullable=True),
        sa.Column('role', sa.Enum('USER', 'AGENT', 'SUPERVISOR', 'ADMIN', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('two_factor_enabled', sa.Boolean(), nullable=False),
        sa.Column('two_factor_secret', sa.String(length=32), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('password_changed_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create call_sessions table
    op.create_table('call_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider_type', sa.String(length=50), nullable=False),
        sa.Column('provider_session_id', sa.String(length=255), nullable=True),
        sa.Column('call_direction', sa.Enum('INBOUND', 'OUTBOUND', name='calldirection'), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('caller_id', sa.String(length=50), nullable=True),
        sa.Column('status', sa.Enum('INITIATED', 'RINGING', 'CONNECTED', 'ACTIVE', 'ON_HOLD', 'DISCONNECTED', 'FAILED', 'COMPLETED', name='callstatus'), nullable=False),
        sa.Column('configuration', sa.JSON(), nullable=False),
        sa.Column('session_metadata', sa.JSON(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('connected_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=False),
        sa.Column('audio_quality_score', sa.Float(), nullable=True),
        sa.Column('latency_ms', sa.Float(), nullable=True),
        sa.Column('packet_loss', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_call_sessions_id'), 'call_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_call_sessions_session_id'), 'call_sessions', ['session_id'], unique=True)

    # Create session_messages table
    op.create_table('session_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('sequence_number', sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum('USER', 'ASSISTANT', 'SYSTEM', 'FUNCTION_CALL', 'FUNCTION_RESULT', name='messagerole'), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('audio_data', sa.Text(), nullable=True),
        sa.Column('transcription', sa.Text(), nullable=True),
        sa.Column('message_metadata', sa.JSON(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('processing_time_ms', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('intent', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['call_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_session_messages_id'), 'session_messages', ['id'], unique=False)

    # Create session_analytics table
    op.create_table('session_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('total_messages', sa.Integer(), nullable=False),
        sa.Column('user_messages', sa.Integer(), nullable=False),
        sa.Column('assistant_messages', sa.Integer(), nullable=False),
        sa.Column('system_messages', sa.Integer(), nullable=False),
        sa.Column('total_audio_duration_ms', sa.Float(), nullable=False),
        sa.Column('user_speaking_time_ms', sa.Float(), nullable=False),
        sa.Column('assistant_speaking_time_ms', sa.Float(), nullable=False),
        sa.Column('silence_time_ms', sa.Float(), nullable=False),
        sa.Column('average_latency_ms', sa.Float(), nullable=True),
        sa.Column('peak_latency_ms', sa.Float(), nullable=True),
        sa.Column('audio_quality_score', sa.Float(), nullable=True),
        sa.Column('connection_stability', sa.Float(), nullable=True),
        sa.Column('function_calls_count', sa.Integer(), nullable=False),
        sa.Column('successful_function_calls', sa.Integer(), nullable=False),
        sa.Column('average_confidence_score', sa.Float(), nullable=True),
        sa.Column('conversion_score', sa.Float(), nullable=True),
        sa.Column('satisfaction_score', sa.Float(), nullable=True),
        sa.Column('resolution_status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['call_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_session_analytics_id'), 'session_analytics', ['id'], unique=False)

    # Create provider_configs table
    op.create_table('provider_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider_type', sa.Enum('OPENAI_REALTIME', 'GEMINI_LIVE', 'DEEPGRAM_NOVA3', 'DEEPGRAM_SEGMENTED', 'ELEVENLABS', 'AZURE_SPEECH', 'AWS_POLLY', 'GOOGLE_TTS', name='providertype'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('api_key', sa.String(length=255), nullable=True),
        sa.Column('api_secret', sa.String(length=255), nullable=True),
        sa.Column('endpoint_url', sa.String(length=500), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('voice', sa.String(length=100), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('region', sa.String(length=50), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('health_check_config', sa.JSON(), nullable=False),
        sa.Column('provider_metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_provider_configs_id'), 'provider_configs', ['id'], unique=False)

    # Create provider_health table
    op.create_table('provider_health',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider_config_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('HEALTHY', 'DEGRADED', 'UNHEALTHY', 'UNKNOWN', name='providerstatus'), nullable=False),
        sa.Column('is_healthy', sa.Boolean(), nullable=False),
        sa.Column('response_time_ms', sa.Float(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('error_rate', sa.Float(), nullable=True),
        sa.Column('uptime_percentage', sa.Float(), nullable=True),
        sa.Column('consecutive_failures', sa.Integer(), nullable=True),
        sa.Column('total_requests', sa.Integer(), nullable=True),
        sa.Column('successful_requests', sa.Integer(), nullable=True),
        sa.Column('failed_requests', sa.Integer(), nullable=True),
        sa.Column('audio_quality_score', sa.Float(), nullable=True),
        sa.Column('latency_p50_ms', sa.Float(), nullable=True),
        sa.Column('latency_p95_ms', sa.Float(), nullable=True),
        sa.Column('latency_p99_ms', sa.Float(), nullable=True),
        sa.Column('error_details', sa.JSON(), nullable=True),
        sa.Column('warnings', sa.JSON(), nullable=True),
        sa.Column('provider_metadata', sa.JSON(), nullable=False),
        sa.Column('last_check', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['provider_config_id'], ['provider_configs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_provider_health_id'), 'provider_health', ['id'], unique=False)

    # Create campaigns table
    op.create_table('campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('campaign_type', sa.Enum('OUTBOUND_SALES', 'INBOUND_SUPPORT', 'LEAD_GENERATION', 'SURVEY', 'NOTIFICATION', name='campaigntype'), nullable=False),
        sa.Column('status', sa.Enum('DRAFT', 'ACTIVE', 'PAUSED', 'COMPLETED', 'CANCELLED', name='campaignstatus'), nullable=False),
        sa.Column('script_id', sa.Integer(), nullable=True),
        sa.Column('target_audience', sa.JSON(), nullable=False),
        sa.Column('schedule_config', sa.JSON(), nullable=False),
        sa.Column('provider_config_id', sa.Integer(), nullable=True),
        sa.Column('max_concurrent_calls', sa.Integer(), nullable=False),
        sa.Column('call_retry_config', sa.JSON(), nullable=False),
        sa.Column('compliance_config', sa.JSON(), nullable=False),
        sa.Column('analytics_config', sa.JSON(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['provider_config_id'], ['provider_configs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaigns_id'), 'campaigns', ['id'], unique=False)

    # Create campaign_scripts table
    op.create_table('campaign_scripts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('script_type', sa.Enum('OUTBOUND_SALES', 'INBOUND_SUPPORT', 'LEAD_GENERATION', 'SURVEY', 'NOTIFICATION', name='campaigntype'), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('variables', sa.JSON(), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaign_scripts_id'), 'campaign_scripts', ['id'], unique=False)


def downgrade() -> None:
    """Revert migration."""
    op.drop_index(op.f('ix_campaign_scripts_id'), table_name='campaign_scripts')
    op.drop_table('campaign_scripts')
    op.drop_index(op.f('ix_campaigns_id'), table_name='campaigns')
    op.drop_table('campaigns')
    op.drop_index(op.f('ix_provider_health_id'), table_name='provider_health')
    op.drop_table('provider_health')
    op.drop_index(op.f('ix_provider_configs_id'), table_name='provider_configs')
    op.drop_table('provider_configs')
    op.drop_index(op.f('ix_session_analytics_id'), table_name='session_analytics')
    op.drop_table('session_analytics')
    op.drop_index(op.f('ix_session_messages_id'), table_name='session_messages')
    op.drop_table('session_messages')
    op.drop_index(op.f('ix_call_sessions_session_id'), table_name='call_sessions')
    op.drop_index(op.f('ix_call_sessions_id'), table_name='call_sessions')
    op.drop_table('call_sessions')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')