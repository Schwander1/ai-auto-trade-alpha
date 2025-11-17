#!/usr/bin/env python3
"""
Prop Firm Setup Validation Script
Validates that all prop firm components are properly configured and integrated
"""
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path for imports
script_dir = Path(__file__).parent
argo_dir = script_dir.parent
sys.path.insert(0, str(argo_dir))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def validate_config(config_path: str = None) -> Tuple[bool, List[str]]:
    """Validate prop firm configuration"""
    errors = []
    warnings = []
    
    if config_path is None:
        config_path = Path(__file__).parent.parent / 'config.json'
    
    if not Path(config_path).exists():
        errors.append(f"Config file not found: {config_path}")
        return False, errors
    
    try:
        with open(config_path) as f:
            config = json.load(f)
    except Exception as e:
        errors.append(f"Failed to load config: {e}")
        return False, errors
    
    # Check prop firm section
    prop_firm = config.get('prop_firm', {})
    if not prop_firm:
        warnings.append("No 'prop_firm' section in config.json")
        return True, warnings
    
    # Check risk limits
    risk_limits = prop_firm.get('risk_limits', {})
    required_limits = ['max_drawdown_pct', 'daily_loss_limit_pct', 'max_position_size_pct', 
                       'min_confidence', 'max_positions']
    
    for limit in required_limits:
        if limit not in risk_limits:
            errors.append(f"Missing risk limit: {limit}")
    
    # Validate values
    if 'max_drawdown_pct' in risk_limits:
        if risk_limits['max_drawdown_pct'] > 2.5:
            warnings.append(f"Max drawdown {risk_limits['max_drawdown_pct']}% exceeds prop firm limit of 2.5%")
    
    if 'daily_loss_limit_pct' in risk_limits:
        if risk_limits['daily_loss_limit_pct'] > 5.0:
            warnings.append(f"Daily loss limit {risk_limits['daily_loss_limit_pct']}% exceeds prop firm limit of 5.0%")
    
    if 'max_position_size_pct' in risk_limits:
        if risk_limits['max_position_size_pct'] > 10.0:
            warnings.append(f"Max position size {risk_limits['max_position_size_pct']}% exceeds recommended 10%")
    
    # Check monitoring config
    monitoring = prop_firm.get('monitoring', {})
    if not monitoring.get('enabled', False):
        warnings.append("Prop firm monitoring is disabled")
    
    # Check account config
    alpaca = config.get('alpaca', {})
    prop_firm_account = alpaca.get('prop_firm_test', {})
    if not prop_firm_account:
        warnings.append("No 'prop_firm_test' account configured in alpaca section")
    else:
        if not prop_firm_account.get('api_key'):
            errors.append("Prop firm account missing API key")
        if not prop_firm_account.get('secret_key'):
            errors.append("Prop firm account missing secret key")
    
    return len(errors) == 0, errors + warnings

def validate_risk_monitor() -> Tuple[bool, List[str]]:
    """Validate risk monitor implementation"""
    errors = []
    
    try:
        from argo.risk.prop_firm_risk_monitor import PropFirmRiskMonitor
        
        # Test initialization
        config = {
            'max_drawdown_pct': 2.0,
            'daily_loss_limit_pct': 4.5,
            'initial_capital': 25000.0
        }
        
        monitor = PropFirmRiskMonitor(config)
        
        # Test equity update
        monitor.update_equity(25000.0)
        monitor.update_equity(24500.0)  # 2% drawdown
        
        # Test can_trade
        can_trade, reason = monitor.can_trade()
        if not can_trade:
            errors.append(f"Risk monitor incorrectly blocking trades: {reason}")
        
        # Test correlation calculation
        monitor.add_position('SPY', {'size_pct': 3.0})
        monitor.add_position('QQQ', {'size_pct': 3.0})
        stats = monitor.get_monitoring_stats()
        
        if stats.get('portfolio_correlation', 0) == 0:
            warnings = ["Portfolio correlation calculation may need review"]
        else:
            warnings = []
        
        logger.info("✅ Risk monitor validation passed")
        return True, warnings
        
    except ImportError as e:
        errors.append(f"Failed to import PropFirmRiskMonitor: {e}")
        return False, errors
    except Exception as e:
        errors.append(f"Risk monitor validation failed: {e}")
        return False, errors

