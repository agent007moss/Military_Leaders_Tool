from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_account
from app.core.authz import Role
from app.core.support_code_service import generate_support_code
from app.models.account import Account

router = APIRouter(prefix="/support", tags=["support"])


@router.post("/generate-verify-code")
def generate_verify_code(
    db: Session = Depends(get_db),
    acct: Account = Depends(get_current_account),
):
    """
    Generates a 6-digit support verification code.
    Only owner/admin allowed.
    Expires in 5 minutes.
    """

    if acct.role not in (Role.OWNER.value, Role.ADMIN.value):
        raise HTTPException(status_code=403, detail="Not authorized")

    code = generate_support_code(db=db, actor_account_id=acct.id)

    return {
        "message": "Verification code generated",
        "expires_in_minutes": 5,
        "code": code,  # In production this would be sent via SMS/email instead
    }