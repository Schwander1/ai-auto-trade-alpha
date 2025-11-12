#!/usr/bin/env python3
"""
Signal Logger with Compliance Integration
Logs every signal to S3 with SHA-256 verification
"""
import boto3
import os
import hashlib
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SignalLogger:
    """Log signals with compliance features"""
    
    def __init__(self):
        """Initialize S3 client"""
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION')
        )
        self.bucket = os.getenv('AWS_BUCKET_NAME')
    
    def generate_hash(self, signal_data):
        """Generate SHA-256 hash for signal"""
        hash_input = f"{signal_data['symbol']}|{signal_data['direction']}|{signal_data['timestamp']}|{signal_data['entry']}|{signal_data['confidence']}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def log_signal(self, signal_data):
        """Log signal with S3 backup"""
        try:
            # Add timestamp if not present
            if 'timestamp' not in signal_data:
                signal_data['timestamp'] = datetime.now().isoformat()
            
            # Generate SHA-256 hash
            signal_data['sha256'] = self.generate_hash(signal_data)
            
            # Create filename
            timestamp = datetime.now()
            filename = f"signal_{signal_data['symbol']}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            
            # Save locally
            with open(f'/tmp/{filename}', 'w') as f:
                json.dump(signal_data, f, indent=2)
            
            # Upload to S3
            s3_key = f"signals/{timestamp.year}/{timestamp.month:02d}/{timestamp.day:02d}/{filename}"
            self.s3.upload_file(f'/tmp/{filename}', self.bucket, s3_key)
            
            # Cleanup
            os.remove(f'/tmp/{filename}')
            
            print(f"✅ Signal logged: {signal_data['symbol']} {signal_data['direction']} (SHA-256: {signal_data['sha256'][:16]}...)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to log signal: {e}")
            return False

# Global instance
_logger = None

def get_logger():
    """Get or create global logger instance"""
    global _logger
    if _logger is None:
        _logger = SignalLogger()
    return _logger

def log_signal_with_compliance(signal_data):
    """
    Log signal with compliance features
    
    Args:
        signal_data (dict): Signal data with keys:
            - symbol: str
            - direction: str (LONG/SHORT)
            - entry: float
            - exit: float (optional)
            - stop: float (optional)
            - confidence: float
            - regime: str (optional)
    """
    logger = get_logger()
    return logger.log_signal(signal_data)

# Example usage
if __name__ == '__main__':
    # Test signal
    test_signal = {
        'symbol': 'SPY',
        'direction': 'LONG',
        'entry': 450.25,
        'exit': 452.50,
        'stop': 448.00,
        'confidence': 95.2,
        'regime': 'BULL'
    }
    log_signal_with_compliance(test_signal)
