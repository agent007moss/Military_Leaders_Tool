from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_account
from app.models.service_member import ServiceMember
from app.domain.org_dashboard import build_org_dashboard


router = APIRouter(prefix="/org-dashboard", tags=["org-dashboard"])


@router.get("/{organization_id}/summary")
def get_org_dashboard_summary(
    organization_id: str,
    db: Session = Depends(get_db),
    acct=Depends(get_current_account),
):
    if acct.role not in ("owner", "admin", "org"):
        raise HTTPException(status_code=403, detail="Not authorized")

    members = (
        db.query(ServiceMember)
        .filter(ServiceMember.organization_id == organization_id)
        .all()
    )

    stp_list = [m.stp_data or {} for m in members]

    return build_org_dashboard(stp_list)