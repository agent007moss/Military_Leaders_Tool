from __future__ import annotations

import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class ServiceMemberShare(Base):
    __tablename__ = "service_member_shares"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    service_member_id: Mapped[str] = mapped_column(String(36), ForeignKey("service_members.id"), index=True)

    # One of these targets is set
    target_account_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("accounts.id"), nullable=True, index=True)
    target_org_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=True, index=True)

    permission: Mapped[str] = mapped_column(String(16), default="view")  # view|edit
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending|accepted|denied