"""Add i18n support with JSONB fields for Czech and English

Revision ID: 001_i18n_support
Revises:
Create Date: 2025-10-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add JSONB i18n fields for multilingual support (Czech + English).

    Fields added:
    - title_i18n / name_i18n (JSONB with 'en' and 'cs' keys)
    - description_i18n (JSONB with 'en' and 'cs' keys)
    """

    # Add i18n fields to tasks table
    op.add_column('task', sa.Column('title_i18n', JSONB, nullable=True))
    op.add_column('task', sa.Column('description_i18n', JSONB, nullable=True))

    # Add i18n fields to project table
    op.add_column('project', sa.Column('name_i18n', JSONB, nullable=True))
    op.add_column('project', sa.Column('description_i18n', JSONB, nullable=True))

    # Migrate existing data from title/description to title_i18n/description_i18n
    # All existing data is in English
    op.execute("""
        UPDATE task
        SET title_i18n = jsonb_build_object('en', title)
        WHERE title IS NOT NULL AND title_i18n IS NULL
    """)

    op.execute("""
        UPDATE task
        SET description_i18n = jsonb_build_object('en', description)
        WHERE description IS NOT NULL AND description_i18n IS NULL
    """)

    op.execute("""
        UPDATE project
        SET name_i18n = jsonb_build_object('en', name)
        WHERE name IS NOT NULL AND name_i18n IS NULL
    """)

    op.execute("""
        UPDATE project
        SET description_i18n = jsonb_build_object('en', description)
        WHERE description IS NOT NULL AND description_i18n IS NULL
    """)

    # Create indexes for JSONB fields for better query performance
    op.create_index(
        'idx_task_title_i18n_en',
        'task',
        [sa.text("(title_i18n->>'en')")],
        unique=False
    )

    op.create_index(
        'idx_task_title_i18n_cs',
        'task',
        [sa.text("(title_i18n->>'cs')")],
        unique=False
    )

    op.create_index(
        'idx_project_name_i18n_en',
        'project',
        [sa.text("(name_i18n->>'en')")],
        unique=False
    )

    op.create_index(
        'idx_project_name_i18n_cs',
        'project',
        [sa.text("(name_i18n->>'cs')")],
        unique=False
    )


def downgrade() -> None:
    """
    Remove i18n support and revert to single-language fields.
    """

    # Drop indexes
    op.drop_index('idx_project_name_i18n_cs', table_name='project')
    op.drop_index('idx_project_name_i18n_en', table_name='project')
    op.drop_index('idx_task_title_i18n_cs', table_name='task')
    op.drop_index('idx_task_title_i18n_en', table_name='task')

    # Drop i18n columns from project
    op.drop_column('project', 'description_i18n')
    op.drop_column('project', 'name_i18n')

    # Drop i18n columns from task
    op.drop_column('task', 'description_i18n')
    op.drop_column('task', 'title_i18n')
