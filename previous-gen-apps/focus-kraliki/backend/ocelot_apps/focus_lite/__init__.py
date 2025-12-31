"""Focus by Kraliki integration module for Ocelot Platform consumers.

This package exposes a `PlanningModule` facade that wraps the existing FastAPI
application and domain logic so other services (Voice by Kraliki, CLI-Toris, or the
Ocelot Platform) can import and use Focus by Kraliki without going through HTTP.
"""

from .module import PlanningModule, PlanningModuleConfig, PlanningModuleError

__all__ = ["PlanningModule", "PlanningModuleConfig", "PlanningModuleError"]
