"""
Captures Router - Seamless content capture with AI processing

This is the "dump in" feature for Focus by Kraliki.
Drop anything → AI processes → becomes context.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
import base64
import httpx
import logging
import json
from datetime import datetime, timedelta

from app.core.database import get_db, SessionLocal
from app.core.security import get_current_user, generate_id
from app.models.user import User
from app.models.item_type import ItemType
from app.models.knowledge_item import KnowledgeItem
from app.schemas.capture import (
    CaptureCreate,
    CaptureProcessed,
    CaptureResponse,
    CaptureListResponse,
    CaptureContextResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/captures", tags=["captures"])

# Constants
CAPTURE_TYPE_NAME = "Capture"
CAPTURE_TYPE_ICON = "📎"
CAPTURE_TYPE_COLOR = "#6366f1"  # Indigo


async def get_or_create_capture_type(user_id: str, db: Session) -> ItemType:
    """Get or create the Capture item type for a user"""
    capture_type = db.query(ItemType).filter(
        ItemType.userId == user_id,
        ItemType.name == CAPTURE_TYPE_NAME
    ).first()

    if not capture_type:
        capture_type = ItemType(
            id=generate_id(),
            userId=user_id,
            name=CAPTURE_TYPE_NAME,
            icon=CAPTURE_TYPE_ICON,
            color=CAPTURE_TYPE_COLOR
        )
        db.add(capture_type)
        db.commit()
        db.refresh(capture_type)

    return capture_type


async def process_with_gemini_vision(image_base64: str, context: Optional[str] = None) -> CaptureProcessed:
    """Process image with Gemini Vision API"""
    import os

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set, using fallback processing")
        return CaptureProcessed(
            summary="Image captured (AI processing unavailable)",
            key_points=["Image uploaded successfully"],
            entities=[],
            suggested_tags=["image", "capture"],
            action_items=[]
        )

    try:
        prompt = """Analyze this image and provide:
1. A concise summary (1-2 sentences)
2. Key points or information visible
3. Any named entities (people, companies, products, places)
4. Suggested tags for categorization
5. Any potential action items or tasks implied

Respond in JSON format:
{
    "summary": "...",
    "key_points": ["...", "..."],
    "entities": ["...", "..."],
    "suggested_tags": ["...", "..."],
    "action_items": ["...", "..."]
}"""

        if context:
            prompt += f"\n\nUser context: {context}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}",
                json={
                    "contents": [{
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/png",
                                    "data": image_base64
                                }
                            }
                        ]
                    }]
                }
            )

            if response.status_code == 200:
                result = response.json()
                text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
                # Clean up markdown code blocks if present
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                parsed = json.loads(text)
                return CaptureProcessed(**parsed)
            else:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")

    except Exception as e:
        logger.error(f"Error processing image with Gemini: {e}")

    return CaptureProcessed(
        summary="Image captured",
        key_points=["Image uploaded successfully"],
        entities=[],
        suggested_tags=["image", "capture"],
        action_items=[]
    )


async def process_url(url: str, context: Optional[str] = None) -> CaptureProcessed:
    """Fetch and process URL content"""
    import os

    try:
        # Fetch URL content
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers={"User-Agent": "Focus-Kraliki/1.0"})
            content = response.text[:10000]  # Limit content size

        # Extract title from HTML if present
        title = url
        if "<title>" in content.lower():
            start = content.lower().find("<title>") + 7
            end = content.lower().find("</title>")
            if end > start:
                title = content[start:end].strip()

        # Process with AI
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return CaptureProcessed(
                summary=f"Link captured: {title}",
                key_points=[f"URL: {url}"],
                entities=[],
                suggested_tags=["link", "web"],
                action_items=[]
            )

        # Use Gemini for summarization
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            prompt = f"""Analyze this web content and provide:
1. A concise summary (1-2 sentences)
2. Key points or takeaways
3. Named entities mentioned
4. Suggested tags
5. Any action items implied

URL: {url}
Content snippet: {content[:3000]}

Respond in JSON:
{{"summary": "...", "key_points": [...], "entities": [...], "suggested_tags": [...], "action_items": [...]}}"""

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={gemini_key}",
                    json={"contents": [{"parts": [{"text": prompt}]}]}
                )

                if response.status_code == 200:
                    result = response.json()
                    text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
                    if text.startswith("```"):
                        text = text.split("```")[1]
                        if text.startswith("json"):
                            text = text[4:]
                    parsed = json.loads(text)
                    return CaptureProcessed(**parsed)

    except Exception as e:
        logger.error(f"Error processing URL {url}: {e}")

    return CaptureProcessed(
        summary=f"Link captured: {url}",
        key_points=[],
        entities=[],
        suggested_tags=["link"],
        action_items=[]
    )


async def process_text(text: str, context: Optional[str] = None) -> CaptureProcessed:
    """Process text content with AI"""
    import os

    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        # Fallback: simple extraction
        words = text.split()
        return CaptureProcessed(
            summary=text[:200] + "..." if len(text) > 200 else text,
            key_points=[],
            entities=[],
            suggested_tags=["note", "text"],
            action_items=[]
        )

    try:
        prompt = f"""Analyze this text and provide:
