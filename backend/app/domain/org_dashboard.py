from __future__ import annotations

from typing import List, Dict, Any
from collections import Counter

from app.domain.dashboard_cards import (
    build_fitness_card,
    build_training_card,
    build_awards_card,
    build_readiness_card,
)


# ==========================================================
# Utility
# ==========================================================

def _rag_counter(items: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Counts red / amber / green statuses from card list.
    """
    counter = Counter()
    for item in items:
        status = item.get("status", "gray")
        counter[status] += 1

    return {
        "green": counter.get("green", 0),
        "amber": counter.get("amber", 0),
        "red": counter.get("red", 0),
        "gray": counter.get("gray", 0),
    }


def _overall_status(counter: Dict[str, int]) -> str:
    """
    Determines overall RAG state.
    """
    if counter["red"] > 0:
        return "red"
    if counter["amber"] > 0:
        return "amber"
    return "green"


# ==========================================================
# Organization Dashboard Builder
# ==========================================================

def build_org_dashboard(service_members: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregates dashboard view for entire organization.
    Accepts list of STP data dictionaries.
    """

    fitness_cards = []
    training_cards = []
    awards_cards = []
    readiness_cards = []

    for stp in service_members:
        fitness_cards.append(build_fitness_card(stp))
        training_cards.append(build_training_card(stp))
        awards_cards.append(build_awards_card(stp))
        readiness_cards.append(build_readiness_card(stp))

    fitness_counter = _rag_counter(fitness_cards)
    training_counter = _rag_counter(training_cards)
    awards_counter = _rag_counter(awards_cards)
    readiness_counter = _rag_counter(readiness_cards)

    total_personnel = len(service_members)

    return {
        "total_personnel": total_personnel,

        "fitness_summary": {
            "counts": fitness_counter,
            "overall_status": _overall_status(fitness_counter),
        },

        "training_summary": {
            "counts": training_counter,
            "overall_status": _overall_status(training_counter),
        },

        "awards_summary": {
            "counts": awards_counter,
            "overall_status": _overall_status(awards_counter),
        },

        "readiness_summary": {
            "counts": readiness_counter,
            "overall_status": _overall_status(readiness_counter),
        },
    }