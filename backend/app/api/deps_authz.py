from __future__ import annotations

from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_account
from app.core.authz import Action, decide_action_for_role, can_control_service_member, can_org_access_service_member

# NOTE: adjust import paths/names to match your models
from app.models.service_member import ServiceMember
from app.models.service_member_share import ServiceMemberShare  # if your project uses a different name, change it


def require_role_action(action: Action):
    def _dep(acct=Depends(get_current_account)):
        d = decide_action_for_role(acct.role, action)
        if not d.allowed:
            raise HTTPException(status_code=403, detail=d.reason)
        return acct
    return _dep


def require_service_member_access(action: Action, *, allow_shared_read: bool = True):
    """
    Enforces:
    - role allowed for action
    - resource-level rules:
      - controller account can read/write/share/upload
      - subject account can read/write if assigned to them
      - org can read if same org_id
      - shared accounts can read if share exists (read-only unless share grants edit)
    """
    def _dep(
        service_member_id: str,
        db: Session = Depends(get_db),
        acct=Depends(get_current_account),
    ):
        # global role policy
        d = decide_action_for_role(acct.role, action)
        if not d.allowed:
            raise HTTPException(status_code=403, detail=d.reason)

        sm = db.get(ServiceMember, service_member_id)
        if not sm:
            raise HTTPException(status_code=404, detail="Service member not found")

        # Controller access
        if can_control_service_member(
            actor_account_id=acct.id,
            service_member_creator_account_id=getattr(sm, "creator_account_id", None),
            service_member_subject_account_id=getattr(sm, "subject_account_id", None),
        ):
            return sm

        # Org scoped read
        if action == Action.SM_READ and can_org_access_service_member(
            actor_org_id=getattr(acct, "organization_id", None),
            service_member_org_id=getattr(sm, "organization_id", None),
        ):
            return sm

        # Shared access (read-only by default)
        if allow_shared_read and action == Action.SM_READ:
            share = (
                db.query(ServiceMemberShare)
                .filter(ServiceMemberShare.service_member_id == service_member_id)
                .filter(ServiceMemberShare.shared_with_account_id == acct.id)
                .one_or_none()
            )
            if share:
                return sm

        # Shared write only if explicit edit permission exists on share
        if action in (Action.SM_WRITE_STP, Action.SM_UPLOAD, Action.SM_SHARE):
            share = (
                db.query(ServiceMemberShare)
                .filter(ServiceMemberShare.service_member_id == service_member_id)
                .filter(ServiceMemberShare.shared_with_account_id == acct.id)
                .one_or_none()
            )
            if share and getattr(share, "can_edit", False):
                return sm

        raise HTTPException(status_code=403, detail="Not authorized for this service member")

    return _dep


# ----------------------------
# 6-digit verification gate (support actions)
# ----------------------------

def require_support_verification(
    *,
    code_header: str = "X-Account-Verify-Code",
):
    """
    Enforces:
    - role is owner/admin (global decision)
    - request contains a 6-digit code header
    - code is validated by a pluggable verifier function (implemented in app/core/verify_code.py)
    """
    def _dep(
        x_account_verify_code: str | None = Header(default=None, alias=code_header),
        db: Session = Depends(get_db),
        acct=Depends(get_current_account),
    ):
        d = decide_action_for_role(acct.role, Action.SUPPORT_ACCOUNT_ACTION)
        if not d.allowed:
            raise HTTPException(status_code=403, detail=d.reason)

        if not x_account_verify_code or not x_account_verify_code.isdigit() or len(x_account_verify_code) != 6:
            raise HTTPException(status_code=403, detail="Missing/invalid 6-digit verification code")

        from app.core.verify_code import verify_support_code  # local import to avoid circular deps

        ok = verify_support_code(db=db, actor_account_id=acct.id, code=x_account_verify_code)
        if not ok:
            raise HTTPException(status_code=403, detail="Verification failed")
        return acct

    return _dep