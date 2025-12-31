"""Add campaign management tables

Revision ID: 20251110_2100
Revises: 20251013_1530_add_user_permissions_and_role
Create Date: 2025-11-10 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251110_2100'
down_revision: Union[str, None] = '20251013_1530_add_user_permissions_and_role'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create contact_lists table
    op.create_table('contact_lists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('import_file_name', sa.String(length=255), nullable=True),
        sa.Column('import_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('import_errors', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('total_contacts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('processed_contacts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('successful_contacts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_contacts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('tags', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contact_lists_id'), 'contact_lists', ['id'], unique=False)

    # Create contacts table
    op.create_table('contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contact_list_id', sa.Integer(), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('company', sa.String(length=200), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('last_attempt_at', sa.DateTime(), nullable=True),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('disposition', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('preferred_call_time', sa.DateTime(), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'),
        sa.Column('do_not_call_before', sa.DateTime(), nullable=True),
        sa.Column('do_not_call_after', sa.DateTime(), nullable=True),
        sa.Column('opted_out', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('opted_out_at', sa.DateTime(), nullable=True),
        sa.Column('compliance_flags', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['contact_list_id'], ['contact_lists.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contacts_id'), 'contacts', ['id'], unique=False)
    op.create_index(op.f('ix_contacts_phone_number'), 'contacts', ['phone_number'], unique=False)

    # Create call_flows table
    op.create_table('call_flows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('flow_definition', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('success_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('average_duration', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_call_flows_id'), 'call_flows', ['id'], unique=False)

    # Create campaign_calls table
    op.create_table('campaign_calls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('call_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='scheduled'),
        sa.Column('disposition', sa.String(length=100), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('talk_time_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('wait_time_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('after_call_work_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('audio_quality_score', sa.Float(), nullable=True),
        sa.Column('transcription_accuracy', sa.Float(), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('intent_detected', sa.String(length=100), nullable=True),
        sa.Column('key_topics', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('recording_url', sa.String(length=500), nullable=True),
        sa.Column('transcription', sa.Text(), nullable=True),
        sa.Column('agent_notes', sa.Text(), nullable=True),
        sa.Column('system_notes', sa.Text(), nullable=True),
        sa.Column('follow_up_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('follow_up_date', sa.DateTime(), nullable=True),
        sa.Column('cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id']),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id']),
        sa.ForeignKeyConstraint(['call_id'], ['call_states.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaign_calls_id'), 'campaign_calls', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_campaign_calls_id'), table_name='campaign_calls')
    op.drop_table('campaign_calls')

    op.drop_index(op.f('ix_call_flows_id'), table_name='call_flows')
    op.drop_table('call_flows')

    op.drop_index(op.f('ix_contacts_phone_number'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_id'), table_name='contacts')
    op.drop_table('contacts')

    op.drop_index(op.f('ix_contact_lists_id'), table_name='contact_lists')
    op.drop_table('contact_lists')
