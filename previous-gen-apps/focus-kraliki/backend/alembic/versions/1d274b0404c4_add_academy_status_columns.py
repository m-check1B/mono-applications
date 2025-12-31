"""add_academy_status_columns

Revision ID: 1d274b0404c4
Revises: linear_id_01
Create Date: 2025-12-25 21:00:55.442790

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d274b0404c4'
down_revision = 'linear_id_01'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add academy columns to user table
    op.add_column('user', sa.Column('academyStatus', sa.Enum('NONE', 'WAITLIST', 'STUDENT', 'GRADUATE', name='academystatus'), nullable=False, server_default='NONE'))
    op.add_column('user', sa.Column('academyInterest', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('user', 'academyInterest')
    op.drop_column('user', 'academyStatus')
    # Drop enum type if exists
    op.execute("DROP TYPE IF EXISTS academystatus")
