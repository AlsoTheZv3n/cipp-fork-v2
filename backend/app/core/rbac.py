"""Role-Based Access Control dependencies for FastAPI.

Usage in routers:
    @router.get("/api/ListUsers", dependencies=[Depends(require_role("reader"))])
    @router.post("/api/EditUser", dependencies=[Depends(require_role("editor"))])
    @router.post("/api/ExecDangerousThing", dependencies=[Depends(require_role("admin"))])
"""
import re

from fastapi import Depends, HTTPException, Request

from app.core.session import get_current_user

ROLE_HIERARCHY = {
    "admin": 3,
    "editor": 2,
    "readonly": 1,
}


def get_authenticated_user(request: Request) -> dict:
    """Dependency that requires an authenticated user."""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def require_role(minimum_role: str):
    """Dependency factory: require at least this role level."""
    min_level = ROLE_HIERARCHY.get(minimum_role, 0)

    def check(user: dict = Depends(get_authenticated_user)):
        user_roles = user.get("roles", [])
        user_max_level = max(
            (ROLE_HIERARCHY.get(r, 0) for r in user_roles),
            default=0,
        )
        if user_max_level < min_level:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{minimum_role}' or higher required.",
            )
        return user

    return check


def require_permission(required: str):
    """Dependency factory: require a specific permission (supports wildcards)."""

    def check(user: dict = Depends(get_authenticated_user)):
        user_permissions = user.get("permissions", [])

        # Wildcard "*" grants everything
        if "*" in user_permissions:
            return user

        for perm in user_permissions:
            if perm == required:
                return user
            # Wildcard matching: "tenant.write.*" matches "tenant.write.user"
            if "*" in perm:
                pattern = perm.replace(".", r"\.").replace("*", ".*")
                if re.match(f"^{pattern}$", required):
                    return user

        raise HTTPException(
            status_code=403,
            detail=f"Permission '{required}' required.",
        )

    return check
