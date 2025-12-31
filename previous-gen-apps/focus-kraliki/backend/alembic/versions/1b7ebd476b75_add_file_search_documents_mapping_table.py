"""add_file_search_documents_mapping_table

Revision ID: 1b7ebd476b75
Revises: efc5b5c84ee7
Create Date: 2025-11-14 11:28:21.894177

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b7ebd476b75'
down_revision = 'efc5b5c84ee7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create file_search_document table
    op.create_table(
        'file_search_document',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('organizationId', sa.String(), nullable=False),
        sa.Column('userId', sa.String(), nullable=False),
        sa.Column('knowledgeItemId', sa.String(), nullable=True),
        sa.Column('voiceRecordingId', sa.String(), nullable=True),
        sa.Column('storeName', sa.String(), nullable=False),
        sa.Column('documentName', sa.String(), nullable=False),
        sa.Column('kind', sa.String(), nullable=False),
        sa.Column('createdAt', sa.DateTime(), nullable=False),
        sa.Column('updatedAt', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['userId'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['knowledgeItemId'], ['knowledge_item.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['voiceRecordingId'], ['voice_recording.id'], ondelete='CASCADE'),
    )

    # Create indexes for fast lookups
    op.create_index('idx_file_search_doc_org', 'file_search_document', ['organizationId'])
    op.create_index('idx_file_search_doc_user', 'file_search_document', ['userId'])
    op.create_index('idx_file_search_doc_knowledge', 'file_search_document', ['knowledgeItemId'])
    op.create_index('idx_file_search_doc_voice', 'file_search_document', ['voiceRecordingId'])
    op.create_index('idx_file_search_doc_store', 'file_search_document', ['storeName'])
    op.create_index('idx_file_search_doc_kind', 'file_search_document', ['kind'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_file_search_doc_kind', table_name='file_search_document')
    op.drop_index('idx_file_search_doc_store', table_name='file_search_document')
    op.drop_index('idx_file_search_doc_voice', table_name='file_search_document')
    op.drop_index('idx_file_search_doc_knowledge', table_name='file_search_document')
    op.drop_index('idx_file_search_doc_user', table_name='file_search_document')
    op.drop_index('idx_file_search_doc_org', table_name='file_search_document')

    # Drop table
    op.drop_table('file_search_document')
