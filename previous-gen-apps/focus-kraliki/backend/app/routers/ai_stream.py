from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from typing import AsyncGenerator
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai/stream", tags=["ai-streaming"])

# Try to use ai-core package first, fall back to local implementation
_use_ai_core = False
_claude_provider = None
_openai_provider = None

try:
    from ai_core import (
        create_provider,
        LLMProvider,
        Message,
        MessageRole,
        CompletionConfig,
    )
    from ai_core.streaming import stream_to_sse
    _use_ai_core = True
except ImportError:
    # Fallback to direct SDK usage
    from anthropic import Anthropic
    from openai import OpenAI


def get_claude_provider():
    """Get Claude provider (ai-core or direct SDK)."""
    global _claude_provider
    if _use_ai_core:
        if _claude_provider is None:
            _claude_provider = create_provider(
                LLMProvider.ANTHROPIC,
                api_key=settings.ANTHROPIC_API_KEY,
            )
        return _claude_provider
    else:
        # Legacy fallback
        return Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def get_openai_provider():
    """Get OpenAI provider (ai-core or direct SDK)."""
    global _openai_provider
    if _use_ai_core:
        if _openai_provider is None:
            _openai_provider = create_provider(
                LLMProvider.OPENAI,
                api_key=settings.OPENAI_API_KEY,
            )
        return _openai_provider
    else:
        # Legacy fallback
        return OpenAI(api_key=settings.OPENAI_API_KEY)


async def stream_claude_response(
    messages: list,
    model: str = "claude-opus-4-20250514"
) -> AsyncGenerator[str, None]:
    """Stream Claude response token by token"""
    if _use_ai_core:
        provider = get_claude_provider()
        ai_messages = [
            Message(role=MessageRole(m["role"]), content=m["content"])
            for m in messages
        ]
        config = CompletionConfig(model=model, max_tokens=2000)

        try:
            async for chunk in provider.stream(ai_messages, config):
                yield f"data: {json.dumps({'type': chunk.chunk_type, 'content': chunk.content})}\n\n"
                await asyncio.sleep(0)
        except Exception as e:
            logger.exception("Claude streaming failed (ai-core)")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    else:
        # Legacy fallback
        try:
            client = get_claude_provider()
            with client.messages.stream(
                model=model,
                max_tokens=2000,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    if text:
                        yield f"data: {json.dumps({'type': 'token', 'content': text})}\n\n"
                        await asyncio.sleep(0)

            yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"
        except Exception as e:
            logger.exception("Claude streaming failed (legacy)")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"


async def stream_openai_response(
    messages: list,
    model: str = "gpt-4o"
) -> AsyncGenerator[str, None]:
    """Stream OpenAI response token by token"""
    if _use_ai_core:
        provider = get_openai_provider()
        ai_messages = [
            Message(role=MessageRole(m["role"]), content=m["content"])
            for m in messages
        ]
        config = CompletionConfig(model=model, max_tokens=2000)

        try:
            async for chunk in provider.stream(ai_messages, config):
                yield f"data: {json.dumps({'type': chunk.chunk_type, 'content': chunk.content})}\n\n"
                await asyncio.sleep(0)
        except Exception as e:
            logger.exception("OpenAI streaming failed (ai-core)")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    else:
        # Legacy fallback
        try:
            client = get_openai_provider()
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
                    await asyncio.sleep(0)

            yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"
        except Exception as e:
            logger.exception("OpenAI streaming failed (legacy)")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"


@router.post("/chat")
async def stream_chat(
    message: str,
    conversation_history: list = None,
    use_high_reasoning: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Stream AI chat response token by token using Server-Sent Events"""

    # Prepare messages
    messages = []
    if conversation_history:
        messages = conversation_history
    messages.append({"role": "user", "content": message})

    # Choose streaming function based on model
    if use_high_reasoning:
        stream_generator = stream_openai_response(messages)
    else:
        stream_generator = stream_claude_response(messages)

    return StreamingResponse(
        stream_generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/test")
async def test_stream():
    """Test streaming endpoint"""
    async def generate():
        test_message = "This is a test of the streaming system. "
        words = test_message.split()
        for word in words:
            yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"
            await asyncio.sleep(0.1)
        yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
