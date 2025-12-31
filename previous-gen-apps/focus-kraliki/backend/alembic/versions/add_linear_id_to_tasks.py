"""
Add linear_id column to task table for Focus → Linear sync
"""

from alembic import op
import sqlalchemy as sa

revision = "linear_id_01"
down_revision = "6b363098889d"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("task", sa.Column("linear_id", sa.String(), nullable=True))
    op.create_index("ix_task_linear_id", "task", ["linear_id"])


def downgrade():
    op.drop_index("ix_task_linear_id", table_name="task")
    op.drop_column("task", "linear_id")
