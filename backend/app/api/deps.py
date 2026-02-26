from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import SessionLocal
from app.models.account import Account

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_account(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> Account:
    try:
        payload = decode_token(token)
        account_id = payload["sub"]
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e

    acct = db.get(Account, account_id)
    if not acct or not acct.is_active:
        raise HTTPException(status_code=401, detail="Account inactive or missing")
    return acct

def require_role(*roles: str):
    def _inner(acct: Account = Depends(get_current_account)) -> Account:
        if acct.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return acct
    return _inner