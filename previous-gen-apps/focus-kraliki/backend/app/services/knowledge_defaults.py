"""
Knowledge Defaults Service

Ensures users have default knowledge item types on first use.
Mirrors behavior from Focus Mind's DatabaseStorage.initializeDefaultTypes.
"""

from sqlalchemy.orm import Session
from app.models.item_type import ItemType
from app.core.security import generate_id
from typing import List, Dict


DEFAULT_ITEM_TYPES = [
    {
        "name": "Ideas",
        "icon": "Lightbulb",
        "color": "text-yellow-500"
    },
    {
        "name": "Notes",
        "icon": "FileText",
        "color": "text-blue-500"
    },
    {
        "name": "Tasks",
        "icon": "CheckSquare",
        "color": "text-green-500"
    },
    {
        "name": "Plans",
        "icon": "Target",
        "color": "text-purple-500"
    }
]


def ensure_default_item_types(user_id: str, db: Session) -> List[ItemType]:
    """
    Ensure the user has default item types.
    If they already have types, this is a no-op.
    If not, create the default types.

    Args:
        user_id: The user's ID
        db: SQLAlchemy database session

    Returns:
        List of ItemType objects (newly created or existing)
    """
    # Check if user already has item types
    existing_types = db.query(ItemType).filter(ItemType.userId == user_id).all()

    if existing_types:
        # User already has types, don't create defaults
        return existing_types

    # Create default types
    created_types = []
    for default_type in DEFAULT_ITEM_TYPES:
        item_type = ItemType(
            id=generate_id(),
            userId=user_id,
            name=default_type["name"],
            icon=default_type["icon"],
            color=default_type["color"]
        )
        db.add(item_type)
        created_types.append(item_type)

    db.commit()

    # Refresh all to get database-generated fields
    for item_type in created_types:
        db.refresh(item_type)

    return created_types
