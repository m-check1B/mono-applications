"""
Knowledge AI Router

AI-powered knowledge management with OpenRouter function calling.
Allows AI to create, update, and list knowledge items via function calls.

Port from Focus Mind's /api/chat/send logic.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from openai import OpenAI
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import os
import json

from app.core.database import get_db
from app.core.security import get_current_user, generate_id
from app.models.user import User
from app.models.item_type import ItemType
from app.models.knowledge_item import KnowledgeItem


router = APIRouter(prefix="/knowledge-ai", tags=["knowledge-ai"])

# Free tier limit
FREE_TIER_LIMIT = 100


# Request/Response schemas
class Message(BaseModel):
    role: str
    content: str


class KnowledgeChatRequest(BaseModel):
    message: str
    conversationHistory: Optional[List[Message]] = []
    model: Optional[str] = "google/gemini-2.5-flash-preview-09-2025"


class KnowledgeChatResponse(BaseModel):
    response: str
    model: str
    toolCalls: Optional[List[Dict[str, Any]]] = []
    usageCount: Optional[int] = None
    remainingUsage: Optional[int] = None


# OpenRouter client (reuse from ai.py pattern)
_openrouter_client = None


def get_openrouter_client(api_key: Optional[str] = None):
    """Get OpenRouter client with optional user API key"""
    global _openrouter_client

    if api_key:
        # User provided their own key (BYOK)
        return OpenAI(
            api_key=api_key,
            base_url=os.environ.get("AI_INTEGRATIONS_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        )

    # Use system key
    if _openrouter_client is None:
        _openrouter_client = OpenAI(
            api_key=os.environ.get("AI_INTEGRATIONS_OPENROUTER_API_KEY"),
            base_url=os.environ.get("AI_INTEGRATIONS_OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        )
    return _openrouter_client


# Tool function definitions for OpenRouter
def get_knowledge_tools():
    """Define the tools available to the AI"""
    return [
        {
            "type": "function",
            "function": {
                "name": "create_knowledge_item",
                "description": "Create a new knowledge item (idea, note, task, or plan). Use this when the user wants to save information, create a task, or capture an idea.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "typeId": {
                            "type": "string",
                            "description": "The ID of the item type (Ideas, Notes, Tasks, or Plans). You must get this from list_knowledge_item_types first."
                        },
                        "title": {
                            "type": "string",
                            "description": "A concise title for the knowledge item"
                        },
                        "content": {
                            "type": "string",
                            "description": "Detailed content or description of the item"
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "Whether the item is completed (mainly for tasks)",
                            "default": False
                        }
                    },
                    "required": ["typeId", "title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_knowledge_item",
                "description": "Update an existing knowledge item. Use this to modify the title, content, or completion status of an item.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "itemId": {
                            "type": "string",
                            "description": "The ID of the knowledge item to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New title for the item (optional)"
                        },
                        "content": {
                            "type": "string",
                            "description": "New content for the item (optional)"
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "Whether the item is completed (optional)"
                        }
                    },
                    "required": ["itemId"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_knowledge_items",
                "description": "List knowledge items, optionally filtered by type. Use this to retrieve tasks, notes, ideas, or plans.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "typeId": {
                            "type": "string",
                            "description": "Filter by item type ID (optional)"
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "Filter by completion status (optional)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of items to return",
                            "default": 20
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_knowledge_item_types",
                "description": "List all available knowledge item types (Ideas, Notes, Tasks, Plans, etc.). Use this first to get type IDs before creating items.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    ]


# Tool execution functions
def execute_create_knowledge_item(
    user_id: str,
    typeId: str,
    title: str,
    content: Optional[str] = None,
    completed: bool = False,
    db: Session = None
) -> Dict[str, Any]:
    """Execute the create_knowledge_item tool"""
    # Verify typeId belongs to user
    item_type = db.query(ItemType).filter(
        ItemType.id == typeId,
        ItemType.userId == user_id
    ).first()

    if not item_type:
        return {"error": "Item type not found or doesn't belong to user"}

    # Create the knowledge item
    knowledge_item = KnowledgeItem(
        id=generate_id(),
        userId=user_id,
        typeId=typeId,
        title=title,
        content=content,
        completed=completed
    )

    db.add(knowledge_item)
    db.commit()
    db.refresh(knowledge_item)

    return {
        "success": True,
        "item": {
            "id": knowledge_item.id,
            "typeId": knowledge_item.typeId,
            "title": knowledge_item.title,
            "content": knowledge_item.content,
            "completed": knowledge_item.completed,
            "createdAt": knowledge_item.createdAt.isoformat()
        }
    }


def execute_update_knowledge_item(
    user_id: str,
    itemId: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    completed: Optional[bool] = None,
    db: Session = None
) -> Dict[str, Any]:
    """Execute the update_knowledge_item tool"""
    # Get the item
    knowledge_item = db.query(KnowledgeItem).filter(
        KnowledgeItem.id == itemId,
        KnowledgeItem.userId == user_id
    ).first()

    if not knowledge_item:
        return {"error": "Knowledge item not found or doesn't belong to user"}

    # Update fields
    if title is not None:
        knowledge_item.title = title
    if content is not None:
        knowledge_item.content = content
    if completed is not None:
        knowledge_item.completed = completed

    db.commit()
    db.refresh(knowledge_item)

    return {
        "success": True,
        "item": {
            "id": knowledge_item.id,
            "typeId": knowledge_item.typeId,
            "title": knowledge_item.title,
            "content": knowledge_item.content,
            "completed": knowledge_item.completed,
            "updatedAt": knowledge_item.updatedAt.isoformat()
        }
    }


def execute_list_knowledge_items(
    user_id: str,
    typeId: Optional[str] = None,
    completed: Optional[bool] = None,
    limit: int = 20,
    db: Session = None
) -> Dict[str, Any]:
    """Execute the list_knowledge_items tool"""
    query = db.query(KnowledgeItem).filter(KnowledgeItem.userId == user_id)

    if typeId:
        query = query.filter(KnowledgeItem.typeId == typeId)
    if completed is not None:
        query = query.filter(KnowledgeItem.completed == completed)

    items = query.order_by(KnowledgeItem.createdAt.desc()).limit(limit).all()

    return {
        "success": True,
        "items": [
            {
                "id": item.id,
                "typeId": item.typeId,
                "title": item.title,
                "content": item.content,
                "completed": item.completed,
                "createdAt": item.createdAt.isoformat()
            }
            for item in items
        ],
        "total": len(items)
    }


def execute_list_knowledge_item_types(
    user_id: str,
    db: Session = None
) -> Dict[str, Any]:
    """Execute the list_knowledge_item_types tool"""
    item_types = db.query(ItemType).filter(ItemType.userId == user_id).all()

    return {
        "success": True,
        "types": [
            {
                "id": item_type.id,
                "name": item_type.name,
                "icon": item_type.icon,
                "color": item_type.color
            }
            for item_type in item_types
        ],
        "total": len(item_types)
    }


@router.post("/chat", response_model=KnowledgeChatResponse)
async def knowledge_chat(
    request: KnowledgeChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI-powered knowledge chat with function calling.

    The AI can create, update, and list knowledge items via function calls.
    Tracks usage for non-premium users without BYOK.
    """
    # Determine which API key to use
    using_system_key = not current_user.openRouterApiKey

    # Check usage limits for non-premium users using system key
    if using_system_key and not current_user.isPremium:
        if current_user.usageCount >= FREE_TIER_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Free tier limit reached ({FREE_TIER_LIMIT} interactions). Please upgrade to premium or add your own OpenRouter API key."
            )

    # Get OpenRouter client
    api_key = current_user.openRouterApiKey if current_user.openRouterApiKey else None
    client = get_openrouter_client(api_key)

    # Build message history
    messages = [{"role": m.role, "content": m.content} for m in request.conversationHistory]
    messages.append({"role": "user", "content": request.message})

    # Add system message with context
    system_message = """You are a helpful AI assistant that helps users manage their knowledge.
You can create ideas, notes, tasks, and plans for users.

Before creating items, ALWAYS call list_knowledge_item_types first to get the available types and their IDs.

When the user wants to:
- Save an idea or brainstorm -> use "Ideas" type
- Take notes or record information -> use "Notes" type
- Create a task or todo item -> use "Tasks" type
- Make a plan or strategy -> use "Plans" type

Be conversational and helpful. After creating items, confirm what you created."""

    messages.insert(0, {"role": "system", "content": system_message})

    try:
        # First AI call with tools
        response = client.chat.completions.create(
            model=request.model,
            messages=messages,
            tools=get_knowledge_tools(),
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message
        tool_calls = []
        tool_results = []

        # Execute any tool calls
        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Execute the appropriate function
                if function_name == "create_knowledge_item":
                    result = execute_create_knowledge_item(
                        user_id=current_user.id,
                        db=db,
                        **function_args
                    )
                elif function_name == "update_knowledge_item":
                    result = execute_update_knowledge_item(
                        user_id=current_user.id,
                        db=db,
                        **function_args
                    )
                elif function_name == "list_knowledge_items":
                    result = execute_list_knowledge_items(
                        user_id=current_user.id,
                        db=db,
                        **function_args
                    )
                elif function_name == "list_knowledge_item_types":
                    result = execute_list_knowledge_item_types(
                        user_id=current_user.id,
                        db=db
                    )
                else:
                    result = {"error": f"Unknown function: {function_name}"}

                tool_results.append({
                    "function": function_name,
                    "arguments": function_args,
                    "result": result
                })

            # Second AI call with tool results to get natural language response
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })

            # Add tool results as separate messages
            for i, tool_call in enumerate(assistant_message.tool_calls):
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_results[i]["result"])
                })

            # Get final response
            final_response = client.chat.completions.create(
                model=request.model,
                messages=messages
            )

            final_text = final_response.choices[0].message.content
        else:
            # No tool calls, just return the response
            final_text = assistant_message.content or "I'm ready to help you manage your knowledge. What would you like to do?"

        # Increment usage count for non-premium users using system key
        if using_system_key and not current_user.isPremium:
            current_user.usageCount += 1
            db.commit()

        # Calculate remaining usage
        remaining_usage = None
        if using_system_key and not current_user.isPremium:
            remaining_usage = FREE_TIER_LIMIT - current_user.usageCount

        return KnowledgeChatResponse(
            response=final_text,
            model=request.model,
            toolCalls=tool_results,
            usageCount=current_user.usageCount if using_system_key and not current_user.isPremium else None,
            remainingUsage=remaining_usage
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI chat error: {str(e)}"
        )
