"""IVR (Interactive Voice Response) models - SQLAlchemy 2.0"""
from datetime import datetime
from typing import Optional
import enum
from sqlalchemy import String, DateTime, Integer, Boolean, ForeignKey, JSON, Text, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class IVRActionType(str, enum.Enum):
    """IVR action types"""
    TRANSFER = "transfer"
    QUEUE = "queue"
    MENU = "menu"
    VOICEMAIL = "voicemail"
    HANGUP = "hangup"


class NoInputAction(str, enum.Enum):
    """Action when no input received"""
    REPEAT = "repeat"
    TRANSFER = "transfer"
    VOICEMAIL = "voicemail"
    HANGUP = "hangup"


class IVRConfig(Base):
    """IVR system configuration"""
    __tablename__ = "ivr_configs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))

    # Main menu reference
    main_menu_id: Mapped[Optional[str]] = mapped_column(ForeignKey("ivr_menus.id", ondelete="SET NULL"), nullable=True)

    # Settings
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization: Mapped["Organization"] = relationship()
    main_menu: Mapped[Optional["IVRMenu"]] = relationship(foreign_keys=[main_menu_id])

    __table_args__ = (
        Index("idx_ivr_config_org", "organization_id"),
    )


class IVRMenu(Base):
    """IVR menu definition"""
    __tablename__ = "ivr_menus"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))

    # Menu properties
    name: Mapped[str] = mapped_column(String)
    greeting: Mapped[str] = mapped_column(Text)  # TTS text or audio file URL

    # Behavior settings
    timeout: Mapped[int] = mapped_column(Integer, default=5)  # seconds
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    no_input_action: Mapped[NoInputAction] = mapped_column(SQLEnum(NoInputAction), default=NoInputAction.REPEAT)
    no_input_target: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    invalid_input_action: Mapped[NoInputAction] = mapped_column(SQLEnum(NoInputAction), default=NoInputAction.REPEAT)
    invalid_input_target: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Status
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization: Mapped["Organization"] = relationship()
    options: Mapped[list["IVRMenuOption"]] = relationship(back_populates="menu", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_ivr_menu_org", "organization_id"),
    )


class IVRMenuOption(Base):
    """IVR menu option (button press)"""
    __tablename__ = "ivr_menu_options"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    menu_id: Mapped[str] = mapped_column(ForeignKey("ivr_menus.id", ondelete="CASCADE"))

    # Option details
    digit: Mapped[str] = mapped_column(String(1))  # 0-9, *, #
    description: Mapped[str] = mapped_column(String)
    action: Mapped[IVRActionType] = mapped_column(SQLEnum(IVRActionType))
    target: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Queue name, phone number, menu ID, etc.

    # Additional data defined for the option
    metadata_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    menu: Mapped["IVRMenu"] = relationship(back_populates="options")

    __table_args__ = (
        Index("idx_ivr_option_menu", "menu_id"),
    )


class IVRFlow(Base):
    """IVR flow - sequence of menus and actions"""
    __tablename__ = "ivr_flows"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))

    # Flow properties
    name: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_menu_id: Mapped[str] = mapped_column(ForeignKey("ivr_menus.id", ondelete="CASCADE"))

    # Status
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization: Mapped["Organization"] = relationship()
    start_menu: Mapped["IVRMenu"] = relationship()
    steps: Mapped[list["IVRFlowStep"]] = relationship(back_populates="flow", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_ivr_flow_org", "organization_id"),
    )


class IVRFlowStep(Base):
    """Individual step in IVR flow"""
    __tablename__ = "ivr_flow_steps"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    flow_id: Mapped[str] = mapped_column(ForeignKey("ivr_flows.id", ondelete="CASCADE"))

    # Step properties
    step_type: Mapped[IVRActionType] = mapped_column(SQLEnum(IVRActionType))
    target: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    conditions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Conditional branching
    order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    flow: Mapped["IVRFlow"] = relationship(back_populates="steps")

    __table_args__ = (
        Index("idx_ivr_step_flow", "flow_id", "order"),
    )
