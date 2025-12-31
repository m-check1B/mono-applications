"""add i18n multilingual fields

Revision ID: 001_add_i18n
Revises:
Create Date: 2025-10-05

Add JSONB fields for multilingual content support (Czech + English)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_add_i18n'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add multilingual JSONB fields"""

    # Update campaigns table
    op.add_column('campaigns',
        sa.Column('name_i18n', postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )
    op.add_column('campaigns',
        sa.Column('description_i18n', postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )

    # Migrate existing data to i18n format
    op.execute("""
        UPDATE campaigns
        SET name_i18n = jsonb_build_object('en', name, 'cs', name),
            description_i18n = jsonb_build_object('en', COALESCE(description, ''), 'cs', COALESCE(description, ''))
        WHERE name_i18n IS NULL
    """)

    # Update agents table (if exists)
    # Similar pattern for other tables that need i18n


def downgrade() -> None:
    """Remove multilingual fields"""

    op.drop_column('campaigns', 'description_i18n')
    op.drop_column('campaigns', 'name_i18n')
