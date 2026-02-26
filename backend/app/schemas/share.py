from __future__ import annotations
from pydantic import BaseModel

class ShareToAccountIn(BaseModel):
    service_member_id: str
    target_account_id: str
    permission: str = "view"  # view|edit

class ShareToOrgIn(BaseModel):
    service_member_id: str
    target_org_id: str
    permission: str = "edit"  # per your rule: org gets edit on accept

class ShareDecisionIn(BaseModel):
    share_id: str
    decision: str  # accepted|denied
    reason: str | None = None