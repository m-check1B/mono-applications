"""add knowledge layer

Revision ID: 006
Revises: 005
Create Date: 2025-11-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create item_type table
    op.create_table('item_type',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('userId', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('icon', sa.String(), nullable=True),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['userId'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_item_type_id'), 'item_type', ['id'], unique=False)
    op.create_index(op.f('ix_item_type_userId'), 'item_type', ['userId'], unique=False)

    # Create knowledge_item table
    op.create_table('knowledge_item',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('userId', sa.String(), nullable=False),
        sa.Column('typeId', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updatedAt', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['userId'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['typeId'], ['item_type.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledge_item_id'), 'knowledge_item', ['id'], unique=False)
    op.create_index(op.f('ix_knowledge_item_userId'), 'knowledge_item', ['userId'], unique=False)
    op.create_index(op.f('ix_knowledge_item_typeId'), 'knowledge_item', ['typeId'], unique=False)


def downgrade() -> None:
    # Drop knowledge_item table
    op.drop_index(op.f('ix_knowledge_item_typeId'), table_name='knowledge_item')
    op.drop_index(op.f('ix_knowledge_item_userId'), table_name='knowledge_item')
    op.drop_index(op.f('ix_knowledge_item_id'), table_name='knowledge_item')
    op.drop_table('knowledge_item')

    # Drop item_type table
    op.drop_index(op.f('ix_item_type_userId'), table_name='item_type')
    op.drop_index(op.f('ix_item_type_id'), table_name='item_type')
    op.drop_table('item_type')
