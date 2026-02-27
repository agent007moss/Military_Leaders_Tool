from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


# ==========================================================
# Internal Utility Functions
# ==========================================================

def _days_remaining(date_str: str | None) -> int | None:
    """
    Safely calculate remaining days from ISO datetime string.
    Returns None if invalid or missing.
    """
    if not date_str:
        return None

    try:
        # Handle possible Z timezone
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        now = datetime.utcnow()
        return (dt - now).days
    except Exception:
        return None


def _status_color(days_remaining: int | None) -> str:
    """
    Standard RAG status logic.
    """
    if days_remaining is None:
        return "gray"
    if days_remaining < 30:
        return "red"
    if days_remaining <= 60:
        return "amber"
    return "green"


# ==========================================================
# Card Builders
# ==========================================================

def build_perstats_card(stp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Command visibility snapshot.
    """
    return {
        "rank": stp.get("rank"),
        "duty_status": stp.get("duty_status"),
        "unit": stp.get("current_unit"),
        "branch": stp.get("branch"),
        "component": stp.get("component"),
    }


def build_fitness_card(stp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Branch-aware fitness summary.
    """

    branch = stp.get("branch")

    test_label_map = {
        "Army": "ACFT",
        "Air Force": "PFA",
        "Navy": "PRT",
        "Marine Corps": "PFT/CFT",
        "Coast Guard": "PT",
        "Space Force": "PFA",
    }

    fitness = stp.get("fitness", {})
    expiration = fitness.get("expiration_date")
    last_test = fitness.get("last_test_date")

    days_remaining = _days_remaining(expiration)

    return {
        "test_type": test_label_map.get(branch, "Fitness"),
        "last_test_date": last_test,
        "expiration_date": expiration,
        "days_remaining": days_remaining,
        "status": _status_color(days_remaining),
    }


def build_training_card(stp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Training readiness aggregation.
    """

    training = stp.get("training", [])

    overdue = 0
    upcoming = 0
    completed = 0

    for item in training:
        if item.get("completed"):
            completed += 1

        due = item.get("due_date")
        if due:
            days = _days_remaining(due)
            if days is not None:
                if days < 0:
                    overdue += 1
                elif days <= 60:
                    upcoming += 1

    total = len(training)
    completion_rate = round((completed / total) * 100, 2) if total else 100

    status = "green"
    if overdue > 0:
        status = "red"
    elif upcoming > 0:
        status = "amber"

    return {
        "total_training_items": total,
        "completed": completed,
        "overdue": overdue,
        "due_within_60_days": upcoming,
        "completion_rate_percent": completion_rate,
        "status": status,
    }


def build_awards_card(stp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Awards tracking preview.
    """

    awards = stp.get("awards", [])
    pending = sum(1 for award in awards if award.get("status") == "pending")

    return {
        "total_awards": len(awards),
        "pending": pending,
        "status": "amber" if pending > 0 else "green",
    }


def build_readiness_card(stp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Branch-neutral readiness expiration tracking.
    """

    readiness = stp.get("readiness", {})

    expiration = readiness.get("readiness_expiration")
    days_remaining = _days_remaining(expiration)

    return {
        "readiness_expiration": expiration,
        "days_remaining": days_remaining,
        "status": _status_color(days_remaining),
    }