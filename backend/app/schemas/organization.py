from __future__ import annotations
from pydantic import BaseModel

class OrgCreateRequestIn(BaseModel):
    name: str
    base: str
    command_team: str
    unit_memorandum_note: str | None = None

class OrgOut(BaseModel):
    id: str
    name: str
    base: str
    command_team: str
    tier_code: str
    is_verified: bool
    is_approved: bool