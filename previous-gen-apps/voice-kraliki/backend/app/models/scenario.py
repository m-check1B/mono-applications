"""Scenario and scenario node models for training simulations."""

from datetime import UTC, datetime

from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Scenario(Base):
    """Training scenario model."""

    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), default="General", nullable=False)
    difficulty = Column(String(50), default="Medium", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    entry_node_id = Column(Integer, nullable=True)  # ID of the starting node

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    nodes = relationship("ScenarioNode", back_populates="scenario", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Scenario(id={self.id}, name={self.name})>"


class ScenarioNode(Base):
    """A single node in a scenario flow."""

    __tablename__ = "scenario_nodes"

    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)

    node_type = Column(String(50), nullable=False)  # statement, question, conditional, goTo, setVariable, end
    name = Column(String(200), nullable=False)
    text_content = Column(Text, nullable=True)

    # Flow control
    next_node_id = Column(Integer, nullable=True)  # For linear flow (statement, setVariable)

    # Conditional logic
    condition_expression = Column(String(500), nullable=True)
    variable_name = Column(String(100), nullable=True)
    variable_value = Column(String(200), nullable=True)

    # Relationships
    scenario = relationship("Scenario", back_populates="nodes")
    options = relationship("ScenarioOption", back_populates="node", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ScenarioNode(id={self.id}, name={self.name}, type={self.node_type})>"


class ScenarioOption(Base):
    """A choice in a 'question' node."""

    __tablename__ = "scenario_options"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("scenario_nodes.id"), nullable=False)

    label = Column(String(500), nullable=False)
    next_node_id = Column(Integer, nullable=True)

    # Relationships
    node = relationship("ScenarioNode", back_populates="options")

    def __repr__(self):
        return f"<ScenarioOption(id={self.id}, label={self.label[:20]}...)>"


# Pydantic models for API

class ScenarioOptionBase(BaseModel):
    label: str
    next_node_id: int | None = None

class ScenarioOptionCreate(ScenarioOptionBase):
    pass

class ScenarioOptionResponse(ScenarioOptionBase):
    id: int
    node_id: int

    class Config:
        from_attributes = True


class ScenarioNodeBase(BaseModel):
    node_type: str
    name: str
    text_content: str | None = None
    next_node_id: int | None = None
    condition_expression: str | None = None
    variable_name: str | None = None
    variable_value: str | None = None

class ScenarioNodeCreate(ScenarioNodeBase):
    scenario_id: int
    options: list[ScenarioOptionCreate] = []

class ScenarioNodeUpdate(ScenarioNodeBase):
    options: list[ScenarioOptionCreate] | None = None

class ScenarioNodeResponse(ScenarioNodeBase):
    id: int
    scenario_id: int
    options: list[ScenarioOptionResponse] = []

    class Config:
        from_attributes = True


class ScenarioBase(BaseModel):
    name: str
    description: str | None = None
    category: str = "General"
    difficulty: str = "Medium"
    is_active: bool = True
    entry_node_id: int | None = None

class ScenarioCreate(ScenarioBase):
    pass

class ScenarioUpdate(ScenarioBase):
    name: str | None = None
    is_active: bool | None = None

class ScenarioResponse(ScenarioBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