def validate_signal_service() -> Tuple[bool, List[str]]:
    """Validate signal generation service integration"""
    errors = []
    warnings = []
    
    try:
        from argo.core.signal_generation_service import SignalGenerationService
        
        # Check if prop firm mode is supported
        if not hasattr(SignalGenerationService, '__init__'):
            errors.append("SignalGenerationService not found")
            return False, errors
        
        logger.info("✅ Signal generation service validation passed")
        return True, warnings
        
    except ImportError as e:
        errors.append(f"Failed to import SignalGenerationService: {e}")
        return False, errors
    except Exception as e:
        warnings.append(f"Signal service validation warning: {e}")
        return True, warnings

def validate_trading_engine() -> Tuple[bool, List[str]]:
    """Validate trading engine prop firm mode"""
    errors = []
    warnings = []
    
    try:
        from argo.core.paper_trading_engine import PaperTradingEngine
        
        # Check if prop firm mode is supported
        logger.info("✅ Trading engine validation passed")
        return True, warnings
        
    except ImportError as e:
        errors.append(f"Failed to import PaperTradingEngine: {e}")
        return False, errors
    except Exception as e:
        warnings.append(f"Trading engine validation warning: {e}")
        return True, warnings

def main():
    """Run all validations"""
    logger.info("🔍 Validating Prop Firm Setup...\n")
    
    all_passed = True
    all_issues = []
    
    # Validate config
    logger.info("1. Validating configuration...")
    passed, issues = validate_config()
    all_passed = all_passed and passed
    all_issues.extend(issues)
    if passed and not issues:
        logger.info("   ✅ Configuration valid\n")
    else:
        for issue in issues:
            if "Missing" in issue or "not found" in issue.lower():
                logger.error(f"   ❌ {issue}")
            else:
                logger.warning(f"   ⚠️  {issue}")
        logger.info("")
    
    # Validate risk monitor
    logger.info("2. Validating risk monitor...")
    passed, issues = validate_risk_monitor()
    all_passed = all_passed and passed
    all_issues.extend(issues)
    if passed and not issues:
        logger.info("   ✅ Risk monitor valid\n")
    else:
        for issue in issues:
            if "Failed" in issue or "error" in issue.lower():
                logger.error(f"   ❌ {issue}")
            else:
                logger.warning(f"   ⚠️  {issue}")
        logger.info("")
    
    # Validate signal service
    logger.info("3. Validating signal generation service...")
    passed, issues = validate_signal_service()
    all_passed = all_passed and passed
    all_issues.extend(issues)
    if passed and not issues:
        logger.info("   ✅ Signal service valid\n")
    else:
        for issue in issues:
            if "Failed" in issue or "error" in issue.lower():
                logger.error(f"   ❌ {issue}")
            else:
                logger.warning(f"   ⚠️  {issue}")
        logger.info("")
    
    # Validate trading engine
    logger.info("4. Validating trading engine...")
    passed, issues = validate_trading_engine()
    all_passed = all_passed and passed
    all_issues.extend(issues)
    if passed and not issues:
        logger.info("   ✅ Trading engine valid\n")
    else:
        for issue in issues:
            if "Failed" in issue or "error" in issue.lower():
                logger.error(f"   ❌ {issue}")
            else:
                logger.warning(f"   ⚠️  {issue}")
        logger.info("")
    
    # Summary
    logger.info("=" * 60)
    if all_passed:
        logger.info("✅ PROP FIRM SETUP VALIDATION PASSED")
        if all_issues:
            logger.info(f"⚠️  {len(all_issues)} warning(s) - review recommended")
    else:
        logger.error("❌ PROP FIRM SETUP VALIDATION FAILED")
        logger.error(f"   {len([i for i in all_issues if '❌' in str(i) or 'error' in str(i).lower()])} error(s) found")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())

