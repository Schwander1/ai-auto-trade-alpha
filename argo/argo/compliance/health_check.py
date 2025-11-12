#!/usr/bin/env python3
"""
Health Check for Argo Capital
Runs hourly to verify system status
"""
import boto3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def health_check():
    """Check system health"""
    print(f"🏥 Health check at {datetime.now().isoformat()}")
    
    checks_passed = 0
    checks_total = 3
    
    # Check 1: .env file exists
    if os.path.exists('.env'):
        print("✅ .env file exists")
        checks_passed += 1
    else:
        print("❌ .env file missing")
    
    # Check 2: AWS credentials work
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION')
        )
        s3.list_buckets()
        print("✅ AWS S3 connection working")
        checks_passed += 1
    except Exception as e:
        print(f"❌ AWS S3 connection failed: {e}")
    
    # Check 3: Signals folder exists
    if os.path.exists('signals'):
        print("✅ Signals folder exists")
        checks_passed += 1
    else:
        print("❌ Signals folder missing")
    
    print(f"\nHealth: {checks_passed}/{checks_total} checks passed")
    return checks_passed == checks_total

if __name__ == '__main__':
    health_check()
