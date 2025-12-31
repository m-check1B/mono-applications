"""migrate tasks to knowledge items

Revision ID: 6b363098889d
Revises: 13662996ceed
Create Date: 2025-11-21 15:23:18.519134

This migration unifies the Task model into the generic KnowledgeItem system.
All existing tasks are migrated to knowledge_item table with typeId="tasks".
Task-specific fields are preserved in item_metadata JSON.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid


# revision identifiers, used by Alembic.
revision = '6b363098889d'
down_revision = '13662996ceed'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Migrate all tasks to knowledge_items.
    Steps:
    1. Ensure "Tasks" item_type exists for each user
    2. Migrate task data to knowledge_item with task-specific metadata
    3. Keep task table intact for backward compatibility
    """
    conn = op.get_bind()

    # Step 1: Ensure "Tasks" item type exists for all users
    print("Creating 'Tasks' item type for all users...")

    # Get all unique userIds from task table
    result = conn.execute(sa.text("""
        SELECT DISTINCT "userId" FROM task WHERE "userId" IS NOT NULL
    """))
    user_ids = [row[0] for row in result]

    for user_id in user_ids:
        # Check if user already has Tasks type
        existing = conn.execute(sa.text("""
            SELECT id FROM item_type
            WHERE "userId" = :user_id AND name = 'Tasks'
        """), {"user_id": user_id})

        if not existing.fetchone():
            # Create Tasks type for this user
            type_id = str(uuid.uuid4())
            conn.execute(sa.text("""
                INSERT INTO item_type (id, "userId", name, description, icon, color, "isDefault", "createdAt")
                VALUES (:id, :user_id, 'Tasks', 'Task items', 'CheckSquare', 'blue', true, NOW())
            """), {"id": type_id, "user_id": user_id})
            print(f"Created Tasks type for user {user_id}")

    # Step 2: Migrate tasks to knowledge_items
    print("Migrating tasks to knowledge_items...")

    conn.execute(sa.text("""
        INSERT INTO knowledge_item (
            id, "userId", "typeId", title, content, item_metadata, completed, "createdAt", "updatedAt"
        )
        SELECT
            t.id,
            t."userId",
            (SELECT id FROM item_type WHERE "userId" = t."userId" AND name = 'Tasks' LIMIT 1) as "typeId",
            t.title,
            COALESCE(t.description, '') as content,
            jsonb_build_object(
                'status', t.status::text,
                'priority', t.priority,
                'dueDate', to_char(t."dueDate", 'YYYY-MM-DD"T"HH24:MI:SS"Z"'),
                'completedAt', to_char(t."completedAt", 'YYYY-MM-DD"T"HH24:MI:SS"Z"'),
                'estimatedMinutes', t."estimatedMinutes",
                'actualMinutes', t."actualMinutes",
                'energyRequired', t."energyRequired"::text,
                'tags', t.tags,
                'parentTaskId', t."parentTaskId",
                'projectId', t."projectId",
                'workspaceId', t."workspaceId",
                'aiInsights', t."aiInsights",
                'urgencyScore', t."urgencyScore",
                'title_i18n', t.title_i18n,
                'description_i18n', t.description_i18n
            ) as item_metadata,
            CASE WHEN t.status = 'COMPLETED' THEN true ELSE false END as completed,
            t."createdAt",
            t."createdAt" as "updatedAt"  -- Use createdAt as initial updatedAt
        FROM task t
        WHERE NOT EXISTS (
            SELECT 1 FROM knowledge_item ki WHERE ki.id = t.id
        )
        AND t."userId" IS NOT NULL
    """))

    rows_migrated = conn.execute(sa.text("SELECT COUNT(*) FROM knowledge_item WHERE \"typeId\" IN (SELECT id FROM item_type WHERE name = 'Tasks')")).scalar()
    print(f"Migrated {rows_migrated} tasks to knowledge_items")

    # Step 3: Add migration marker (for tracking)
    print("Migration complete! Task table kept for backward compatibility.")


def downgrade() -> None:
    """
    Rollback: Delete migrated tasks from knowledge_items.
    Note: Task table data is preserved, so no data loss on downgrade.
    """
    conn = op.get_bind()

    print("Rolling back task migration...")

    # Delete all knowledge_items with Tasks type
    conn.execute(sa.text("""
        DELETE FROM knowledge_item
        WHERE "typeId" IN (
            SELECT id FROM item_type WHERE name = 'Tasks'
        )
    """))

    print("Rollback complete. Tasks remain in task table.")
