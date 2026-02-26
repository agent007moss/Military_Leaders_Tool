from __future__ import annotations

from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(title="MilitaryTool API", version="0.1.0")
app.include_router(api_router)

@app.get("/health")
def health():
    return {"ok": True}