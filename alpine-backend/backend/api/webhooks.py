"""Zapier webhook endpoints"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.signal import Signal
from datetime import datetime
import json
import subprocess

router = APIRouter()

@router.post("/zapier/pre-order")
async def pre_order(request: Request):
    data = await request.json()
    with open("/root/alpine-analytics/logs/zapier.log", "a") as f:
        f.write(f"{datetime.utcnow().isoformat()} - {json.dumps(data)}\n")
    return {"status": "received"}

@router.get("/zapier/daily-stats")
async def daily_stats(db: Session = Depends(get_db)):
    signals = db.query(Signal).filter(Signal.is_active == True).count()
    return {"date": datetime.utcnow().date().isoformat(), "signals": signals}

@router.post("/zapier/end-presale")
async def end_presale():
    subprocess.run(["sed", "-i", "s/50% Off Annual Plans/Regular Pricing/g", "/var/www/alpine-frontend/index.html"])
    subprocess.run(["systemctl", "reload", "nginx"])
    return {"status": "presale_ended"}
