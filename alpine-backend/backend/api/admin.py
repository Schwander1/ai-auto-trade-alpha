"""Admin API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.signal import Signal

router = APIRouter()

@router.get("/stats")
async def get_platform_stats(db: Session = Depends(get_db)):
    """Get platform statistics - ONLY ONE FUNCTION"""
    total_signals = db.query(Signal).count()
    active_signals = db.query(Signal).filter(Signal.is_active == True).count()
    
    return {
        "total_users": 1,
        "total_signals": total_signals,
        "active_signals": active_signals,
        "platform": "Alpine Analytics"
    }
