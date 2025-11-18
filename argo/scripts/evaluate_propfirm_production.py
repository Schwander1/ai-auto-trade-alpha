#!/usr/bin/env python3
"""
Prop Firm Production Setup Evaluation
Comprehensive evaluation of prop firm setup on production vs requirements
Considers profitability, risk limits, compliance, and configuration
"""
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import subprocess

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Requirements from documentation
REQUIRED_PROP_FIRM_CONFIG = {
    "max_drawdown_pct": 2.0,  # Conservative: 2.0% vs prop firm limit 2.5%
    "daily_loss_limit_pct": 4.5,  # Conservative: 4.5% vs prop firm limit 5.0%
    "max_position_size_pct": 3.0,  # Conservative position sizing
    "min_confidence": 82.0,  # High quality signals only
    "max_positions": 3,  # Diversification
    "max_stop_loss_pct": 1.5  # Tight risk control
}

REQUIRED_MONITORING = {
    "enabled": True,
    "check_interval_seconds": 5,
    "alert_on_warning": True,
    "auto_shutdown": True
}

PROFITABILITY_TARGETS = {
    "win_rate_percent": 45.0,  # Minimum acceptable
    "profit_factor": 1.5,  # Minimum acceptable
    "return_percent": 10.0,  # Target for profitability
    "max_drawdown_pct": 2.0,  # Must stay under
    "daily_loss_limit_pct": 4.5  # Must stay under
}


