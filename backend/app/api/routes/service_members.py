from __future__ import annotations

import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_account
from app.core.audit import audit
from app.domain.branch_rules import validate_branch_component
from app.models.service_member import ServiceMember
from app.models.share import ServiceMemberShare
from app.schemas.service_member import ServiceMemberCreateIn, ServiceMemberOut, ClaimCodeOut

router = APIRouter(prefix="/service-members", tags=["service-members"])

@router.post("", response_model=ServiceMemberOut)
def create_service_member(
    data: ServiceMemberCreateIn,
    db: Session = Depends(get_db),
    acct=Depends(get_current_account),
):
    validate_branch_component(data.branch, data.component)

    sm = ServiceMember(
        creator_account_id=acct.id,
        subject_account_id=acct.id,  # self-created default
        branch=data.branch,
        component=data.component,
        stp_data=data.stp_data or {},
    )
    db.add(sm)
    db.commit()
    db.refresh(sm)

    audit(
        db,
        actor_type="account",
        actor_id=acct.id,
        action="service_member.create",
        target_type="service_member",
        target_id=sm.id,
        meta={"branch": sm.branch, "component": sm.component},
    )
    db.commit()
    return ServiceMemberOut(**sm.__dict__)

@router.get("", response_model=list[ServiceMemberOut])
def list_accessible_service_members(
    db: Session = Depends(get_db),
    acct=Depends(get_current_account),
):
    # Accessible if: subject, creator, or shared (accepted)
    owned = db.query(ServiceMember).filter(
        (ServiceMember.subject_account_id == acct.id) | (ServiceMember.creator_account_id == acct.id)
    )
    shared_ids = (
        db.query(ServiceMemberShare.service_member_id)
        .filter(ServiceMemberShare.target_account_id == acct.id, ServiceMemberShare.status == "accepted")
        .subquery()
    )
    shared = db.query(ServiceMember).filter(ServiceMember.id.in_(shared_ids))
    sms = owned.union(shared).all()
    return [ServiceMemberOut(**sm.__dict__) for sm in sms]

@router.post("/{service_member_id}/issue-claim", response_model=ClaimCodeOut)
def issue_claim_code(
    service_member_id: str,
    db: Session = Depends(get_db),
    acct=Depends(get_current_account),
):
    sm = db.get(ServiceMember, service_member_id)
    if not sm:
        raise HTTPException(status_code=404, detail="Not found")
    if sm.creator_account_id != acct.id:
        raise HTTPException(status_code=403, detail="Only creator can issue claim code")
    if sm.subject_account_id is not None:
        raise HTTPException(status_code=409, detail="Already linked to a subject account")

    sm.claim_code = secrets.token_urlsafe(24)
    db.add(sm)
    db.commit()

    audit(
        db,
        actor_type="account",
        actor_id=acct.id,
        action="service_member.claim_code.issue",
        target_type="service_member",
        target_id=sm.id,
        meta={},
    )
    db.commit()
    return ClaimCodeOut(service_member_id=sm.id, claim_code=sm.claim_code)

@router.post("/claim/{claim_code}", response_model=ServiceMemberOut)
def claim_service_member(
    claim_code: str,
    db: Session = Depends(get_db),
    acct=Depends(get_current_account),
):
    sm = db.query(ServiceMember).filter(ServiceMember.claim_code == claim_code).first()
    if not sm:
        raise HTTPException(status_code=404, detail="Invalid claim code")
    if sm.subject_account_id is not None:
        raise HTTPException(status_code=409, detail="Already claimed")

    sm.subject_account_id = acct.id
    sm.claim_code = None
    db.add(sm)
    db.commit()
    db.refresh(sm)

    audit(
        db,
        actor_type="account",
        actor_id=acct.id,
        action="service_member.claim",
        target_type="service_member",
        target_id=sm.id,
        meta={},
    )
    db.commit()
    return ServiceMemberOut(**sm.__dict__)