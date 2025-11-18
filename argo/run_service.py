#!/usr/bin/env python3
"""Wrapper script to run the FastAPI service with correct import paths"""
import sys
import os
from pathlib import Path

# Get the service directory
service_dir = Path(__file__).parent.absolute()

# Remove service directory from sys.path to avoid conflicts
if str(service_dir) in sys.path:
    sys.path.remove(str(service_dir))

# Add argo subdirectory to path
argo_dir = service_dir / "argo"
if argo_dir.exists() and str(argo_dir) not in sys.path:
    sys.path.insert(0, str(argo_dir))

# Change to service directory for relative imports
os.chdir(service_dir)

# Now import and run
if __name__ == "__main__":
    import uvicorn
    from main import app
    
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port, workers=1, timeout_keep_alive=30)

