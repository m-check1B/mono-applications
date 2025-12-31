"""
Targeted tests to improve coverage for Gemini File Search Service
"""
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from datetime import datetime

from app.services import gemini_file_search as service
from app.models.file_search_store import FileSearchStore
from app.models.knowledge_item import KnowledgeItem
from app.models.user import User

@pytest.fixture
def mock_genai_available():
    """Ensure google-generativeai module is available and mocked"""
    mock_gen = MagicMock()
    with patch("app.services.gemini_file_search._genai", mock_gen), \
         patch("app.services.gemini_file_search._GEMINI_AVAILABLE", True), \
         patch("app.services.gemini_file_search.is_gemini_available", return_value=True):
        yield mock_gen

@pytest.mark.asyncio
async def test_get_or_create_org_store_creation_logic(db: Session, test_user: User, mock_genai_available):
    """Hit lines 121-176: new store creation via Gemini API"""
    # Ensure no existing store
    db.query(FileSearchStore).filter_by(organizationId=test_user.organizationId).delete()
    db.commit()
    
    mock_store = MagicMock()
    mock_store.name = "fileSearchStores/new-store-xyz"
    mock_genai_available.create_file_store.return_value = mock_store
    
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.GEMINI_API_KEY = "test-key"
        
        store_name = await service.get_or_create_org_store(db, test_user)
        
        assert store_name == "fileSearchStores/new-store-xyz"
        mock_genai_available.create_file_store.assert_called()
        
        # Verify DB entry
        db_store = db.query(FileSearchStore).filter_by(organizationId=test_user.organizationId).first()
        assert db_store is not None
        assert db_store.store_name == "fileSearchStores/new-store-xyz"

@pytest.mark.asyncio
async def test_import_knowledge_item_upload_logic(db: Session, test_user: User, mock_genai_available):
    """Hit lines 203-275: knowledge item upload logic"""
    # Ensure item type exists
    from app.models.item_type import ItemType
    type_id = "note"
    existing_type = db.query(ItemType).filter_by(id=type_id).first()
    if not existing_type:
        db.add(ItemType(id=type_id, name="Note", icon="file-text", userId=test_user.id))
        db.commit()

    # Pre-create store in DB
    store = FileSearchStore(
        id="store_id", organizationId=test_user.organizationId,
        store_name="fileSearchStores/target-store", kind="org_main"
    )
    db.add(store)
    
    item = KnowledgeItem(
        id="k_id", userId=test_user.id, title="Test coverage title",
        content="Coverage content", typeId=type_id,
        createdAt=datetime.now(), updatedAt=datetime.now()
    )
    db.add(item)
    db.commit()
    
    mock_file = MagicMock()
    mock_file.name = "files/uploaded-doc"
    mock_genai_available.upload_file.return_value = mock_file
    
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.GEMINI_API_KEY = "test-key"
        
        doc_name = await service.import_knowledge_item(db, test_user, item)
        
        assert doc_name == "files/uploaded-doc"
        mock_genai_available.upload_file.assert_called()
        mock_genai_available.add_file_to_store.assert_called_with(
            store_name="fileSearchStores/target-store",
            file_name="files/uploaded-doc"
        )

@pytest.mark.asyncio
async def test_query_store_gemini_logic(db: Session, test_user: User, mock_genai_available):
    """Hit lines 305-388: Gemini query logic with grounding metadata"""
    store = FileSearchStore(
        id="store_id", organizationId=test_user.organizationId,
        store_name="fileSearchStores/query-store", kind="org_main"
    )
    db.add(store)
    db.commit()
    
    # Mock response with grounding metadata and citations
    mock_chunk = MagicMock()
    mock_chunk.text = "Citated text"
    mock_chunk.source = "Source 1"
    mock_chunk.metadata = {"knowledge_item_id": "k1"}
    
    mock_grounding = MagicMock()
    mock_grounding.grounding_chunks = [mock_chunk]
    
    mock_candidate = MagicMock()
    mock_candidate.grounding_metadata = mock_grounding
    
    mock_response = MagicMock()
    mock_response.text = "Generated answer"
    mock_response.candidates = [mock_candidate]
    
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    mock_genai_available.GenerativeModel.return_value = mock_model
    
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.GEMINI_API_KEY = "test-key"
        
        result = await service.query_store(db, test_user, "How to improve coverage?")
        
        assert result["answer"] == "Generated answer"
        assert len(result["citations"]) == 1
        assert result["citations"][0]["knowledge_item_id"] == "k1"
        assert result["store_name"] == "fileSearchStores/query-store"

@pytest.mark.asyncio
async def test_import_voice_transcript_logic(db: Session, test_user: User, mock_genai_available):
    """Hit lines 525-597: import voice transcript logic"""
    # Pre-create store in DB
    store = FileSearchStore(
        id="store_id", organizationId=test_user.organizationId,
        store_name="fileSearchStores/voice-store", kind="org_main"
    )
    db.add(store)
    db.commit()
    
    mock_recording = MagicMock()
    mock_recording.id = "rec_123"
    mock_recording.transcript = "Voice transcript text"
    mock_recording.language = "en"
    mock_recording.confidence = 0.98
    mock_recording.duration = 45
    mock_recording.intent = "support"
    mock_recording.createdAt = datetime.now()
    
    mock_file = MagicMock()
    mock_file.name = "files/voice-doc"
    mock_genai_available.upload_file.return_value = mock_file
    
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.GEMINI_API_KEY = "test-key"
        
        doc_name = await service.import_voice_transcript(db, test_user, mock_recording)
        
        assert doc_name == "files/voice-doc"
        mock_genai_available.upload_file.assert_called()
        mock_genai_available.add_file_to_store.assert_called_with(
            store_name="fileSearchStores/voice-store",
            file_name="files/voice-doc"
        )

@pytest.mark.asyncio
async def test_delete_document_success(mock_genai_available):
    """Hit lines 600+: delete document logic"""
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.GEMINI_API_KEY = "test-key"
        
        result = await service.delete_document("store-1", "doc-to-delete")
        
        assert result is True
        mock_genai_available.delete_file.assert_called_with("doc-to-delete")

@pytest.mark.asyncio
async def test_list_store_documents_logic(db: Session, test_user: User, mock_genai_available):
    """Hit lines 481-505: list store documents success path"""
    store = FileSearchStore(
        id="store_id", organizationId=test_user.organizationId,
        store_name="fileSearchStores/list-store", kind="org_main"
    )
    db.add(store)
    db.commit()
    
    mock_file = MagicMock()
    mock_file.name = "files/doc-1"
    mock_file.display_name = "Document One"
    mock_file.size_bytes = 500
    mock_file.create_time = datetime.now()
    
    mock_genai_available.list_files_in_store.return_value = [mock_file]
    
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.GEMINI_API_KEY = "test-key"
        
        results = await service.list_store_documents(db, test_user)
        
        assert results is not None
        assert len(results) == 1
        assert results[0]["name"] == "files/doc-1"
        assert results[0]["display_name"] == "Document One"
