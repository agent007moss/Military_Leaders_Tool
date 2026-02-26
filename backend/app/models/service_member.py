from __future__ import annotations

import uuid
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class ServiceMember(Base):
    __tablename__ = "service_members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Ownership / control
    creator_account_id: Mapped[str] = mapped_column(String(36), ForeignKey("accounts.id"), index=True)
    subject_account_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("accounts.id"), nullable=True, index=True)

    # Branch-authoritative core
    branch: Mapped[str] = mapped_column(String(64), index=True)
    component: Mapped[str] = mapped_column(String(64), index=True)

    # STP source-of-truth blob (branch modules later refine)
    stp_data: Mapped[dict] = mapped_column(JSON, default=dict)

    # Claim/transfer
    claim_code: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)  # link/QR token