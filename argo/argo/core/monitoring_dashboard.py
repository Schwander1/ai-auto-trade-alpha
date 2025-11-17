#!/usr/bin/env python3
"""
Monitoring Dashboard v5.0
Real-time monitoring and alerting for all system components
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MonitoringDashboard")


class MonitoringDashboard:
    """
    Centralized monitoring dashboard
    Tracks all system metrics, health, and performance
    """
    
    def __init__(self):
        self.metrics: Dict[str, Dict] = {}
        self.alerts: List[Dict] = []
        self.health_status: Dict[str, str] = {}
    
    def record_metric(self, name: str, value: float, tags: Optional[Dict] = None):
        """Record a metric"""
        if name not in self.metrics:
            self.metrics[name] = {
                'values': [],
                'tags': tags or {},
                'last_updated': None
            }
        
        self.metrics[name]['values'].append({
            'value': value,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Keep only last 1000 values
        if len(self.metrics[name]['values']) > 1000:
            self.metrics[name]['values'] = self.metrics[name]['values'][-1000:]
        
        self.metrics[name]['last_updated'] = datetime.utcnow().isoformat()
    
    def get_metric_summary(self, name: str, minutes: int = 60) -> Optional[Dict]:
        """Get metric summary for last N minutes"""
        if name not in self.metrics:
            return None
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        recent_values = [
            m['value'] for m in self.metrics[name]['values']
            if datetime.fromisoformat(m['timestamp']) > cutoff_time
        ]
        
        if not recent_values:
            return None
        
        return {
            'name': name,
            'count': len(recent_values),
            'min': min(recent_values),
            'max': max(recent_values),
            'avg': sum(recent_values) / len(recent_values),
            'latest': recent_values[-1],
            'tags': self.metrics[name]['tags']
        }
    
    def set_health_status(self, component: str, status: str, message: Optional[str] = None):
        """Set health status for a component"""
        self.health_status[component] = {
            'status': status,  # 'healthy', 'degraded', 'unhealthy'
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Generate alert if unhealthy
        if status == 'unhealthy':
            self.add_alert('error', f"{component} is unhealthy: {message}", component)
        elif status == 'degraded':
            self.add_alert('warning', f"{component} is degraded: {message}", component)
    
    def add_alert(self, level: str, message: str, component: Optional[str] = None):
        """Add an alert"""
        alert = {
            'level': level,  # 'info', 'warning', 'error', 'critical'
            'message': message,
            'component': component,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.alerts.append(alert)
        
        # Keep only last 1000 alerts
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
        
        # Log alert
        if level == 'critical' or level == 'error':
            logger.error(f"🚨 ALERT [{level}]: {message}")
        elif level == 'warning':
            logger.warning(f"⚠️  ALERT [{level}]: {message}")
        else:
            logger.info(f"ℹ️  ALERT [{level}]: {message}")
    
    def get_health_summary(self) -> Dict:
        """Get overall health summary"""
        total = len(self.health_status)
        healthy = sum(1 for h in self.health_status.values() if h['status'] == 'healthy')
        degraded = sum(1 for h in self.health_status.values() if h['status'] == 'degraded')
        unhealthy = sum(1 for h in self.health_status.values() if h['status'] == 'unhealthy')
        
        overall_status = 'healthy'
        if unhealthy > 0:
            overall_status = 'unhealthy'
        elif degraded > 0:
            overall_status = 'degraded'
        
        return {
            'overall_status': overall_status,
            'total_components': total,
            'healthy': healthy,
            'degraded': degraded,
            'unhealthy': unhealthy,
            'components': self.health_status
        }
    
    def get_recent_alerts(self, minutes: int = 60, level: Optional[str] = None) -> List[Dict]:
        """Get recent alerts"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        recent = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) > cutoff_time
        ]
        
        if level:
            recent = [a for a in recent if a['level'] == level]
        
        return recent
    
    def get_dashboard_data(self) -> Dict:
        """Get complete dashboard data"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'health': self.get_health_summary(),
            'metrics': {
                name: self.get_metric_summary(name, 60)
                for name in self.metrics.keys()
            },
            'recent_alerts': self.get_recent_alerts(60),
            'critical_alerts': self.get_recent_alerts(60, 'critical'),
            'error_alerts': self.get_recent_alerts(60, 'error')
        }
    
    def export_dashboard_json(self, filepath: Optional[Path] = None):
        """Export dashboard data to JSON file"""
        if filepath is None:
            filepath = Path(__file__).parent.parent.parent.parent / "logs" / "dashboard.json"
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.get_dashboard_data(), f, indent=2)
        
        logger.info(f"✅ Dashboard data exported to {filepath}")


# Global dashboard instance
_dashboard_instance = None

def get_monitoring_dashboard() -> MonitoringDashboard:
    """Get global monitoring dashboard instance"""
    global _dashboard_instance
    if _dashboard_instance is None:
        _dashboard_instance = MonitoringDashboard()
    return _dashboard_instance

