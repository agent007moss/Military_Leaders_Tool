from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_account
from app.models.service_member import ServiceMember
from app.domain.dashboard_cards import (
    build_perstats_card,
    build_fitness_card,
    build_training_card,
    build_awards_card,
    build_readiness_card,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{service_member_id}/cards")
def get_dashboard_cards(
    service_member_id: str,
    db: Session = Depends(get_db),
    acct=Depends(get_current_account),
):
    sm = db.get(ServiceMember, service_member_id)
    if not sm:
        raise HTTPException(status_code=404, detail="Service member not found")

    controller = sm.subject_account_id or sm.creator_account_id
    if controller != acct.id and acct.role not in ("admin", "owner", "org"):
        raise HTTPException(status_code=403, detail="Not authorized")

    stp = sm.stp_data or {}

    return {
        "perstats": build_perstats_card(stp),
        "fitness": build_fitness_card(stp),
        "training": build_training_card(stp),
        "awards": build_awards_card(stp),
        "readiness": build_readiness_card(stp),
    }
