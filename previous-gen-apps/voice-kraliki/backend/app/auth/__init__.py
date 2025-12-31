"""Authentication module for operator demo"""

from .ed25519_auth import Ed25519Auth, get_auth_manager

__all__ = ["Ed25519Auth", "get_auth_manager"]
