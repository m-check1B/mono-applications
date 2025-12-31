"""
Gemini File Search Integration Service

This service provides integration with Google's Gemini File Search API
for importing knowledge items and enabling semantic search capabilities.

Features:
- Store management (create, get, list) with database tracking
- Document import from knowledge items
- Semantic search with Gemini AI
- Graceful degradation when Gemini unavailable
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.security import generate_id
from app.models.file_search_store import FileSearchStore
from app.models.knowledge_item import KnowledgeItem
from app.models.user import User

logger = logging.getLogger(__name__)

import threading

# Lazy imports to avoid startup failures if google-generativeai not installed
_genai = None
_GEMINI_AVAILABLE = False
_current_api_key = None
_init_lock = threading.Lock()


def _ensure_genai():
    """Lazy import and initialization of google.generativeai"""
    global _genai, _GEMINI_AVAILABLE
    if _genai is None:
        with _init_lock:
            if _genai is None:
                try:
                    import google.generativeai as genai
                    _genai = genai
                    _GEMINI_AVAILABLE = True
                except ImportError:
                    logger.warning("google-generativeai not installed - File Search disabled")
                    _GEMINI_AVAILABLE = False
    return _GEMINI_AVAILABLE


def is_gemini_available(api_key: Optional[str] = None) -> bool:
    """
    Check if Gemini File Search is available

    Args:
        api_key: Optional Gemini API key to validate

    Returns:
        True if Gemini is available and configured
    """
    if not _ensure_genai():
        return False

    if api_key:
        return True

    # Check if API key is configured in environment
    from app.core.config import settings
    return bool(settings.GEMINI_API_KEY)


def configure_gemini(api_key: str) -> bool:
    """
    Configure Gemini API with the provided key

    Args:
        api_key: Gemini API key

    Returns:
        True if configuration succeeded
    """
    global _current_api_key

    if not _ensure_genai():
        return False
    
    # Avoid re-configuring if key hasn't changed
    if _current_api_key == api_key:
        return True

    try:
        _genai.configure(api_key=api_key)
        _current_api_key = api_key
        logger.info("Gemini API configured successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {e}")
        return False


async def get_or_create_org_store(db: Session, user: User) -> Optional[str]:
    """
    Get or create File Search store for user's organization.

    This is the primary entry point for getting a store. It ensures that
    each organization has exactly one main File Search store.

    Args:
        db: Database session
        user: User object (must have organizationId)

    Returns:
        Store name (e.g., "fileSearchStores/xyz123") or None if Gemini unavailable

    Logic:
        1. Query FileSearchStore for organizationId + kind="org_main"
        2. If exists, return store_name
        3. Else: call Gemini API to create store, save to DB, return name
        4. Handle errors gracefully (log and return None if Gemini unavailable)
    """
    if not user.organizationId:
        logger.error(f"User {user.id} has no organizationId")
        return None

    # Check database for existing store
    existing_store = db.query(FileSearchStore).filter(
        FileSearchStore.organizationId == user.organizationId,
        FileSearchStore.kind == "org_main"
    ).first()

    if existing_store:
        logger.info(f"Found existing org store: {existing_store.store_name}")
        return existing_store.store_name

    # Need to create new store via Gemini API
    if not is_gemini_available():
        logger.warning("Gemini unavailable - cannot create org store")
        return None

    try:
        from app.core.config import settings
        configure_gemini(settings.GEMINI_API_KEY)

        # Create store in Gemini
        display_name = f"focus_kraliki_org_{user.organizationId}"

        # Sanitize display name (only alphanumeric and underscores)
        safe_display_name = ''.join(
            c if c.isalnum() or c == '_' else '_'
            for c in display_name
        )

        store = _genai.create_file_store(display_name=safe_display_name)

        logger.info(f"Created Gemini File Search store: {store.name}")

        # Save to database
        db_store = FileSearchStore(
            id=generate_id(),
            organizationId=user.organizationId,
            userId=None,  # Org-level store has no specific user
            store_name=store.name,
            kind="org_main"
        )

        db.add(db_store)
        db.commit()
        db.refresh(db_store)

        logger.info(f"Saved org store to database: {db_store.store_name}")
        return db_store.store_name

    except Exception as e:
        logger.error(f"Failed to create org store for org {user.organizationId}: {e}")
        db.rollback()
        return None


async def import_knowledge_item(
    db: Session,
    user: User,
    item: KnowledgeItem
) -> Optional[str]:
    """
    Import knowledge item content to File Search.

    Args:
        db: Database session
        user: User object
        item: KnowledgeItem to import

    Returns:
        Document name or None on error

    Logic:
        - Get org store via get_or_create_org_store
        - Build document from item.title + item.content
        - Attach metadata: {organization_id, user_id, knowledge_item_id, type}
        - Upload to Gemini File Search API
        - Return document name or None on error
    """
    # Get org store
    store_name = await get_or_create_org_store(db, user)
    if not store_name:
        logger.error("Failed to get org store for knowledge item import")
        return None

    if not is_gemini_available():
        logger.warning("Gemini unavailable - skipping knowledge item import")
        return None

    try:
        from app.core.config import settings
        configure_gemini(settings.GEMINI_API_KEY)

        # Build document content
        content = f"""Title: {item.title}

