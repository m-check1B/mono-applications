"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-11-28

Speak by Kraliki - Initial database schema
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Companies table
    op.create_table(
        'companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False),
        sa.Column('plan', sa.String(50), server_default='starter'),
        sa.Column('stripe_customer_id', sa.String(100)),
        sa.Column('stripe_subscription_id', sa.String(100)),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('settings', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Departments table
    op.create_table(
        'departments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id', ondelete='SET NULL')),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_departments_company_id', 'departments', ['company_id'])

    # Users table (HR/CEO/Admin)
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('role', sa.String(50), server_default='manager'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('last_login', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_users_company_id', 'users', ['company_id'])
    op.create_index('ix_users_email', 'users', ['email'])

    # Employees table
    op.create_table(
        'employees',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id', ondelete='SET NULL')),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100)),
        sa.Column('employee_id', sa.String(100)),
        sa.Column('hire_date', sa.Date),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        # Speak-specific fields (legacy vop_* columns)
        sa.Column('magic_link_token', sa.String(100)),
        sa.Column('magic_link_expires', sa.DateTime),
        sa.Column('vop_opted_out', sa.Boolean, server_default='false'),
        sa.Column('vop_last_survey', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_employees_company_id', 'employees', ['company_id'])
    op.create_index('ix_employees_magic_link_token', 'employees', ['magic_link_token'])

    # Surveys table
    op.create_table(
        'vop_surveys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('status', sa.String(20), server_default='draft'),
        sa.Column('frequency', sa.String(50), server_default='monthly'),
        sa.Column('questions', postgresql.JSONB),
        sa.Column('custom_system_prompt', sa.Text),
        sa.Column('starts_at', sa.DateTime),
        sa.Column('ends_at', sa.DateTime),
        sa.Column('target_departments', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_vop_surveys_company_id', 'vop_surveys', ['company_id'])

    # Conversations table
    op.create_table(
        'vop_conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('survey_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vop_surveys.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('invited_at', sa.DateTime),
        sa.Column('started_at', sa.DateTime),
        sa.Column('completed_at', sa.DateTime),
        sa.Column('duration_seconds', sa.Integer),
        sa.Column('transcript', postgresql.JSONB),
        sa.Column('transcript_reviewed_by_employee', sa.Boolean, server_default='false'),
        sa.Column('redacted_sections', postgresql.JSONB),
        sa.Column('audio_url', sa.String(500)),
        sa.Column('fallback_to_text', sa.Boolean, server_default='false'),
        sa.Column('fallback_reason', sa.String(100)),
        sa.Column('sentiment_score', sa.Numeric(3, 2)),
        sa.Column('topics', postgresql.JSONB),
        sa.Column('flags', postgresql.JSONB),
        sa.Column('summary', sa.Text),
        sa.Column('anonymous_id', sa.String(50)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_vop_conversations_survey_id', 'vop_conversations', ['survey_id'])
    op.create_index('ix_vop_conversations_employee_id', 'vop_conversations', ['employee_id'])

    # Alerts table
    op.create_table(
        'vop_alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vop_conversations.id', ondelete='CASCADE')),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), server_default='medium'),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id', ondelete='SET NULL')),
        sa.Column('description', sa.Text),
        sa.Column('trigger_keywords', sa.String(500)),
        sa.Column('is_read', sa.Boolean, server_default='false'),
        sa.Column('read_at', sa.DateTime),
        sa.Column('read_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_vop_alerts_company_id', 'vop_alerts', ['company_id'])
    op.create_index('ix_vop_alerts_type', 'vop_alerts', ['type'])

    # Actions table (Action Loop)
    op.create_table(
        'vop_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id', ondelete='SET NULL')),
        sa.Column('created_from_alert_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vop_alerts.id', ondelete='SET NULL')),
        sa.Column('topic', sa.String(200), nullable=False),
        sa.Column('status', sa.String(20), server_default='new'),
        sa.Column('internal_notes', sa.Text),
        sa.Column('public_message', sa.Text),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('resolved_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_vop_actions_company_id', 'vop_actions', ['company_id'])
    op.create_index('ix_vop_actions_status', 'vop_actions', ['status'])


def downgrade() -> None:
    op.drop_table('vop_actions')
    op.drop_table('vop_alerts')
    op.drop_table('vop_conversations')
    op.drop_table('vop_surveys')
    op.drop_table('employees')
    op.drop_table('users')
    op.drop_table('departments')
    op.drop_table('companies')
