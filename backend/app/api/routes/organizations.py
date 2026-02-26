from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_account, require_role
from app.core.audit import audit
from app.models.organization import Organization
from app.schemas.organization import OrgCreateRequestIn, OrgOut

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.post("/request", response_model=OrgOut)
def request_org_creation(data: OrgCreateRequestIn, db: Session = Depends(get_db), acct=Depends(get_current_account)):
    # Customer service flow placeholder: user can submit request; approval is owner/admin.
    existing = db.query(Organization).filter(Organization.name == data.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Organization already exists")
    org = Organization(name=data.name, base=data.base, command_team=data.command_team, is_verified=False, is_approved=False)
    db.add(org)
    db.commit()
    db.refresh(org)
    audit(db, actor_type="account", actor_id=acct.id, action="org.request.create",
          target_type="organization", target_id=org.id, meta={"unit_memorandum_note": data.unit_memorandum_note})
    db.commit()
    return OrgOut(**org.__dict__)

@router.post("/{org_id}/verify", response_model=OrgOut)
def verify_org(org_id: str, db: Session = Depends(get_db), acct=Depends(require_role("admin","owner"))):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Not found")
    org.is_verified = True
    db.add(org)
    audit(db, actor_type="account", actor_id=acct.id, action="org.verify",
          target_type="organization", target_id=org.id, meta={})
    db.commit()
    db.refresh(org)
    return OrgOut(**org.__dict__)

@router.post("/{org_id}/approve", response_model=OrgOut)
def approve_org(org_id: str, db: Session = Depends(get_db), acct=Depends(require_role("admin","owner"))):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Not found")
    if not org.is_verified:
        raise HTTPException(status_code=409, detail="Must be verified first")
    org.is_approved = True
    db.add(org)
    audit(db, actor_type="account", actor_id=acct.id, action="org.approve",
          target_type="organization", target_id=org.id, meta={})
    db.commit()
    db.refresh(org)
    return OrgOut(**org.__dict__)