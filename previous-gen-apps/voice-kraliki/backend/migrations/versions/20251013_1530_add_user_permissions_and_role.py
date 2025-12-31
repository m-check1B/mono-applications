"""Add user permissions column and analyst role

Revision ID: 20251013_1530
Revises: 20251013_1200
Create Date: 2025-10-13 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import Connection


# revision identifiers, used by Alembic.
revision = "20251013_1530"
down_revision = "20251013_1200"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration."""
    # Add permissions column with safe default
    op.add_column(
        "users",
        sa.Column(
            "permissions",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )

    # Normalise existing role values to uppercase to match enum
    op.execute("UPDATE users SET role = upper(role) WHERE role IS NOT NULL")

    # Extend userrole enum with ANALYST when running on PostgreSQL
    bind: Connection = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'ANALYST'")

    # Drop server default now that column is populated
    op.alter_column("users", "permissions", server_default=None)


def downgrade() -> None:
    """Revert migration."""
    op.drop_column("users", "permissions")
    # Rolling back enum value removal is not supported safely; no action taken.
