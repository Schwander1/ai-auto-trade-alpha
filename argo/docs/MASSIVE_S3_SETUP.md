# Massive S3 Setup Guide

## Overview

Massive.com provides S3-compatible access to 10-20 years of historical market data. This guide explains how to configure it for comprehensive backtesting.

## Getting S3 Credentials

1. **Log in to Massive Dashboard**: https://dashboard.massive.com
2. **Navigate to API Keys**: Go to Settings → API Keys
3. **Create S3 Credentials**: Generate S3 Access Key and Secret Key
4. **Copy Credentials**: Save both keys securely

## Configuration Methods

### Method 1: Environment Variables (Recommended)

```bash
export MASSIVE_S3_ACCESS_KEY="your_access_key_here"
export MASSIVE_S3_SECRET_KEY="your_secret_key_here"
```

### Method 2: config.json

Edit `argo/config.json`:

```json
{
  "massive": {
    "s3_access_key": "your_access_key_here",
    "s3_secret_key": "your_secret_key_here",
    "s3_endpoint": "https://files.massive.com"
  }
}
```

## Verification

Test the connection:

```bash
python3 -c "
from argo.core.data_sources.massive_s3_client import MassiveS3Client
client = MassiveS3Client()
if client.s3_client:
    print('✅ Massive S3 configured successfully')
else:
    print('❌ Massive S3 not configured - add credentials')
"
```

## Usage

Once configured, the DataManager will automatically use Massive S3 for historical data:

- **Priority 1**: Parquet cache (if available)
- **Priority 2**: Massive S3 (10-20 year data)
- **Priority 3**: yfinance (fallback)

## Benefits

- **10-20 Years of Data**: Comprehensive historical coverage
- **Parallel Downloads**: 10x faster than sequential
- **Data Quality**: Validated OHLC relationships
- **Automatic Caching**: Parquet format for speed

## Troubleshooting

**Issue**: "Massive S3 credentials not configured"
- **Solution**: Add credentials via environment variables or config.json

**Issue**: "Connection timeout"
- **Solution**: Check internet connection and firewall settings

**Issue**: "Access denied"
- **Solution**: Verify credentials are correct and have S3 access enabled

