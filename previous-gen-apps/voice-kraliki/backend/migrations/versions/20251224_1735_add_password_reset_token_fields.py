"""Add password reset token fields to users table

Revision ID: 20251224_1735
Revises: 20251224_1630
Create Date: 2025-12-24 17:35:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20251224_1735"
down_revision = "20251224_1630"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration."""
    # Add password reset token column
    op.add_column(
        "users",
        sa.Column(
            "password_reset_token",
            sa.String(255),
            nullable=True,
        ),
    )

    # Add password reset token expiration column
    op.add_column(
        "users",
        sa.Column(
            "password_reset_token_expires",
            sa.DateTime(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Revert migration."""
    op.drop_column("users", "password_reset_token_expires")
    op.drop_column("users", "password_reset_token")
