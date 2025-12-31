"""Role-Based Access Control (RBAC) Service

Provides centralized permission checking and role management
for the Operator Demo 2026 application.
"""

from app.models.user import Permission, UserRole


class RBACService:
    """Role-Based Access Control service"""

    def __init__(self):
        """Initialize RBAC with role-permission mappings"""
        self._role_permissions: dict[UserRole, set[Permission]] = {
            UserRole.ADMIN: {
                # User management
                Permission.USER_READ, Permission.USER_WRITE, Permission.USER_DELETE,
                # Session management
                Permission.SESSION_READ, Permission.SESSION_WRITE, Permission.SESSION_DELETE,
                # Campaign management
                Permission.CAMPAIGN_READ, Permission.CAMPAIGN_WRITE, Permission.CAMPAIGN_DELETE,
                # Provider management
                Permission.PROVIDER_READ, Permission.PROVIDER_WRITE, Permission.PROVIDER_DELETE,
                # Analytics
                Permission.ANALYTICS_READ, Permission.ANALYTICS_WRITE,
                # System administration
                Permission.SYSTEM_ADMIN, Permission.SYSTEM_MONITOR,
            },
            UserRole.SUPERVISOR: {
                # User management (limited)
                Permission.USER_READ,
                # Session management
                Permission.SESSION_READ, Permission.SESSION_WRITE,
                # Campaign management
                Permission.CAMPAIGN_READ, Permission.CAMPAIGN_WRITE,
                # Provider management (read-only)
                Permission.PROVIDER_READ,
                # Analytics
                Permission.ANALYTICS_READ, Permission.ANALYTICS_WRITE,
                # System monitoring
                Permission.SYSTEM_MONITOR,
            },
            UserRole.AGENT: {
                # Session management (own sessions only)
                Permission.SESSION_READ, Permission.SESSION_WRITE,
                # Campaign management (read-only)
                Permission.CAMPAIGN_READ,
                # Provider management (read-only)
                Permission.PROVIDER_READ,
                # Analytics (read-only, own data)
                Permission.ANALYTICS_READ,
            },
            UserRole.ANALYST: {
                # Session management (read-only)
                Permission.SESSION_READ,
                # Campaign management (read-only)
                Permission.CAMPAIGN_READ,
                # Provider management (read-only)
                Permission.PROVIDER_READ,
                # Analytics (full read access)
                Permission.ANALYTICS_READ, Permission.ANALYTICS_WRITE,
                # System monitoring
                Permission.SYSTEM_MONITOR,
            },
        }

    def get_role_permissions(self, role: UserRole) -> set[Permission]:
        """Get all permissions for a given role"""
        return self._role_permissions.get(role, set())

    def has_permission(self, role: UserRole, permission: Permission) -> bool:
        """Check if a role has a specific permission"""
        return permission in self.get_role_permissions(role)

    def has_any_permission(self, role: UserRole, permissions: list[Permission]) -> bool:
        """Check if a role has any of the specified permissions"""
        role_permissions = self.get_role_permissions(role)
        return any(perm in role_permissions for perm in permissions)

    def has_all_permissions(self, role: UserRole, permissions: list[Permission]) -> bool:
        """Check if a role has all of the specified permissions"""
        role_permissions = self.get_role_permissions(role)
        return all(perm in role_permissions for perm in permissions)

    def get_users_with_permission(self, permission: Permission) -> list[UserRole]:
        """Get all roles that have a specific permission"""
        return [
            role for role, perms in self._role_permissions.items()
            if permission in perms
        ]

    def can_access_resource(self, role: UserRole, resource: str, action: str) -> bool:
        """Check if a role can access a resource with a specific action
        
        Args:
            role: User role
            resource: Resource type (e.g., 'user', 'session', 'campaign')
            action: Action type (e.g., 'read', 'write', 'delete')
        """
        permission = f"{resource}:{action}"
        try:
            perm_enum = Permission(permission)
            return self.has_permission(role, perm_enum)
        except ValueError:
            # Permission doesn't exist, deny access
            return False

    def get_hierarchy_level(self, role: UserRole) -> int:
        """Get hierarchy level for role (higher number = more privileges)"""
        hierarchy = {
            UserRole.ANALYST: 1,
            UserRole.AGENT: 2,
            UserRole.SUPERVISOR: 3,
            UserRole.ADMIN: 4,
        }
        return hierarchy.get(role, 0)

    def can_manage_role(self, manager_role: UserRole, target_role: UserRole) -> bool:
        """Check if a role can manage another role"""
        manager_level = self.get_hierarchy_level(manager_role)
        target_level = self.get_hierarchy_level(target_role)
        return manager_level > target_level


# Global RBAC service instance
rbac_service = RBACService()


def get_rbac_service() -> RBACService:
    """Get the global RBAC service instance"""
    return rbac_service


# Convenience functions for common checks
def has_permission(role: UserRole, permission: Permission) -> bool:
    """Check if a role has a specific permission"""
    return rbac_service.has_permission(role, permission)


def can_access_resource(role: UserRole, resource: str, action: str) -> bool:
    """Check if a role can access a resource with a specific action"""
    return rbac_service.can_access_resource(role, resource, action)


def can_manage_role(manager_role: UserRole, target_role: UserRole) -> bool:
    """Check if a role can manage another role"""
    return rbac_service.can_manage_role(manager_role, target_role)
