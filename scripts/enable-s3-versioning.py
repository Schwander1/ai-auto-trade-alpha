#!/usr/bin/env python3
"""
Enable S3 Versioning and Lifecycle Policies for Backup Bucket
COMPLIANCE: 7-year retention requirement with cost optimization
"""
import boto3
import os
import json
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("S3Versioning")

def enable_versioning(bucket_name: str):
    """Enable versioning on S3 bucket"""
    s3 = boto3.client('s3')
    
    try:
        s3.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={
                'Status': 'Enabled'
            }
        )
        logger.info(f"✅ Versioning enabled for bucket: {bucket_name}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to enable versioning: {e}")
        return False

def configure_lifecycle_policy(bucket_name: str):
    """Configure lifecycle policy for 7-year retention"""
    s3 = boto3.client('s3')
    
    # Lifecycle policy for 7-year retention
    lifecycle_policy = {
        'Rules': [
            {
                'Id': '7YearRetentionPolicy',
                'Status': 'Enabled',
                'Filter': {'Prefix': 'signals/'},
                'Transitions': [
                    {
                        'Days': 90,
                        'StorageClass': 'STANDARD_IA'  # Infrequent Access after 90 days
                    },
                    {
                        'Days': 365,
                        'StorageClass': 'GLACIER'  # Glacier after 1 year
                    }
                ],
                'Expiration': {
                    'Days': 2555  # 7 years (365 * 7)
                },
                'NoncurrentVersionTransitions': [
                    {
                        'NoncurrentDays': 30,
                        'StorageClass': 'GLACIER'
                    }
                ],
                'NoncurrentVersionExpiration': {
                    'NoncurrentDays': 90  # Delete old versions after 90 days
                }
            }
        ]
    }
    
    try:
        s3.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration=lifecycle_policy
        )
        logger.info(f"✅ Lifecycle policy configured for bucket: {bucket_name}")
        logger.info("   - Current versions: Standard → Standard-IA (90d) → Glacier (365d) → Expire (2555d)")
        logger.info("   - Previous versions: Glacier (30d) → Expire (90d)")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to configure lifecycle policy: {e}")
        return False

def verify_versioning(bucket_name: str) -> bool:
    """Verify versioning is enabled"""
    s3 = boto3.client('s3')
    
    try:
        response = s3.get_bucket_versioning(Bucket=bucket_name)
        status = response.get('Status', 'NotEnabled')
        
        if status == 'Enabled':
            logger.info(f"✅ Versioning verified: {status}")
            return True
        else:
            logger.warning(f"⚠️  Versioning status: {status}")
            return False
    except Exception as e:
        logger.error(f"❌ Failed to verify versioning: {e}")
        return False

def verify_lifecycle_policy(bucket_name: str) -> bool:
    """Verify lifecycle policy is active"""
    s3 = boto3.client('s3')
    
    try:
        response = s3.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        rules = response.get('Rules', [])
        
        if rules:
            logger.info(f"✅ Lifecycle policy verified: {len(rules)} rule(s) active")
            for rule in rules:
                logger.info(f"   - Rule: {rule.get('Id')}, Status: {rule.get('Status')}")
            return True
        else:
            logger.warning("⚠️  No lifecycle rules found")
            return False
    except Exception as e:
        logger.error(f"❌ Failed to verify lifecycle policy: {e}")
        return False

def print_cost_estimate(bucket_name: str):
    """Print estimated storage costs"""
    logger.info("\n📊 Estimated Storage Costs (7-year retention):")
    logger.info("   - Standard Storage (0-90 days): ~$0.023/GB/month")
    logger.info("   - Standard-IA (90-365 days): ~$0.0125/GB/month")
    logger.info("   - Glacier (1-7 years): ~$0.004/GB/month")
    logger.info("   - Previous versions (30-90 days): Glacier pricing")
    logger.info("\n💡 Cost optimization:")
    logger.info("   - Old versions expire after 90 days")
    logger.info("   - Current versions transition to cheaper storage classes")
    logger.info("   - 7-year retention maintained for compliance")

def main():
    """Main execution"""
    bucket_name = os.getenv('BACKUP_BUCKET_NAME') or os.getenv('AWS_BUCKET_NAME')
    
    if not bucket_name:
        logger.error("❌ BACKUP_BUCKET_NAME or AWS_BUCKET_NAME environment variable required")
        return False
    
    logger.info(f"🔧 Configuring S3 versioning and lifecycle for: {bucket_name}")
    logger.info("=" * 60)
    
    # Enable versioning
    if not enable_versioning(bucket_name):
        return False
    
    # Configure lifecycle policy
    if not configure_lifecycle_policy(bucket_name):
        return False
    
    # Verify configuration
    logger.info("\n🔍 Verifying configuration...")
    versioning_ok = verify_versioning(bucket_name)
    lifecycle_ok = verify_lifecycle_policy(bucket_name)
    
    # Print cost estimate
    print_cost_estimate(bucket_name)
    
    if versioning_ok and lifecycle_ok:
        logger.info("\n✅ S3 versioning and lifecycle configuration complete!")
        return True
    else:
        logger.warning("\n⚠️  Configuration completed with warnings")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)

