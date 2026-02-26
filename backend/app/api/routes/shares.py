from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_account
from app.core.audit import audit
from app.models.service_member import ServiceMember
from app.models.share import ServiceMemberShare
from app.schemas.share import ShareToAccountIn, ShareToOrgIn, ShareDecisionIn

router = APIRouter(prefix="/shares", tags=["shares"])

def _controller_check(sm: ServiceMember, acct_id: str) -> None:
    # Controller is subject if linked; else creator
    controller = sm.subject_account_id or sm.creator_account_id
    if controller != acct_id:
        raise HTTPException(status_code=403, detail="Not record controller")

@router.post("/to-account")
def share_to_account(data: ShareToAccountIn, db: Session = Depends(get_db), acct=Depends(get_current_account)):
    sm = db.get(ServiceMember, data.service_member_id)
    if not sm:
        raise HTTPException(status_code=404, detail="Service member not found")
    _controller_check(sm, acct.id)

    share = ServiceMemberShare(
        service_member_id=sm.id,
        target_account_id=data.target_account_id,
        permission=data.permission,
        status="accepted",  # account sharing accepted immediately (no second-party acceptance specified)
    )
    db.add(share)
    audit(db, actor_type="account", actor_id=acct.id, action="share.account.grant",
          target_type="service_member", target_id=sm.id, meta={"permission": data.permission})
    db.commit()
    return {"share_id": share.id, "status": share.status}

@router.post("/to-org")
def share_to_org(data: ShareToOrgIn, db: Session = Depends(get_db), acct=Depends(get_current_account)):
    sm = db.get(ServiceMember, data.service_member_id)
    if not sm:
        raise HTTPException(status_code=404, detail="Service member not found")
    _controller_check(sm, acct.id)

    share = ServiceMemberShare(
        service_member_id=sm.id,
        target_org_id=data.target_org_id,
        permission="edit",  # locked: org gets edit rights on accept
        status="pending",
    )
    db.add(share)
    audit(db, actor_type="account", actor_id=acct.id, action="share.org.request",
          target_type="service_member", target_id=sm.id, meta={"target_org_id": data.target_org_id})
    db.commit()
    return {"share_id": share.id, "status": share.status}

@router.post("/org-decision")
def org_accept_deny(data: ShareDecisionIn, db: Session = Depends(get_db), acct=Depends(get_current_account)):
    # For MVP: allow org admins later; currently gate by role=org or admin/owner
    if acct.role not in ("org", "admin", "owner"):
        raise HTTPException(status_code=403, detail="Org decision not permitted for role")

    share = db.get(ServiceMemberShare, data.share_id)
    if not share or not share.target_org_id:
        raise HTTPException(status_code=404, detail="Org share not found")

    if share.status != "pending":
        raise HTTPException(status_code=409, detail="Already decided")

    if data.decision not in ("accepted", "denied"):
        raise HTTPException(status_code=400, detail="Invalid decision")

    share.status = data.decision
    db.add(share)

    audit(db, actor_type="account", actor_id=acct.id, action=f"share.org.{data.decision}",
          target_type="share", target_id=share.id, meta={"reason": data.reason})
    db.commit()
    return {"share_id": share.id, "status": share.status}