1. A concise summary (1-2 sentences)
2. Key points or takeaways
3. Named entities (people, companies, concepts)
4. Suggested tags for categorization
5. Any action items or tasks implied

Text: {text[:5000]}

Respond in JSON:
{{"summary": "...", "key_points": [...], "entities": [...], "suggested_tags": [...], "action_items": [...]}}"""

        if context:
            prompt += f"\n\nUser context: {context}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={gemini_key}",
                json={"contents": [{"parts": [{"text": prompt}]}]}
            )

            if response.status_code == 200:
                result = response.json()
                text_response = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
                if text_response.startswith("```"):
                    text_response = text_response.split("```")[1]
                    if text_response.startswith("json"):
                        text_response = text_response[4:]
                parsed = json.loads(text_response)
                return CaptureProcessed(**parsed)

    except Exception as e:
        logger.error(f"Error processing text: {e}")

    return CaptureProcessed(
        summary=text[:200] + "..." if len(text) > 200 else text,
        key_points=[],
        entities=[],
        suggested_tags=["note"],
        action_items=[]
    )


def capture_to_response(item: KnowledgeItem) -> CaptureResponse:
    """Convert KnowledgeItem to CaptureResponse"""
    metadata = item.item_metadata or {}
    processed = CaptureProcessed(
        summary=metadata.get("ai_summary", ""),
        key_points=metadata.get("ai_key_points", []),
        entities=metadata.get("ai_entities", []),
        suggested_tags=metadata.get("ai_tags", []),
        action_items=metadata.get("ai_action_items", []),
        relevance_context=metadata.get("ai_relevance")
    )

    return CaptureResponse(
        id=item.id,
        userId=item.userId,
        source_type=metadata.get("source_type", "text"),
        title=item.title,
        content=item.content,
        original_content=metadata.get("original_content", ""),
        processed=processed,
        createdAt=item.createdAt,
        updatedAt=item.updatedAt
    )


# ========== API Endpoints ==========

@router.post("", response_model=CaptureResponse)
async def create_capture(
    capture: CaptureCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new capture from any content type.

    Accepts:
    - image: base64 encoded image data
    - url: web URL to fetch and summarize
    - text: raw text content
    - file: file reference (handled separately via upload endpoint)

    AI automatically processes and extracts insights.
    """
    # Get or create capture type
    capture_type = await get_or_create_capture_type(current_user.id, db)

    # Process based on source type
    if capture.source_type == "image":
        processed = await process_with_gemini_vision(capture.content, capture.context)
        title = capture.title or processed.summary[:50] + "..."
    elif capture.source_type == "url":
        processed = await process_url(capture.content, capture.context)
        title = capture.title or processed.summary[:50] + "..."
    else:  # text or file
        processed = await process_text(capture.content, capture.context)
        title = capture.title or processed.summary[:50] + "..."

    # Store as KnowledgeItem
    item = KnowledgeItem(
        id=generate_id(),
        userId=current_user.id,
        typeId=capture_type.id,
        title=title,
        content=processed.summary,
        item_metadata={
            "source_type": capture.source_type,
            "original_content": capture.content[:1000] if capture.source_type == "text" else capture.content[:100],  # Truncate for storage
            "ai_summary": processed.summary,
            "ai_key_points": processed.key_points,
            "ai_entities": processed.entities,
            "ai_tags": processed.suggested_tags,
            "ai_action_items": processed.action_items,
            "user_context": capture.context,
            "captured_at": datetime.utcnow().isoformat()
        }
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    logger.info(f"Created capture {item.id} for user {current_user.id} (type: {capture.source_type})")

    return capture_to_response(item)


@router.post("/upload", response_model=CaptureResponse)
async def upload_capture(
    file: UploadFile = File(...),
    context: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a file as a capture (images, documents, etc.)

    Supports: PNG, JPG, GIF, PDF, TXT, MD
    """
    # Read file content
    content = await file.read()

    # Determine type and process
    content_type = file.content_type or ""

    if content_type.startswith("image/"):
        # Process as image
        base64_content = base64.b64encode(content).decode("utf-8")
        capture = CaptureCreate(
            source_type="image",
            content=base64_content,
            title=file.filename,
            context=context
        )
    elif content_type in ["text/plain", "text/markdown"]:
        # Process as text
        text_content = content.decode("utf-8")
        capture = CaptureCreate(
            source_type="text",
            content=text_content,
            title=file.filename,
            context=context
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {content_type}. Supported: images, text files."
        )

    # Reuse create_capture logic
    capture_type = await get_or_create_capture_type(current_user.id, db)

    if capture.source_type == "image":
        processed = await process_with_gemini_vision(capture.content, capture.context)
    else:
        processed = await process_text(capture.content, capture.context)

    title = capture.title or processed.summary[:50] + "..."

    item = KnowledgeItem(
        id=generate_id(),
        userId=current_user.id,
        typeId=capture_type.id,
        title=title,
        content=processed.summary,
        item_metadata={
            "source_type": capture.source_type,
            "original_filename": file.filename,
            "content_type": content_type,
            "ai_summary": processed.summary,
            "ai_key_points": processed.key_points,
            "ai_entities": processed.entities,
            "ai_tags": processed.suggested_tags,
            "ai_action_items": processed.action_items,
            "user_context": context,
            "captured_at": datetime.utcnow().isoformat()
        }
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return capture_to_response(item)


@router.get("", response_model=CaptureListResponse)
async def list_captures(
    limit: int = 20,
    offset: int = 0,
    since_hours: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List recent captures for the current user.

    Optionally filter by time (since_hours) to get recent context.
    """
    capture_type = await get_or_create_capture_type(current_user.id, db)

    query = db.query(KnowledgeItem).filter(
        KnowledgeItem.userId == current_user.id,
        KnowledgeItem.typeId == capture_type.id
    )

    if since_hours:
        cutoff = datetime.utcnow() - timedelta(hours=since_hours)
        query = query.filter(KnowledgeItem.createdAt >= cutoff)

    total = query.count()
    items = query.order_by(KnowledgeItem.createdAt.desc()).offset(offset).limit(limit).all()

    return CaptureListResponse(
        captures=[capture_to_response(item) for item in items],
        total=total
    )


@router.get("/context", response_model=CaptureContextResponse)
async def get_capture_context(
    hours: int = 24,
    max_captures: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent captures formatted for AI chat context injection.

    Returns a summary of recent captures that can be injected into
    AI conversations for contextual awareness.
    """
    capture_type = await get_or_create_capture_type(current_user.id, db)
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    items = db.query(KnowledgeItem).filter(
        KnowledgeItem.userId == current_user.id,
        KnowledgeItem.typeId == capture_type.id,
        KnowledgeItem.createdAt >= cutoff
    ).order_by(KnowledgeItem.createdAt.desc()).limit(max_captures).all()

    if not items:
        return CaptureContextResponse(
            context_summary="No recent captures.",
            captures=[],
            total_captures=0
        )

    # Build context summary
    summaries = []
    captures_data = []

    for item in items:
        metadata = item.item_metadata or {}
        summary = metadata.get("ai_summary", item.title)
        summaries.append(f"- {summary}")

        captures_data.append({
            "id": item.id,
            "title": item.title,
            "summary": summary,
            "source_type": metadata.get("source_type", "unknown"),
            "key_points": metadata.get("ai_key_points", []),
            "entities": metadata.get("ai_entities", []),
            "captured_at": item.createdAt.isoformat()
        })

    context_summary = f"Recent captures ({len(items)} items in last {hours}h):\n" + "\n".join(summaries)

    return CaptureContextResponse(
        context_summary=context_summary,
        captures=captures_data,
        total_captures=len(items)
    )


@router.get("/{capture_id}", response_model=CaptureResponse)
async def get_capture(
    capture_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific capture by ID"""
    capture_type = await get_or_create_capture_type(current_user.id, db)

    item = db.query(KnowledgeItem).filter(
        KnowledgeItem.id == capture_id,
        KnowledgeItem.userId == current_user.id,
        KnowledgeItem.typeId == capture_type.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Capture not found")

    return capture_to_response(item)


@router.delete("/{capture_id}")
async def delete_capture(
    capture_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a capture"""
    capture_type = await get_or_create_capture_type(current_user.id, db)

    item = db.query(KnowledgeItem).filter(
        KnowledgeItem.id == capture_id,
        KnowledgeItem.userId == current_user.id,
        KnowledgeItem.typeId == capture_type.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Capture not found")

    db.delete(item)
    db.commit()

    return {"message": "Capture deleted", "id": capture_id}
