from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import (
    auth,
    service_members,
    organizations,
    shares,
    uploads,
    dashboard,
    org_dashboard,
    support,  # <-- added
)

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router)
api_router.include_router(service_members.router)
api_router.include_router(organizations.router)
api_router.include_router(shares.router)
api_router.include_router(uploads.router)
api_router.include_router(dashboard.router)
api_router.include_router(org_dashboard.router)
api_router.include_router(support.router)  # <-- added