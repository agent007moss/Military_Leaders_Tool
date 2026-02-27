from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.support_verify_code import SupportVerifyCode

# 5-minute expiration window (authoritative)
SUPPORT_CODE_EXPIRATION_MINUTES = 5


def generate_support_code(*, db: Session, actor_account_id: str) -> str:
    """
    Generates a secure 6-digit verification code for owner/admin support actions.

    Properties:
    - 6 digits, zero-padded
    - Actor-bound (actor_account_id)
    - Expires in SUPPORT_CODE_EXPIRATION_MINUTES
    - One-time use enforced by verify_support_code() when marked is_used=True
    """

    # Secure random 6-digit code (000000-999999)
    code = f"{secrets.randbelow(10**6):06d}"

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=SUPPORT_CODE_EXPIRATION_MINUTES)

    row = SupportVerifyCode(
        actor_account_id=actor_account_id,
        code=code,
        is_used=False,
        expires_at=expires_at,
    )

    db.add(row)
    db.commit()

    return code