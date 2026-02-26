from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.account import Account
from app.schemas.auth import RegisterIn, LoginIn, TokenOut

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenOut)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    existing = db.query(Account).filter(Account.email == data.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    acct = Account(email=data.email, password_hash=hash_password(data.password), role="user", tier_code="SINGLE_FREE")
    db.add(acct)
    db.commit()
    db.refresh(acct)
    return TokenOut(access_token=create_access_token(acct.id, acct.role))

@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    acct = db.query(Account).filter(Account.email == data.email).first()
    if not acct or not verify_password(data.password, acct.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenOut(access_token=create_access_token(acct.id, acct.role))