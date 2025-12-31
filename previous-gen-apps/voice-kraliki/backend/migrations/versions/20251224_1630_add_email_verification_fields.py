"""Add email verification fields to users table

Revision ID: 20251224_1630
Revises: 20251111_1300
Create Date: 2025-12-24 16:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20251224_1630"
down_revision = "20251111_1300"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration."""
    # Add email verification token column
    op.add_column(
        "users",
        sa.Column(
            "email_verification_token",
            sa.String(255),
            nullable=True,
        ),
    )

    # Add email verification token expiration column
    op.add_column(
        "users",
        sa.Column(
            "email_verification_token_expires",
            sa.DateTime(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Revert migration."""
    op.drop_column("users", "email_verification_token_expires")
    op.drop_column("users", "email_verification_token")