Content:
{item.content or '(no content)'}

Type ID: {item.typeId}
Completed: {item.completed}
Created: {item.createdAt}
Updated: {item.updatedAt}
User ID: {user.id}
Organization ID: {user.organizationId}
"""

        # Prepare metadata
        metadata = {
            "knowledge_item_id": item.id,
            "user_id": user.id,
            "organization_id": user.organizationId,
            "type_id": item.typeId,
            "title": item.title,
            "completed": str(item.completed),
            "created_at": item.createdAt.isoformat(),
            "kind": "knowledge_item"
        }

        # Upload document to Gemini
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            # Upload file to Gemini
            uploaded_file = _genai.upload_file(
                path=temp_path,
                display_name=f"{item.title[:50]}_{item.id}.txt"
            )

            # Add to file store
            _genai.add_file_to_store(
                store_name=store_name,
                file_name=uploaded_file.name
            )

            logger.info(f"Imported knowledge item {item.id} to File Search as {uploaded_file.name}")
            return uploaded_file.name

        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.debug(f"Failed to delete temp file: {e}")

    except Exception as e:
        logger.error(f"Failed to import knowledge item {item.id}: {e}")
        return None


async def query_store(
    db: Session,
    user: User,
    prompt: str,
    context: Optional[dict] = None
) -> Dict[str, Any]:
    """
    Query File Search store with Gemini.

    Args:
        db: Database session
        user: User object
        prompt: Search query/prompt
        context: Optional context dict (for filtering, etc.)

    Returns:
        Dict with {answer: str, citations: List[dict]}

    Logic:
        - Get org store via get_or_create_org_store
        - Call Gemini generateContent with File Search tool
        - Include prompt instructions to filter by organization_id
        - Parse response for answer + citations
        - Map citations back to knowledge items if possible
        - Return structured response
    """
    # Get org store
    store_name = await get_or_create_org_store(db, user)
    if not store_name:
        logger.error("Failed to get org store for query")
        return {
            "answer": "Error: Could not access organization knowledge base. Please contact support.",
            "citations": [],
            "error": "store_unavailable"
        }

    if not is_gemini_available():
        logger.warning("Gemini unavailable - falling back to SQL search")
        return await _sql_fallback_search(db, user, prompt)

    try:
        from app.core.config import settings
        configure_gemini(settings.GEMINI_API_KEY)

        # Build enhanced prompt with org filtering instructions
        enhanced_prompt = f"""Search the organization's knowledge base and answer the following question.

Organization ID: {user.organizationId}
User ID: {user.id}

IMPORTANT: Only use documents that belong to organization_id="{user.organizationId}".

Question: {prompt}

Provide a comprehensive answer based on the knowledge base. Include specific details and cite your sources."""

        # Add context if provided
        if context:
            enhanced_prompt += f"\n\nAdditional Context: {context}"

        # Query using Gemini model with File Search
        model = _genai.GenerativeModel(
            model_name='gemini-2.0-flash-exp',
            tools=[{"file_search": {"store_name": store_name}}]
        )

        response = model.generate_content(enhanced_prompt)

        # Parse response
        answer = response.text if hasattr(response, 'text') else "No answer generated."
        citations = []

        # Extract grounding metadata and citations
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'grounding_metadata'):
                    grounding = candidate.grounding_metadata

                    # Extract grounding chunks (citations)
                    if hasattr(grounding, 'grounding_chunks'):
                        for chunk in grounding.grounding_chunks:
                            citation = {
                                "text": chunk.text if hasattr(chunk, 'text') else "",
                                "source": chunk.source if hasattr(chunk, 'source') else "Unknown"
                            }

                            # Try to extract metadata
                            if hasattr(chunk, 'metadata'):
                                citation["metadata"] = chunk.metadata

                                # Try to map back to knowledge item
                                if isinstance(chunk.metadata, dict):
                                    knowledge_item_id = chunk.metadata.get('knowledge_item_id')
                                    if knowledge_item_id:
                                        citation["knowledge_item_id"] = knowledge_item_id

                            citations.append(citation)

        logger.info(f"Query completed: {len(citations)} citations found")

        return {
            "answer": answer,
            "citations": citations,
            "model": "gemini-2.0-flash-exp",
            "store_name": store_name
        }

    except Exception as e:
        logger.error(f"Failed to query File Search: {e}")
        # Fallback to SQL search
        return await _sql_fallback_search(db, user, prompt)


async def _sql_fallback_search(
    db: Session,
    user: User,
    query: str
) -> Dict[str, Any]:
    """
    SQL-based fallback search when Gemini is unavailable.

    Performs a simple ILIKE search across knowledge items.

    Args:
        db: Database session
        user: User object
        query: Search query

    Returns:
        Dict with {answer: str, citations: List[dict]}
    """
    try:
        # Search knowledge items with ILIKE
        items = db.query(KnowledgeItem).filter(
            KnowledgeItem.userId == user.id,
            (KnowledgeItem.title.ilike(f"%{query}%")) |
            (KnowledgeItem.content.ilike(f"%{query}%"))
        ).limit(10).all()

        if not items:
            return {
                "answer": f"No results found for '{query}' in your knowledge base. Try different keywords or add more knowledge items.",
                "citations": [],
                "fallback": "sql_search",
                "note": "Gemini File Search is currently unavailable. Using basic keyword search."
            }

        # Build answer from results
        citations = []
        results_text = []

        for item in items:
            citations.append({
                "knowledge_item_id": item.id,
                "title": item.title,
                "content": item.content[:200] if item.content else "",
                "type_id": item.typeId,
                "completed": item.completed
            })

            results_text.append(f"- {item.title}: {item.content[:100] if item.content else '(no content)'}...")

        answer = f"""Found {len(items)} matching items for '{query}':

