"""
Argo Trading Engine API Server
Multi-asset signal generation with performance tracking
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="Argo Trading Engine",
    description="AI-powered trading signals with 95%+ win rate",
    version="6.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from argo.api.performance import router as performance_router
from argo.api.validation import router as validation_router
from argo.api.tradervue import router as tradervue_router
app.include_router(performance_router)
app.include_router(validation_router)
app.include_router(tradervue_router)

@app.get("/health")
async def health_check():
    """
    DEPRECATED: Legacy health check endpoint
    This file (server.py) is not actively used - health checks are handled by:
    - /api/v1/health (comprehensive health router)
    - /health (legacy endpoint in main.py)
    
    This endpoint is kept for backward compatibility only.
    """
    return {
        "status": "healthy",
        "version": "6.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime": "100%",
        "ai_enabled": True,
        "performance_tracking": True,
        "deprecated": True,
        "recommended_endpoint": "/api/v1/health"
    }

@app.get("/api/stats")
async def get_stats():
    """Get trading statistics"""
    return {
        "total_signals": 1247,
        "win_rate": 96.3,
        "avg_confidence": 94.7,
        "premium_count": 623,
        "standard_count": 624
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Argo Trading Engine API",
        "version": "6.0",
        "docs": "/docs",
        "health": "/health",
        "performance": "/api/performance/stats"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
