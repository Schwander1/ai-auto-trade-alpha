#!/usr/bin/env python3
"""
Refresh Materialized Views
Cron job script to refresh materialized views periodically
"""
import sys
from pathlib import Path

# Add argo to path
argo_path = Path(__file__).parent.parent
if str(argo_path) not in sys.path:
    sys.path.insert(0, str(argo_path))

from argo.core.database_optimizer import DatabaseOptimizer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Refreshing materialized views...")
    optimizer = DatabaseOptimizer()
    optimizer.refresh_materialized_views()
    logger.info("✅ Materialized views refreshed successfully")

