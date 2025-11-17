#!/usr/bin/env python3
"""
Data Quality Monitor
Monitors data quality across all sources.
Detects anomalies, staleness, and inconsistencies.
"""
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Dict, List
from collections import deque

logger = logging.getLogger(__name__)

@dataclass
class DataQualityIssue:
    source: str
    issue_type: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    timestamp: datetime

class DataQualityMonitor:
    """
    Monitors data quality across all sources.
    Detects anomalies, staleness, and inconsistencies.
    """
    def __init__(self):
        self.quality_thresholds = {
            "max_staleness_seconds": 600,  # 10 minutes (increased for cached signals)
            "max_price_deviation_pct": 5.0,  # 5% from consensus
            "min_confidence": 60.0,
            "max_null_rate": 0.1  # 10% null values
        }
        self.quality_issues = deque(maxlen=1000)
        self.source_health = {}
        
    async def validate_signal(self, signal: Dict, market_data: Dict) -> tuple[bool, Optional[DataQualityIssue]]:
        """
        Validate signal quality across multiple dimensions.
        Returns (is_valid, issue) tuple.
        """
        # Check 1: Staleness
        if not self._check_freshness(signal):
            issue = DataQualityIssue(
                source=signal.get('source', 'unknown'),
                issue_type="staleness",
                severity="high",
                description=f"Signal older than {self.quality_thresholds['max_staleness_seconds']}s",
                timestamp=datetime.now()
            )
            self.quality_issues.append(issue)
            return False, issue
            
        # Check 2: Price consistency
        if not self._check_price_consistency(signal, market_data):
            issue = DataQualityIssue(
                source=signal.get('source', 'unknown'),
                issue_type="price_anomaly",
                severity="critical",
                description="Price deviates significantly from market consensus",
                timestamp=datetime.now()
            )
            self.quality_issues.append(issue)
            return False, issue
            
        # Check 3: Confidence threshold
        if signal.get('confidence', 0) < self.quality_thresholds["min_confidence"]:
            issue = DataQualityIssue(
                source=signal.get('source', 'unknown'),
                issue_type="low_confidence",
                severity="medium",
                description=f"Confidence {signal.get('confidence', 0)} below minimum",
                timestamp=datetime.now()
            )
            self.quality_issues.append(issue)
            return False, issue
            
        # Check 4: Completeness
        if not self._check_completeness(signal):
            issue = DataQualityIssue(
                source=signal.get('source', 'unknown'),
                issue_type="incomplete_data",
                severity="high",
                description="Required fields missing or null",
                timestamp=datetime.now()
            )
            self.quality_issues.append(issue)
            return False, issue
            
        return True, None
        
    def _check_freshness(self, signal: Dict) -> bool:
        """Check if signal is fresh enough"""
        timestamp_str = signal.get('timestamp')
        if not timestamp_str:
            # If no timestamp, check if it's a cached signal (allow it)
            # Cached signals might not have timestamps but are still valid
            return True  # Allow signals without timestamps (likely cached)
            
        try:
            if isinstance(timestamp_str, str):
                # Handle both with and without timezone
                if 'Z' in timestamp_str or '+' in timestamp_str or timestamp_str.endswith('+00:00'):
                    signal_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    signal_time = datetime.fromisoformat(timestamp_str)
            else:
                signal_time = timestamp_str
            
            # Handle timezone-aware and naive datetimes
            if signal_time.tzinfo is not None:
                now = datetime.now(signal_time.tzinfo)
                age_seconds = (now - signal_time).total_seconds()
            else:
                age_seconds = (datetime.now() - signal_time).total_seconds()
                
            return age_seconds <= self.quality_thresholds["max_staleness_seconds"]
        except Exception as e:
            logger.debug(f"Error checking freshness: {e}, allowing signal")
            # If we can't parse timestamp, allow the signal (fail open)
            return True
        
    def _check_price_consistency(self, signal: Dict, market_data: Dict) -> bool:
        """Check if signal price is consistent with market data"""
        signal_price = signal.get('price')
        market_price = market_data.get('price')
        
        if signal_price is None or market_price is None:
            return True  # Can't check, assume OK
            
        deviation_pct = abs(signal_price - market_price) / market_price * 100
        return deviation_pct <= self.quality_thresholds["max_price_deviation_pct"]
        
    def _check_completeness(self, signal: Dict) -> bool:
        """Check if signal has all required fields"""
        required_fields = ["direction", "confidence", "timestamp", "symbol"]
        return all(
            field in signal and signal[field] is not None 
            for field in required_fields
        )
        
    def get_source_health_status(self) -> Dict:
        """
        Get health status for all sources.
        Returns dict of source -> health score (0-100).
        """
        health_status = {}
        
        # Analyze recent issues per source
        recent_issues = [
            issue for issue in self.quality_issues 
            if (datetime.now() - issue.timestamp).total_seconds() < 3600
        ]  # Last hour
        
        # Get unique sources
        sources = set(issue.source for issue in recent_issues)
        sources.update(self.source_health.keys())
        
        for source in sources:
            source_issues = [i for i in recent_issues if i.source == source]
            
            # Calculate health score
            critical_count = sum(1 for i in source_issues if i.severity == "critical")
            high_count = sum(1 for i in source_issues if i.severity == "high")
            medium_count = sum(1 for i in source_issues if i.severity == "medium")
            
            # Health score: 100 - (weighted issue count)
            health_score = 100 - (critical_count * 20 + high_count * 10 + medium_count * 5)
            health_score = max(0, min(100, health_score))
            
            health_status[source] = {
                "health_score": health_score,
                "critical_issues": critical_count,
                "high_issues": high_count,
                "medium_issues": medium_count,
                "status": self._get_status_label(health_score)
            }
            
        return health_status
        
    def _get_status_label(self, health_score: float) -> str:
        """Convert health score to status label"""
        if health_score >= 90:
            return "excellent"
        elif health_score >= 75:
            return "good"
        elif health_score >= 50:
            return "fair"
        elif health_score >= 25:
            return "poor"
        else:
            return "critical"
            
    def get_quality_report(self) -> Dict:
        """Get comprehensive quality report"""
        recent_issues = [
            issue for issue in self.quality_issues
            if (datetime.now() - issue.timestamp).total_seconds() < 86400  # Last 24 hours
        ]
        
        return {
            "total_issues_24h": len(recent_issues),
            "issues_by_severity": {
                "critical": sum(1 for i in recent_issues if i.severity == "critical"),
                "high": sum(1 for i in recent_issues if i.severity == "high"),
                "medium": sum(1 for i in recent_issues if i.severity == "medium"),
                "low": sum(1 for i in recent_issues if i.severity == "low")
            },
            "issues_by_type": {},
            "source_health": self.get_source_health_status()
        }
