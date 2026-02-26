from __future__ import annotations
from pydantic import BaseModel

class ServiceMemberCreateIn(BaseModel):
    branch: str
    component: str
    stp_data: dict = {}

class ServiceMemberOut(BaseModel):
    id: str
    creator_account_id: str
    subject_account_id: str | None
    branch: str
    component: str
    stp_data: dict

class ClaimCodeOut(BaseModel):
    service_member_id: str
    claim_code: str