{chr(10).join(results_text)}

Note: This is a basic keyword search. For AI-powered semantic search with natural language understanding, please configure Gemini API key."""

        return {
            "answer": answer,
            "citations": citations,
            "fallback": "sql_search",
            "total": len(items),
            "note": "Using basic SQL search - Gemini File Search unavailable"
        }

    except Exception as e:
        logger.error(f"SQL fallback search failed: {e}")
        return {
            "answer": "Search unavailable. Please try again later.",
            "citations": [],
            "error": str(e)
        }


# Additional helper functions for advanced features

async def list_store_documents(
    db: Session,
    user: User,
    limit: int = 100
) -> Optional[List[Dict[str, Any]]]:
    """
    List documents in the organization's File Search store.

    Args:
        db: Database session
        user: User object
        limit: Maximum documents to return

    Returns:
        List of document info dicts or None if unavailable
    """
    store_name = await get_or_create_org_store(db, user)
    if not store_name or not is_gemini_available():
        return None

    try:
        from app.core.config import settings
        configure_gemini(settings.GEMINI_API_KEY)

        # List files in store
        files = _genai.list_files_in_store(store_name, page_size=limit)

        results = []
        for file in files:
            results.append({
                "name": file.name,
                "display_name": file.display_name,
                "size_bytes": file.size_bytes if hasattr(file, 'size_bytes') else None,
                "create_time": file.create_time.isoformat() if hasattr(file, 'create_time') else None
            })

        return results

    except Exception as e:
        logger.error(f"Failed to list store documents: {e}")
        return None


async def import_voice_transcript(
    db: Session,
    user: Any,
    recording: Any
) -> Optional[str]:
    """
    Import voice transcript to File Search.

    Args:
        db: Database session
        user: User object
        recording: VoiceRecording object

    Returns:
        Document name or None on error
    """
    # Get org store
    store_name = await get_or_create_org_store(db, user)
    if not store_name:
        logger.error("Failed to get org store for voice transcript import")
        return None

    if not is_gemini_available():
        logger.warning("Gemini unavailable - skipping voice transcript import")
        return None

    try:
        from app.core.config import settings
        configure_gemini(settings.GEMINI_API_KEY)

        # Build document content
        content = f"""Voice Transcript

Transcript: {recording.transcript}

Language: {recording.language}
Confidence: {recording.confidence}
Duration: {recording.duration}s
Intent: {recording.intent or 'unknown'}
Created: {recording.createdAt}
User ID: {user.id}
Organization ID: {user.organizationId}
"""

        # Prepare metadata
        metadata = {
            "voice_recording_id": recording.id,
            "user_id": user.id,
            "organization_id": user.organizationId,
            "language": recording.language,
            "confidence": str(recording.confidence or 0),
            "intent": recording.intent or "unknown",
            "created_at": recording.createdAt.isoformat(),
            "kind": "voice_transcript"
        }

        # Upload document to Gemini
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            # Upload file to Gemini
            uploaded_file = _genai.upload_file(
                path=temp_path,
                display_name=f"voice_transcript_{recording.id}.txt"
            )

            # Add to file store
            _genai.add_file_to_store(
                store_name=store_name,
                file_name=uploaded_file.name
            )

            logger.info(f"Imported voice transcript {recording.id} to File Search as {uploaded_file.name}")
            return uploaded_file.name

        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.debug(f"Failed to delete temp file: {e}")

    except Exception as e:
        logger.error(f"Failed to import voice transcript {recording.id}: {e}")
        return None


async def delete_document(
    store_name: str,
    document_name: str,
    api_key: Optional[str] = None
) -> bool:
    """
    Delete a document from File Search store.

    Args:
        store_name: Store name
        document_name: Document name
        api_key: Optional Gemini API key

    Returns:
        True if deletion succeeded
    """
    if not is_gemini_available(api_key):
        logger.warning("Gemini unavailable - skipping document deletion")
        return False

    try:
        from app.core.config import settings
        key = api_key or settings.GEMINI_API_KEY
        configure_gemini(key)

        _genai.delete_file(document_name)
        logger.info(f"Deleted document {document_name} from File Search")
        return True

    except Exception as e:
        logger.error(f"Failed to delete document {document_name}: {e}")
        return False
