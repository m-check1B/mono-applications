"""add_workspace_id_to_task_and_project

Revision ID: 13662996ceed
Revises: 2947ae7b33d4
Create Date: 2025-11-16 15:19:16.036991

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '13662996ceed'
down_revision = '2947ae7b33d4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add workspaceId column to task table
    op.add_column('task', sa.Column('workspaceId', sa.String(), nullable=True))
    op.create_foreign_key('task_workspaceId_fkey', 'task', 'workspace', ['workspaceId'], ['id'])

    # Add workspaceId column to project table
    op.add_column('project', sa.Column('workspaceId', sa.String(), nullable=True))
    op.create_foreign_key('project_workspaceId_fkey', 'project', 'workspace', ['workspaceId'], ['id'])


def downgrade() -> None:
    # Remove workspaceId from project table
    op.drop_constraint('project_workspaceId_fkey', 'project', type_='foreignkey')
    op.drop_column('project', 'workspaceId')

    # Remove workspaceId from task table
    op.drop_constraint('task_workspaceId_fkey', 'task', type_='foreignkey')
    op.drop_column('task', 'workspaceId')
