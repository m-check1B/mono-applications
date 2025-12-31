"""API routers for Learn by Kraliki"""

from app.routers.courses import router as courses_router
from app.routers.progress import router as progress_router
from app.routers.assessment import router as assessment_router
from app.routers.corporate import router as corporate_router

__all__ = ["courses_router", "progress_router", "assessment_router", "corporate_router"]
