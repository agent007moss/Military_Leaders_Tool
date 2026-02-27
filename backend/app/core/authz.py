from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Role(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    ORG = "org"
    USER = "user"


class Action(str, Enum):
    # service member
    SM_READ = "sm:read"
    SM_WRITE_STP = "sm:write:stp"
    SM_SHARE = "sm:share"
    SM_UPLOAD = "sm:upload"
    SM_DELETE = "sm:delete"

    # org
    ORG_READ = "org:read"
    ORG_MANAGE_ROSTER = "org:manage_roster"
    ORG_DASHBOARD = "org:dashboard"

    # account support
    SUPPORT_ACCOUNT_ACTION = "support:account_action"  # requires 6-digit verify


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str


# ----------------------------
# Core policy helpers
# ----------------------------

def is_owner(role: str) -> bool:
    return role == Role.OWNER.value


def is_admin(role: str) -> bool:
    return role == Role.ADMIN.value


def is_org(role: str) -> bool:
    return role == Role.ORG.value


def is_user(role: str) -> bool:
    return role == Role.USER.value


# ----------------------------
# Decisions
# ----------------------------

def decide_action_for_role(role: str, action: Action) -> Decision:
    """
    Role-to-action policy (global). Resource-specific checks happen elsewhere.
    """
    if is_owner(role):
        return Decision(True, "owner allowed")

    if is_admin(role):
        # admin cannot do owner-only / global-only operations (audit/tier/global override not shown here)
        if action in (Action.SM_DELETE,):
            return Decision(False, "admin cannot delete service members")
        return Decision(True, "admin allowed")

    if is_org(role):
        if action in (Action.ORG_READ, Action.ORG_MANAGE_ROSTER, Action.ORG_DASHBOARD, Action.SM_READ):
            return Decision(True, "org allowed")
        return Decision(False, "org not allowed for this action")

    if is_user(role):
        if action in (Action.SM_READ, Action.SM_WRITE_STP, Action.SM_SHARE, Action.SM_UPLOAD, Action.ORG_READ):
            return Decision(True, "user allowed")
        return Decision(False, "user not allowed for this action")

    return Decision(False, "unknown role")


# ----------------------------
# Resource-specific decisions
# ----------------------------

def can_control_service_member(
    *,
    actor_account_id: str,
    service_member_creator_account_id: Optional[str],
    service_member_subject_account_id: Optional[str],
) -> bool:
    """
    A single controlling account: creator unless transferred to subject_account_id.
    """
    controller = service_member_subject_account_id or service_member_creator_account_id
    return controller == actor_account_id


def can_org_access_service_member(
    *,
    actor_org_id: Optional[str],
    service_member_org_id: Optional[str],
) -> bool:
    """
    Org actor can see org-owned members.
    """
    return bool(actor_org_id) and (actor_org_id == service_member_org_id)