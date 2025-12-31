"""add_persona_and_privacy_preferences

Revision ID: 010
Revises: 009
Create Date: 2025-11-16

Track 5: Persona Onboarding & Trust
- Add persona selection and privacy preferences to user table
- Add feature toggles for Gemini File Search and II-Agent
- Add onboarding status tracking
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '010'
down_revision: Union[str, None] = '009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add persona and privacy columns to user table
    op.add_column('user', sa.Column('selectedPersona', sa.String(), nullable=True))
    op.add_column('user', sa.Column('onboardingCompleted', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('user', sa.Column('onboardingStep', sa.Integer(), nullable=False, server_default='0'))

    # Privacy and feature toggle preferences (stored as JSON)
    op.add_column('user', sa.Column('privacyPreferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('user', sa.Column('featureToggles', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    # Set default values for existing users (all users will get defaults)
    # No WHERE clause needed since columns were just added


def downgrade() -> None:
    op.drop_column('user', 'featureToggles')
    op.drop_column('user', 'privacyPreferences')
    op.drop_column('user', 'onboardingStep')
    op.drop_column('user', 'onboardingCompleted')
    op.drop_column('user', 'selectedPersona')
