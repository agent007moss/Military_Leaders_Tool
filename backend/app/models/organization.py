from __future__ import annotations

import uuid
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    base: Mapped[str] = mapped_column(String(200))
    command_team: Mapped[str] = mapped_column(String(500))
    tier_code: Mapped[str] = mapped_column(String(32), default="ORG_500_MONTH")

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)