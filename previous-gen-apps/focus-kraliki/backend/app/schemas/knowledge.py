from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# ItemType Schemas

class ItemTypeBase(BaseModel):
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None

class ItemTypeCreate(ItemTypeBase):
    pass

class ItemTypeUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None

class ItemTypeResponse(ItemTypeBase):
    id: str
    userId: str
    createdAt: datetime

    class Config:
        from_attributes = True

class ItemTypeListResponse(BaseModel):
    itemTypes: List[ItemTypeResponse]
    total: int

# KnowledgeItem Schemas

class KnowledgeItemBase(BaseModel):
    typeId: str
    title: str
    content: Optional[str] = None
    item_metadata: Optional[Dict[str, Any]] = None
    completed: bool = False

class KnowledgeItemCreate(KnowledgeItemBase):
    pass

class KnowledgeItemUpdate(BaseModel):
    typeId: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    item_metadata: Optional[Dict[str, Any]] = None
    completed: Optional[bool] = None

class KnowledgeItemResponse(KnowledgeItemBase):
    id: str
    userId: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

class KnowledgeItemListResponse(BaseModel):
    items: List[KnowledgeItemResponse]
    total: int
