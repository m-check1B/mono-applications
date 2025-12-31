"""IVR schemas - Pydantic models for IVR validation"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class IVRActionType(str, Enum):
    """IVR action types"""
    TRANSFER = "transfer"
    QUEUE = "queue"
    MENU = "menu"
    VOICEMAIL = "voicemail"
    HANGUP = "hangup"


class NoInputAction(str, Enum):
    """No input action"""
    REPEAT = "repeat"
    TRANSFER = "transfer"
    VOICEMAIL = "voicemail"
    HANGUP = "hangup"


class IVRMenuOptionCreate(BaseModel):
    """Schema for creating IVR menu option"""
    digit: str = Field(..., pattern="^[0-9*#]$")
    description: str
    action: IVRActionType
    target: Optional[str] = None
    metadata: Optional[dict] = Field(None, alias="metadata_payload")

    model_config = ConfigDict(populate_by_name=True)


class IVRMenuOptionResponse(IVRMenuOptionCreate):
    """Schema for IVR menu option response"""
    id: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class IVRMenuCreate(BaseModel):
    """Schema for creating IVR menu"""
    name: str
    greeting: str
    options: List[IVRMenuOptionCreate]
    timeout: int = Field(default=5, ge=1, le=60)
    max_retries: int = Field(default=3, ge=1, le=10)
    no_input_action: NoInputAction = NoInputAction.REPEAT
    no_input_target: Optional[str] = None
    invalid_input_action: NoInputAction = NoInputAction.REPEAT
    invalid_input_target: Optional[str] = None


class IVRMenuUpdate(BaseModel):
    """Schema for updating IVR menu"""
    name: Optional[str] = None
    greeting: Optional[str] = None
    options: Optional[List[IVRMenuOptionCreate]] = None
    timeout: Optional[int] = Field(None, ge=1, le=60)
    max_retries: Optional[int] = Field(None, ge=1, le=10)
    no_input_action: Optional[NoInputAction] = None
    no_input_target: Optional[str] = None
    invalid_input_action: Optional[NoInputAction] = None
    invalid_input_target: Optional[str] = None


class IVRMenuResponse(BaseModel):
    """Schema for IVR menu response"""
    id: str
    name: str
    greeting: str
    options: List[IVRMenuOptionResponse]
    timeout: int
    max_retries: int
    no_input_action: NoInputAction
    no_input_target: Optional[str]
    invalid_input_action: NoInputAction
    invalid_input_target: Optional[str]
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IVRConfigResponse(BaseModel):
    """Schema for IVR configuration response"""
    id: str
    organization_id: str
    main_menu_id: Optional[str]
    main_menu: Optional[IVRMenuResponse]
    settings: Optional[dict]
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IVRConfigUpdate(BaseModel):
    """Schema for updating IVR config"""
    main_menu_id: Optional[str] = None
    settings: Optional[dict] = None


class IVRFlowStepCreate(BaseModel):
    """Schema for creating IVR flow step"""
    type: IVRActionType
    target: Optional[str] = None
    conditions: Optional[dict] = None


class IVRFlowCreate(BaseModel):
    """Schema for creating IVR flow"""
    name: str
    description: Optional[str] = None
    start_menu_id: str
    steps: List[IVRFlowStepCreate]


class IVRFlowResponse(BaseModel):
    """Schema for IVR flow response"""
    id: str
    organization_id: str
    name: str
    description: Optional[str]
    start_menu_id: str
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
