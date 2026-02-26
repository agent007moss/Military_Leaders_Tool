from __future__ import annotations
from pydantic import BaseModel

class UploadConfirmIn(BaseModel):
    service_member_id: str
    spot_key: str
    confirm_rotate: bool = False