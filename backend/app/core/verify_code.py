from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.support_verify_code import SupportVerifyCode


def verify_support_code(*, db: Session, actor_account_id: str, code: str) -> bool:
    """
    Validates a 6-digit support verification code.

    Requirements:
    - Must belong to actor
    - Must not be used
    - Must not be expired
    - One-time use
    """

    row = (
        db.query(SupportVerifyCode)
        .filter(SupportVerifyCode.actor_account_id == actor_account_id)
        .filter(SupportVerifyCode.code == code)
        .filter(SupportVerifyCode.is_used == False)  # noqa: E712
        .filter(SupportVerifyCode.expires_at > datetime.now(timezone.utc))
        .one_or_none()
    )

    if not row:
        return False

    row.is_used = True
    db.add(row)
    db.commit()

    return True