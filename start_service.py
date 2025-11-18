#!/usr/bin/env python3
"""
Start Signal Generation Service
Run this to start the Argo signal generation service with all enhancements
"""
import asyncio
import sys
import os
from pathlib import Path

# Add argo to path
workspace_root = Path(__file__).parent
argo_path = workspace_root / "argo"
sys.path.insert(0, str(argo_path))

# Set PYTHONPATH
os.environ['PYTHONPATH'] = str(argo_path)

# Enable 24/7 mode for continuous signal generation
os.environ['ARGO_24_7_MODE'] = 'true'

from argo.core.signal_generation_service import SignalGenerationService

async def main():
    """Start the signal generation service"""
    print("🚀 Starting Argo Signal Generation Service")
    print("=" * 50)
    
    # Create service instance
    service = SignalGenerationService()
    print("✅ Service initialized")
    
    # Start background generation
    print("🚀 Starting background signal generation...")
    await service.start_background_generation(interval_seconds=5)
    print("✅ Service running!")
    print("")
    print("📊 Service Status:")
    print("  - Signal generation: Active (every 5 seconds)")
    print("  - Chinese models: GLM + DeepSeek enabled")
    print("  - All enhancements: Active")
    print("")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Stopping service...")
        service.stop()
        print("✅ Service stopped")
        sys.exit(0)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Service stopped")
        sys.exit(0)

