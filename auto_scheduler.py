#!/usr/bin/env python3
import os, time, subprocess, sys
import alpaca_trade_api as tradeapi
from datetime import datetime, timezone
import logging

ROOT = "/Users/dylanneuenschwander/projects/ARGO-Master-Unified"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_bg(cmd, logfile):
    full_cmd = f"cd {ROOT} && source argo_env/bin/activate && {cmd} > {logfile} 2>&1 &"
    return subprocess.Popen(full_cmd, shell=True, executable='/bin/bash')

def get_clock_with_retry(api, max_retries=3, base_retry_delay=5):
    """Get market clock with retry logic and exponential backoff for connection errors."""
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return api.get_clock()
        except (ConnectionError, TimeoutError, Exception) as e:
            last_exception = e
            retry_delay = base_retry_delay * (attempt + 1)
            
            if attempt < max_retries - 1:
                logger.warning(f"⚠️ Clock API error (attempt {attempt + 1}/{max_retries}): {type(e).__name__}")
                logger.info(f"⏳ Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                logger.error(f"❌ Failed to get clock after {max_retries} attempts")
                # Re-raise the last exception to be caught by main loop
                raise last_exception
    
    return None

def main():
    os.chdir(ROOT)
    
    # Load environment
    subprocess.run("./export_env.sh", shell=True)
    
    # Verify API credentials are loaded
    api_key = os.getenv("APCA_API_KEY_ID")
    api_secret = os.getenv("APCA_API_SECRET_KEY")
    base_url = os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")
    
    if not api_key or not api_secret:
        logger.error("❌ APCA_API_KEY_ID or APCA_API_SECRET_KEY not set!")
        sys.exit(1)
    
    logger.info(f"Using Alpaca API: {base_url}")
    
    api = tradeapi.REST(
        key_id=api_key,
        secret_key=api_secret,
        base_url=base_url
    )
    
    running_processes = []
    
    try:
        while True:
            try:
                clock = get_clock_with_retry(api)
                now = datetime.now(timezone.utc)
            except (ConnectionError, TimeoutError) as e:
                logger.warning(f"⚠️ Alpaca API unreachable, will retry in 60s: {type(e).__name__}")
                time.sleep(60)
                continue
            except Exception as e:
                logger.error(f"❌ Unexpected error reaching Alpaca API, retrying in 60s: {e}")
                time.sleep(60)
                continue
            
            if clock.is_open and not running_processes:
                print(f"🚀 Market OPEN at {now} - Starting all systems...")
                
                # Start data ingestion
                running_processes.append(run_bg("python3 20_code/consolidated/live_data_ingestion.py", "logs/ingestion.log"))
                
                # Start signal generation
                running_processes.append(run_bg("python3 20_code/consolidated/model_training.py", "logs/signals.log"))
                
                # Start execution engine  
                running_processes.append(run_bg("python3 20_code/consolidated/full_system_deployment.py", "logs/execution.log"))
                
                # Start dashboard
                running_processes.append(run_bg("streamlit run 50_monitoring/dashboard.py --server.port 8501", "logs/dashboard.log"))
                
                print("✅ All trading systems launched")
                
            elif not clock.is_open and running_processes:
                print(f"🛑 Market CLOSED at {now} - Systems continue in background")
                # Let processes continue running for after-hours data
                
            # Health check every 30 seconds
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("🛑 Scheduler stopped by user")
        
if __name__ == "__main__":
    main()