class PropFirmProductionEvaluator:
    """Evaluate prop firm production setup"""
    
    def __init__(self, production_server: str = "178.156.194.174", 
                 production_user: str = "root",
                 config_path: Optional[str] = None,
                 use_ssh: bool = True):
        self.production_server = production_server
        self.production_user = production_user
        self.config_path = config_path
        self.use_ssh = use_ssh
        self.config = None
        self.issues = []
        self.warnings = []
        self.passed_checks = []
        
    def load_production_config(self) -> bool:
        """Load production config via SSH or local path"""
        if self.config_path and Path(self.config_path).exists():
            # Load from local path
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"✅ Loaded config from: {self.config_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to load local config: {e}")
                return False
        
        if not self.use_ssh:
            logger.error("Cannot load production config: SSH disabled and no local path provided")
            return False
        
        # Try to load from production server
        prod_paths = [
            "/root/argo-production-prop-firm/config.json",
            "/root/argo-production-green/config.json",
            "/root/argo-production/config.json"
        ]
        
        for path in prod_paths:
            try:
                cmd = f"ssh {self.production_user}@{self.production_server} 'cat {path}'"
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    self.config = json.loads(result.stdout)
                    logger.info(f"✅ Loaded config from production: {path}")
                    self.config_path = path
                    return True
            except subprocess.TimeoutExpired:
                logger.warning(f"Timeout loading config from {path}")
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from {path}")
            except Exception as e:
                logger.warning(f"Error loading {path}: {e}")
        
        logger.error("Failed to load production config from any location")
        return False
    
    def check_prop_firm_enabled(self) -> bool:
        """Check if prop firm mode is enabled"""
        if not self.config:
            self.issues.append("Config not loaded - cannot check prop firm status")
            return False
        
        prop_firm = self.config.get('prop_firm', {})
        enabled = prop_firm.get('enabled', False)
        
        if enabled:
            self.passed_checks.append("Prop firm mode is enabled")
            return True
        else:
            self.issues.append("Prop firm mode is NOT enabled")
            return False
    
    def check_risk_limits(self) -> bool:
        """Check risk limits against requirements"""
        if not self.config:
            return False
        
        prop_firm = self.config.get('prop_firm', {})
        risk_limits = prop_firm.get('risk_limits', {})
        
        all_passed = True
        
        # Check each required limit
        for key, required_value in REQUIRED_PROP_FIRM_CONFIG.items():
            actual_value = risk_limits.get(key)
            
            if actual_value is None:
                self.issues.append(f"Missing risk limit: {key} (required: {required_value})")
                all_passed = False
            elif key in ['max_drawdown_pct', 'daily_loss_limit_pct', 'max_position_size_pct', 'max_stop_loss_pct']:
                # These should be <= required (conservative)
                if actual_value > required_value:
                    self.issues.append(
                        f"{key} too high: {actual_value} (required: <= {required_value})"
                    )
                    all_passed = False
                elif actual_value < required_value * 0.8:
                    self.warnings.append(
                        f"{key} very conservative: {actual_value} (recommended: {required_value})"
                    )
                else:
                    self.passed_checks.append(f"{key}: {actual_value} (required: {required_value})")
            elif key == 'min_confidence':
                # Should be >= required
                if actual_value < required_value:
                    self.issues.append(
                        f"{key} too low: {actual_value} (required: >= {required_value})"
                    )
                    all_passed = False
                else:
                    self.passed_checks.append(f"{key}: {actual_value} (required: >= {required_value})")
            elif key == 'max_positions':
                # Should be <= required
                if actual_value > required_value:
                    self.warnings.append(
                        f"{key} higher than recommended: {actual_value} (recommended: {required_value})"
                    )
                else:
                    self.passed_checks.append(f"{key}: {actual_value} (required: <= {required_value})")
        
        return all_passed
    
    def check_monitoring(self) -> bool:
        """Check monitoring configuration"""
        if not self.config:
            return False
        
        prop_firm = self.config.get('prop_firm', {})
        monitoring = prop_firm.get('monitoring', {})
        
        all_passed = True
        
        for key, required_value in REQUIRED_MONITORING.items():
            actual_value = monitoring.get(key)
            
            if actual_value is None:
                self.issues.append(f"Missing monitoring config: {key} (required: {required_value})")
                all_passed = False
            elif actual_value != required_value:
                if key == 'check_interval_seconds' and actual_value <= required_value:
                    # Shorter interval is OK
                    self.passed_checks.append(f"{key}: {actual_value} (required: {required_value})")
                else:
                    self.warnings.append(
                        f"{key} differs: {actual_value} (recommended: {required_value})"
                    )
            else:
                self.passed_checks.append(f"{key}: {actual_value}")
        
        return all_passed
    
    def check_account_config(self) -> bool:
        """Check prop firm account is configured"""
        if not self.config:
            return False
        
        prop_firm = self.config.get('prop_firm', {})
        account_name = prop_firm.get('account', 'prop_firm_test')
        
        alpaca_config = self.config.get('alpaca', {})
        if account_name not in alpaca_config:
            self.issues.append(f"Prop firm account '{account_name}' not found in alpaca config")
            return False
        
        account_config = alpaca_config[account_name]
        if not account_config.get('api_key') or not account_config.get('secret_key'):
            self.issues.append(f"Prop firm account '{account_name}' missing credentials")
            return False
        
        self.passed_checks.append(f"Prop firm account '{account_name}' is configured")
        return True
    
    def check_signal_generation(self) -> bool:
        """Check signal generation is properly configured"""
        if not self.config:
            return False
        
        strategy = self.config.get('strategy', {})
        trading = self.config.get('trading', {})
        
        all_passed = True
        
        # Check multi-source is enabled
        if not strategy.get('use_multi_source', False):
            self.issues.append("Signal generation: 'use_multi_source' should be true")
            all_passed = False
        else:
            self.passed_checks.append("Multi-source signal generation enabled")
        
        # Check min_confidence matches prop firm requirement
        prop_firm = self.config.get('prop_firm', {})
        risk_limits = prop_firm.get('risk_limits', {})
        required_confidence = risk_limits.get('min_confidence', 82.0)
        
        trading_confidence = trading.get('min_confidence', 0)
        if trading_confidence < required_confidence:
            self.issues.append(
                f"Trading min_confidence ({trading_confidence}) < prop firm requirement ({required_confidence})"
            )
            all_passed = False
        else:
            self.passed_checks.append(f"Trading min_confidence: {trading_confidence} >= {required_confidence}")
        
        return all_passed
    
    def evaluate_profitability(self) -> Dict:
        """Evaluate profitability metrics (if available)"""
        profitability = {
            "evaluated": False,
            "metrics": {},
            "grade": "N/A",
            "recommendations": []
        }
        
        # Try to get performance data
        try:
            from argo.tracking.unified_tracker import UnifiedPerformanceTracker
            from argo.core.paper_trading_engine import PaperTradingEngine
            
            tracker = UnifiedPerformanceTracker()
            stats = tracker.get_performance_stats(asset_class=None, days=30)
            
            win_rate = stats.get('win_rate_percent', 0)
            completed_trades = stats.get('completed_trades', 0)
            
            if completed_trades > 0:
                # Get recent trades for profit factor calculation
                recent_trades = tracker.get_recent_trades(limit=100)
                completed = [t for t in recent_trades if t.get('outcome') != 'pending']
                
                if completed:
                    wins = [t for t in completed if t.get('outcome') == 'win']
                    losses = [t for t in completed if t.get('outcome') == 'loss']
                    
                    win_pnl = sum(t.get('pnl_dollars', 0) or 0 for t in wins)
                    loss_pnl = sum(t.get('pnl_dollars', 0) or 0 for t in losses)
                    
                    profit_factor = abs(win_pnl / loss_pnl) if loss_pnl != 0 else 0
                    
                    total_pnl = sum(t.get('pnl_dollars', 0) or 0 for t in completed)
                    
                    # Try to get account value for return calculation
                    try:
                        engine = PaperTradingEngine()
                        if engine.alpaca_enabled:
                            account = engine.get_account_details()
                            portfolio_value = account.get('portfolio_value', 0)
                            if portfolio_value > 0:
                                initial_value = portfolio_value - total_pnl
                                if initial_value > 0:
                                    return_pct = (total_pnl / initial_value) * 100
                                else:
                                    return_pct = 0
                            else:
                                return_pct = 0
                        else:
                            return_pct = 0
                    except:
                        return_pct = 0
                    
                    profitability["evaluated"] = True
                    profitability["metrics"] = {
                        "win_rate_percent": round(win_rate, 2),
                        "profit_factor": round(profit_factor, 2),
                        "return_percent": round(return_pct, 2),
                        "total_trades": completed_trades,
                        "wins": len(wins),
                        "losses": len(losses),
                        "total_pnl_dollars": round(total_pnl, 2)
                    }
                    
                    # Grade profitability
                    score = 0
                    if win_rate >= PROFITABILITY_TARGETS["win_rate_percent"]:
                        score += 1
                    if profit_factor >= PROFITABILITY_TARGETS["profit_factor"]:
                        score += 1
                    if return_pct >= PROFITABILITY_TARGETS["return_percent"]:
                        score += 1
                    
                    if score == 3:
                        profitability["grade"] = "A (Excellent)"
                    elif score == 2:
                        profitability["grade"] = "B (Good)"
                    elif score == 1:
                        profitability["grade"] = "C (Fair)"
                    else:
                        profitability["grade"] = "D (Needs Improvement)"
                    
                    # Recommendations
                    if win_rate < PROFITABILITY_TARGETS["win_rate_percent"]:
                        profitability["recommendations"].append(
                            f"Win rate ({win_rate:.2f}%) below target ({PROFITABILITY_TARGETS['win_rate_percent']}%)"
                        )
                    if profit_factor < PROFITABILITY_TARGETS["profit_factor"]:
                        profitability["recommendations"].append(
                            f"Profit factor ({profit_factor:.2f}) below target ({PROFITABILITY_TARGETS['profit_factor']})"
                        )
                    if return_pct < PROFITABILITY_TARGETS["return_percent"]:
                        profitability["recommendations"].append(
                            f"Return ({return_pct:.2f}%) below target ({PROFITABILITY_TARGETS['return_percent']}%)"
                        )
                    if not profitability["recommendations"]:
                        profitability["recommendations"].append("Profitability metrics meet targets")
        except Exception as e:
            logger.warning(f"Could not evaluate profitability: {e}")
            profitability["error"] = str(e)
        
        return profitability
    
    def check_compliance(self) -> Dict:
        """Check compliance with prop firm rules"""
        compliance = {
            "compliant": True,
            "issues": [],
            "warnings": []
        }
        
        if not self.config:
            compliance["compliant"] = False
            compliance["issues"].append("Config not loaded")
            return compliance
        
        prop_firm = self.config.get('prop_firm', {})
        risk_limits = prop_firm.get('risk_limits', {})
        
        # Check drawdown limit
        max_dd = risk_limits.get('max_drawdown_pct', 0)
        if max_dd > 2.5:  # Prop firm hard limit
            compliance["compliant"] = False
            compliance["issues"].append(f"Max drawdown ({max_dd}%) exceeds prop firm limit (2.5%)")
        elif max_dd > 2.0:
            compliance["warnings"].append(f"Max drawdown ({max_dd}%) close to recommended limit (2.0%)")
        
        # Check daily loss limit
        daily_loss = risk_limits.get('daily_loss_limit_pct', 0)
        if daily_loss > 5.0:  # Prop firm hard limit
            compliance["compliant"] = False
            compliance["issues"].append(f"Daily loss limit ({daily_loss}%) exceeds prop firm limit (5.0%)")
        elif daily_loss > 4.5:
            compliance["warnings"].append(f"Daily loss limit ({daily_loss}%) close to recommended limit (4.5%)")
        
        # Check position size
        position_size = risk_limits.get('max_position_size_pct', 0)
        if position_size > 10.0:  # Prop firm hard limit
            compliance["compliant"] = False
            compliance["issues"].append(f"Max position size ({position_size}%) exceeds prop firm limit (10.0%)")
        
        return compliance
    
    def generate_report(self) -> Dict:
        """Generate comprehensive evaluation report"""
        report = {
            "evaluation_date": datetime.now().isoformat(),
            "config_path": self.config_path,
            "production_server": self.production_server,
            "checks": {
                "prop_firm_enabled": self.check_prop_firm_enabled(),
                "risk_limits": self.check_risk_limits(),
                "monitoring": self.check_monitoring(),
                "account_config": self.check_account_config(),
                "signal_generation": self.check_signal_generation()
            },
            "compliance": self.check_compliance(),
            "profitability": self.evaluate_profitability(),
            "issues": self.issues,
            "warnings": self.warnings,
            "passed_checks": self.passed_checks
        }
        
        # Overall status
        all_checks_passed = all(report["checks"].values())
        compliance_ok = report["compliance"]["compliant"]
        
        if all_checks_passed and compliance_ok and not self.issues:
            report["overall_status"] = "✅ OK - Setup meets requirements"
        elif all_checks_passed and compliance_ok:
            report["overall_status"] = "⚠️ WARNING - Setup meets requirements but has warnings"
        else:
            report["overall_status"] = "❌ ISSUES FOUND - Setup does not meet requirements"
        
        return report
    
    def print_report(self, report: Dict):
        """Print formatted report"""
        print("\n" + "=" * 70)
        print("PROP FIRM PRODUCTION SETUP EVALUATION")
        print("=" * 70)
        print(f"Date: {report['evaluation_date']}")
        print(f"Config Path: {report['config_path'] or 'N/A'}")
        print(f"Production Server: {report['production_server']}")
        print()
        
        print("=" * 70)
        print("CONFIGURATION CHECKS")
        print("=" * 70)
        for check, passed in report["checks"].items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{check.replace('_', ' ').title()}: {status}")
        print()
        
        if report["passed_checks"]:
            print("✅ Passed Checks:")
            for check in report["passed_checks"]:
                print(f"   • {check}")
            print()
        
        if report["issues"]:
            print("❌ Issues Found:")
            for issue in report["issues"]:
                print(f"   • {issue}")
            print()
        
        if report["warnings"]:
            print("⚠️  Warnings:")
            for warning in report["warnings"]:
                print(f"   • {warning}")
            print()
        
        print("=" * 70)
        print("COMPLIANCE CHECK")
        print("=" * 70)
        compliance = report["compliance"]
        status = "✅ COMPLIANT" if compliance["compliant"] else "❌ NON-COMPLIANT"
        print(f"Status: {status}")
        
        if compliance["issues"]:
            print("Issues:")
            for issue in compliance["issues"]:
                print(f"   • {issue}")
        
        if compliance["warnings"]:
            print("Warnings:")
            for warning in compliance["warnings"]:
                print(f"   • {warning}")
        print()
        
        print("=" * 70)
        print("PROFITABILITY EVALUATION")
        print("=" * 70)
        profitability = report["profitability"]
        if profitability["evaluated"]:
            metrics = profitability["metrics"]
            print(f"Grade: {profitability['grade']}")
            print(f"Win Rate: {metrics.get('win_rate_percent', 0):.2f}% (target: {PROFITABILITY_TARGETS['win_rate_percent']}%)")
            print(f"Profit Factor: {metrics.get('profit_factor', 0):.2f} (target: {PROFITABILITY_TARGETS['profit_factor']})")
            print(f"Return: {metrics.get('return_percent', 0):.2f}% (target: {PROFITABILITY_TARGETS['return_percent']}%)")
            print(f"Total Trades: {metrics.get('total_trades', 0)}")
            print(f"Total P&L: ${metrics.get('total_pnl_dollars', 0):,.2f}")
            
            if profitability["recommendations"]:
                print("\nRecommendations:")
                for rec in profitability["recommendations"]:
                    print(f"   • {rec}")
        else:
            print("⚠️  Profitability data not available")
            if "error" in profitability:
                print(f"   Error: {profitability['error']}")
        print()
        
        print("=" * 70)
        print("OVERALL STATUS")
        print("=" * 70)
        print(report["overall_status"])
        print()


def main():
    parser = argparse.ArgumentParser(description='Evaluate prop firm production setup')
    parser.add_argument('--config-path', type=str, help='Local path to config.json')
    parser.add_argument('--server', type=str, default='178.156.194.174', help='Production server')
    parser.add_argument('--user', type=str, default='root', help='SSH user')
    parser.add_argument('--no-ssh', action='store_true', help='Disable SSH (use local config only)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    
    evaluator = PropFirmProductionEvaluator(
        production_server=args.server,
        production_user=args.user,
        config_path=args.config_path,
        use_ssh=not args.no_ssh
    )
    
    if not evaluator.load_production_config():
        print("❌ Failed to load production config")
        sys.exit(1)
    
    report = evaluator.generate_report()
    
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        evaluator.print_report(report)
        
        # Exit with error code if issues found
        if evaluator.issues or not all(report["checks"].values()):
            sys.exit(1)


if __name__ == '__main__':
    main()

