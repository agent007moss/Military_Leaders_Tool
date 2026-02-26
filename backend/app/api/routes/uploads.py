from __future__ import annotations

import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db, get_current_account
from app.core.config import settings
from app.core.audit import audit
from app.models.upload import UploadFile as UploadFileModel
from app.models.service_member import ServiceMember

router = APIRouter(prefix="/uploads", tags=["uploads"])

def _ensure_storage_dir() -> Path:
    p = Path(settings.upload_storage_dir)
    p.mkdir(parents=True, exist_ok=True)
    return p

@router.post("/spot")
def upload_to_spot(
    service_member_id: str = Form(...),
    spot_key: str = Form(...),
    confirm_rotate: bool = Form(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    acct=Depends(get_current_account),
):
    sm = db.get(ServiceMember, service_member_id)
    if not sm:
        raise HTTPException(status_code=404, detail="Service member not found")

    # Controller: subject if linked else creator
    controller = sm.subject_account_id or sm.creator_account_id
    if controller != acct.id and acct.role not in ("admin","owner","org"):
        raise HTTPException(status_code=403, detail="No permission")

    storage_dir = _ensure_storage_dir()
    existing = (
        db.execute(
            select(UploadFileModel)
            .where(UploadFileModel.service_member_id == service_member_id, UploadFileModel.spot_key == spot_key)
            .order_by(UploadFileModel.created_at.asc())
        )
        .scalars()
        .all()
    )

    if len(existing) >= settings.max_uploads_per_spot and not confirm_rotate:
        return {
            "requires_confirmation": True,
            "message": "Spot is full. Confirm rotate to delete oldest file and add new one.",
            "max_files": settings.max_uploads_per_spot,
            "current_files": [e.filename for e in existing],
        }

    if len(existing) >= settings.max_uploads_per_spot and confirm_rotate:
        oldest = existing[0]
        try:
            if os.path.exists(oldest.storage_path):
                os.remove(oldest.storage_path)
        except Exception:
            pass
        db.delete(oldest)
        audit(db, actor_type="account", actor_id=acct.id, action="upload.rotate.delete_oldest",
              target_type="upload_file", target_id=oldest.id, meta={"spot_key": spot_key, "filename": oldest.filename})
        db.commit()

    # Persist new file
    safe_name = f"{service_member_id}_{spot_key.replace('.','_')}_{file.filename}"
    dest = storage_dir / safe_name
    content = file.file.read()
    dest.write_bytes(content)

    rec = UploadFileModel(
        service_member_id=service_member_id,
        spot_key=spot_key,
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        storage_path=str(dest),
    )
    db.add(rec)
    audit(db, actor_type="account", actor_id=acct.id, action="upload.add",
          target_type="service_member", target_id=service_member_id, meta={"spot_key": spot_key, "filename": file.filename})
    db.commit()

    return {"uploaded": True, "file_id": rec.id, "filename": rec.filename}