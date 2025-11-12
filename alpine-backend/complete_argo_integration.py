
# ============================================
# ARGO TRADING SIGNALS INTEGRATION - COMPLETE
# ============================================

@app.get("/api/v1/argo/signals/crypto")
async def get_argo_crypto():
    """Fetch crypto signals from Argo"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{ARGO_API_URL}/api/v1/signals/crypto")
            return r.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/v1/argo/signals/stocks")
async def get_argo_stocks():
    """Fetch stock signals from Argo"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{ARGO_API_URL}/api/v1/signals/stocks")
            return r.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/v1/argo/tier/{tier}")
async def get_argo_tier(tier: str):
    """Fetch signals by tier from Argo"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{ARGO_API_URL}/api/v1/tier/{tier}")
            return r.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/v1/argo/stats")
async def get_argo_stats():
    """Fetch stats from Argo"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{ARGO_API_URL}/api/v1/stats")
            return r.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/v1/argo/signals/live/{symbol}")
async def get_argo_live_signal(symbol: str):
    """Fetch live signal for specific symbol from Argo"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{ARGO_API_URL}/api/v1/signals/live/{symbol}")
            return r.json()
    except Exception as e:
        return {"success": False, "error": str(e)}
