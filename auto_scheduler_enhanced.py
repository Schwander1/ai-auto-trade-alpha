#!/usr/bin/env python3
import time
import schedule
import subprocess
import alpaca_trade_api as tradeapi
import os
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

# Configure logging
logging.basicConfig(
    filename='logs/scheduler_enhanced.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_robust_api_client():
    """Create API client with retry logic and timeout handling"""
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    try:
        api = tradeapi.REST(
            os.getenv('APCA_API_KEY_ID'),
            os.getenv('APCA_API_SECRET_KEY'),
            os.getenv('APCA_API_BASE_URL'),
            api_version='v2'
        )
        api._session = session
        return api
    except Exception as e:
        logging.error(f"API client creation failed: {e}")
        return None

def safe_api_call(func, *args, **kwargs):
    """Execute API calls with error handling and retries"""
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            result = func(*args, **kwargs)
            logging.info(f"API call successful on attempt {attempt + 1}")
            return result
        except requests.exceptions.ConnectionError as e:
            logging.warning(f"Connection error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
            else:
                logging.error(f"API call failed after {max_retries} attempts")
                return None
        except Exception as e:
            logging.error(f"Unexpected error in API call: {e}")
            return None

def market_open_check():
    """Check if market is open with robust error handling"""
    try:
        api = create_robust_api_client()
        if api:
            clock = safe_api_call(api.get_clock)
            if clock:
                is_open = clock.is_open
                logging.info(f"Market check: {'OPEN' if is_open else 'CLOSED'}")
                
                if is_open:
                    # Market is open - trigger data collection
                    account = safe_api_call(api.get_account)
                    if account:
                        logging.info(f"Portfolio: ${account.portfolio_value}")
                    
                return is_open
        
        logging.warning("Market check failed - assuming closed for safety")
        return False
        
    except Exception as e:
        logging.error(f"Market check error: {e}")
        return False

def start_data_collection():
    """Start live data collection"""
    try:
        logging.info("Starting data collection...")
        # Your data collection logic here
        print(f"Data collection triggered at {datetime.now()}")
    except Exception as e:
        logging.error(f"Data collection error: {e}")

def generate_signals():
    """Generate trading signals"""
    try:
        logging.info("Generating trading signals...")
        # Your signal generation logic here
        print(f"Signal generation triggered at {datetime.now()}")
    except Exception as e:
        logging.error(f"Signal generation error: {e}")

# Schedule market-aware operations with error handling
schedule.every().minute.do(market_open_check)
schedule.every(5).minutes.do(start_data_collection)
schedule.every(10).minutes.do(generate_signals)

print("🚀 Enhanced Argo Auto-Scheduler Started")
print("🛡️ Robust error handling and retry logic active")
logging.info("Enhanced scheduler started with robust error handling")

while True:
    try:
        schedule.run_pending()
        time.sleep(30)
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user")
        break
    except Exception as e:
        logging.error(f"Scheduler error: {e}")
        time.sleep(60)  # Wait longer on unexpected errors
