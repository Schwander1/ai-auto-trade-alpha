#!/usr/bin/env python3
"""
Unified Health Check System
Works locally and in production - detects environment automatically
"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Add paths - ensure argo is in path
argo_path = Path(__file__).parent.parent
if str(argo_path) not in sys.path:
    sys.path.insert(0, str(argo_path))
# Also add workspace root for shared packages
workspace_root = argo_path.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from argo.core.environment import detect_environment, get_environment_info
from argo.core.paper_trading_engine import PaperTradingEngine
from argo.core.signal_generation_service import SignalGenerationService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HealthCheckResult:
    """Health check result"""
    def __init__(self, name: str, status: bool, message: str = "", details: Dict = None):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()

class UnifiedHealthChecker:
    """Unified health checker for local and production"""
    
    def __init__(self, level: int = 2):
        """
        Initialize health checker
        
        Args:
            level: Health check level (1=basic, 2=standard, 3=comprehensive)
        """
        self.level = level
        self.environment = detect_environment()
        self.env_info = get_environment_info()
        self.results: List[HealthCheckResult] = []
        
    def check_environment(self) -> HealthCheckResult:
        """Check environment detection"""
        try:
            return HealthCheckResult(
                "Environment Detection",
                True,
                f"Environment: {self.environment}",
                self.env_info
            )
        except Exception as e:
            return HealthCheckResult(
                "Environment Detection",
                False,
                f"Failed: {e}"
            )
    
    def check_trading_engine(self) -> HealthCheckResult:
        """Check trading engine connectivity"""
        try:
            engine = PaperTradingEngine()
            if engine.alpaca_enabled:
                account = engine.get_account_details()
                return HealthCheckResult(
                    "Trading Engine",
                    True,
                    f"Connected to {engine.account_name}",
                    {
                        "account_name": engine.account_name,
                        "portfolio_value": account.get("portfolio_value", 0),
                        "buying_power": account.get("buying_power", 0),
                        "environment": engine.environment
                    }
                )
            else:
                return HealthCheckResult(
                    "Trading Engine",
                    False,
                    "Alpaca not connected (simulation mode)"
                )
        except Exception as e:
            return HealthCheckResult(
                "Trading Engine",
                False,
                f"Failed: {e}"
            )
    
    def check_signal_service(self) -> HealthCheckResult:
        """Check signal generation service"""
        try:
            service = SignalGenerationService()
            return HealthCheckResult(
                "Signal Generation Service",
                True,
                f"Service initialized (auto_execute: {service.auto_execute})",
                {
                    "environment": service.environment,
                    "auto_execute": service.auto_execute,
                    "data_sources": list(service.data_sources.keys())
                }
            )
        except Exception as e:
            return HealthCheckResult(
                "Signal Generation Service",
                False,
                f"Failed: {e}"
            )
    
    def check_data_sources(self) -> HealthCheckResult:
        """Check data sources availability"""
        try:
            service = SignalGenerationService()
            sources_status = {}
            for source_name, source in service.data_sources.items():
                sources_status[source_name] = source is not None
            
            all_available = all(sources_status.values())
            return HealthCheckResult(
                "Data Sources",
                all_available,
                f"{sum(sources_status.values())}/{len(sources_status)} sources available",
                sources_status
            )
        except Exception as e:
            return HealthCheckResult(
                "Data Sources",
                False,
                f"Failed: {e}"
            )
    
    def check_configuration(self) -> HealthCheckResult:
        """Check configuration file"""
        try:
            config_path = None
            if Path('/root/argo-production/config.json').exists():
                config_path = Path('/root/argo-production/config.json')
            elif Path('argo/config.json').exists():
                config_path = Path('argo/config.json')
            else:
                return HealthCheckResult(
                    "Configuration",
                    False,
                    "config.json not found"
                )
            
            with open(config_path) as f:
                config = json.load(f)
            
            required_sections = ['trading', 'strategy', 'alpaca']
            missing = [s for s in required_sections if s not in config]
            
            if missing:
                return HealthCheckResult(
                    "Configuration",
                    False,
                    f"Missing sections: {', '.join(missing)}"
                )
            
            return HealthCheckResult(
                "Configuration",
                True,
                f"Config file valid: {config_path}",
                {
                    "path": str(config_path),
                    "sections": list(config.keys())
                }
            )
        except Exception as e:
            return HealthCheckResult(
                "Configuration",
                False,
                f"Failed: {e}"
            )
    
    def check_database(self) -> HealthCheckResult:
        """Check database connectivity"""
        try:
            import sqlite3
            db_path = Path('argo/data/signals.db')
            if not db_path.exists():
                return HealthCheckResult(
                    "Database",
                    False,
                    "Database file not found (will be created on first use)"
                )
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM signals")
            count = cursor.fetchone()[0]
            conn.close()
            
            return HealthCheckResult(
                "Database",
                True,
                f"Database accessible ({count} signals)",
                {"signal_count": count}
            )
        except Exception as e:
            return HealthCheckResult(
                "Database",
                False,
                f"Failed: {e}"
            )
    
    def check_api_endpoints(self) -> HealthCheckResult:
        """Check API endpoints (if service is running)"""
        if self.level < 3:
            return HealthCheckResult(
                "API Endpoints",
                None,
                "Skipped (level 3 only)"
            )
        
        try:
            import requests
            base_url = "http://localhost:8000" if self.environment == "development" else "http://178.156.194.174:8000"
            
            endpoints = {
                "/health": 200,
                "/api/signals/latest": 200
            }
            
            results = {}
            for endpoint, expected_status in endpoints.items():
                try:
                    response = requests.get(f"{base_url}{endpoint}", timeout=5)
                    results[endpoint] = response.status_code == expected_status
                except:
                    results[endpoint] = False
            
            all_ok = all(results.values())
            return HealthCheckResult(
                "API Endpoints",
                all_ok,
                f"{sum(results.values())}/{len(results)} endpoints responding",
                results
            )
        except ImportError:
            return HealthCheckResult(
                "API Endpoints",
                None,
                "Skipped (requests library not available)"
            )
        except Exception as e:
            return HealthCheckResult(
                "API Endpoints",
                False,
                f"Failed: {e}"
            )
    
    def check_secrets_manager(self) -> HealthCheckResult:
        """Check AWS Secrets Manager (production only)"""
        if self.environment == "development":
            return HealthCheckResult(
                "AWS Secrets Manager",
                None,
                "Skipped (development environment)"
            )
        
        try:
            from utils.secrets_manager import get_secrets_manager
            secrets = get_secrets_manager()
            # Try to get a secret
            test_secret = secrets.get_secret("alpaca-api-key-production", service="argo", required=False)
            return HealthCheckResult(
                "AWS Secrets Manager",
                True,
                "Secrets Manager accessible"
            )
        except ImportError:
            return HealthCheckResult(
                "AWS Secrets Manager",
                None,
                "Skipped (secrets manager not available)"
            )
        except Exception as e:
            return HealthCheckResult(
                "AWS Secrets Manager",
                False,
                f"Failed: {e}"
            )
    
    def run_all_checks(self) -> Dict:
        """Run all health checks"""
        print(f'\n🏥 UNIFIED HEALTH CHECK (Level {self.level})')
        print(f'🌍 Environment: {self.environment.upper()}')
        print('='*70)
        
        # Level 1: Basic checks
        self.results.append(self.check_environment())
        self.results.append(self.check_configuration())
        
        # Level 2: Standard checks
        if self.level >= 2:
            self.results.append(self.check_trading_engine())
            self.results.append(self.check_signal_service())
            self.results.append(self.check_data_sources())
            self.results.append(self.check_database())
        
        # Level 3: Comprehensive checks
        if self.level >= 3:
            self.results.append(self.check_api_endpoints())
            self.results.append(self.check_secrets_manager())
        
        # Print results
        print('\n📊 Health Check Results:')
        print('-'*70)
        
        passed = 0
        failed = 0
        skipped = 0
        
        for result in self.results:
            if result.status is None:
                status_icon = "⏭️ "
                status_text = "SKIPPED"
                skipped += 1
            elif result.status:
                status_icon = "✅"
                status_text = "PASS"
                passed += 1
            else:
                status_icon = "❌"
                status_text = "FAIL"
                failed += 1
            
            print(f'{status_icon} {result.name}: {status_text}')
            if result.message:
                print(f'   {result.message}')
            if result.details and self.level >= 2:
                for key, value in result.details.items():
                    if isinstance(value, (int, float)):
                        if 'price' in key.lower() or 'value' in key.lower() or 'power' in key.lower():
                            print(f'   {key}: ${value:,.2f}')
                        else:
                            print(f'   {key}: {value:,}')
                    else:
                        print(f'   {key}: {value}')
        
        # Summary
        print('\n' + '='*70)
        print('📊 SUMMARY')
        print('='*70)
        print(f'✅ Passed: {passed}')
        print(f'❌ Failed: {failed}')
        print(f'⏭️  Skipped: {skipped}')
        print(f'📊 Total: {len(self.results)}')
        
        overall_status = failed == 0
        if overall_status:
            print('\n✅ ALL HEALTH CHECKS PASSED!')
        else:
            print('\n❌ SOME HEALTH CHECKS FAILED')
        
        return {
            "environment": self.environment,
            "level": self.level,
            "timestamp": datetime.utcnow().isoformat(),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "overall_status": overall_status,
            "results": [
                {
                    "name": r.name,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details,
                    "timestamp": r.timestamp
                }
                for r in self.results
            ]
        }

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Unified Health Check System')
    parser.add_argument('--level', type=int, default=2, choices=[1, 2, 3],
                       help='Health check level (1=basic, 2=standard, 3=comprehensive)')
    parser.add_argument('--json', action='store_true',
                       help='Output results as JSON')
    
    args = parser.parse_args()
    
    checker = UnifiedHealthChecker(level=args.level)
    results = checker.run_all_checks()
    
    if args.json:
        print(json.dumps(results, indent=2))
    
    sys.exit(0 if results["overall_status"] else 1)

if __name__ == '__main__':
    main()

