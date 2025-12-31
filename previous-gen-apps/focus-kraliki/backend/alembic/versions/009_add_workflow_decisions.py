"""add workflow decision fields to request telemetry

Revision ID: 009
Revises: efc5b5c84ee7
Create Date: 2025-11-15 12:00:00

"""
from alembic import op
import sqlalchemy as sa
import enum

# revision identifiers, used by Alembic.
revision = '009'
down_revision = 'c1310994d158'
branch_labels = None
depends_on = None


class WorkflowDecisionStatus(str, enum.Enum):
    APPROVED = 'approved'
    REVISE = 'revise'
    REJECTED = 'rejected'


def upgrade() -> None:
    status_type = sa.Enum(WorkflowDecisionStatus, name='workflowdecisionstatus')
    status_type.create(op.get_bind(), checkfirst=True)
    op.add_column('request_telemetry', sa.Column('decisionStatus', status_type, nullable=True))
    op.add_column('request_telemetry', sa.Column('decisionNotes', sa.JSON(), nullable=True))
    op.add_column('request_telemetry', sa.Column('decisionAt', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('request_telemetry', 'decisionAt')
    op.drop_column('request_telemetry', 'decisionNotes')
    op.drop_column('request_telemetry', 'decisionStatus')
    status_type = sa.Enum(WorkflowDecisionStatus, name='workflowdecisionstatus')
    status_type.drop(op.get_bind(), checkfirst=True)
