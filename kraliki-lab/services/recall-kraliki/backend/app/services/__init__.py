"""Services module for recall-kraliki"""

from .glm import GLMService, get_glm_service

try:
    from .storage import StorageService, get_storage_service
except Exception:  # Optional dependency for lightweight imports/tests
    StorageService = None
    get_storage_service = None

__all__ = ["GLMService", "get_glm_service"]

if StorageService is not None and get_storage_service is not None:
    __all__.extend(["StorageService", "get_storage_service"])
