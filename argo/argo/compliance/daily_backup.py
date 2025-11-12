#!/usr/bin/env python3
"""
Daily Backup Script for Argo Capital
Backs up yesterday's signals to S3
"""
import boto3
import os
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def backup_signals():
    """Export yesterday's signals to CSV and upload to S3"""
    print(f"🔄 Starting daily backup for {datetime.now().strftime('%Y-%m-%d')}")
    
    try:
        # Create S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION')
        )
        
        bucket = os.getenv('AWS_BUCKET_NAME')
        
        # Get yesterday's date
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime('%Y%m%d')
        
        # Create test CSV (replace with actual database query)
        csv_filename = f'signals_{date_str}.csv'
        
        with open(csv_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'symbol', 'direction', 'confidence', 'sha256'])
            # TODO: Query actual signals from database
            writer.writerow([yesterday.isoformat(), 'SPY', 'LONG', '95.2', 'abc123...'])
        
        # Upload to S3
        s3_key = f'signals/{yesterday.year}/{yesterday.month:02d}/{csv_filename}'
        s3.upload_file(csv_filename, bucket, s3_key)
        
        print(f"✅ Uploaded to s3://{bucket}/{s3_key}")
        
        # Clean up local file
        os.remove(csv_filename)
        
        print(f"✅ Daily backup completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

if __name__ == '__main__':
    backup_signals()
