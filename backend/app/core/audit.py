from __future__ import annotations

from typing import Any, Optional
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog

def audit(
    db: Session,
    *,
    actor_type: str,
    actor_id: str,
    action: str,
    target_type: str,
    target_id: str,
    meta: Optional[dict[str, Any]] = None,
) -> None:
    db.add(
        AuditLog(
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            meta=meta or {},
        )
    )