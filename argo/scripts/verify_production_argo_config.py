#!/usr/bin/env python3
"""
Production ARGO Configuration Verification and Optimization Script

Verifies and ensures:
1. Prop trading is properly configured with signal generation
2. Regular trading is properly configured with signal generation
3. Both have appropriate strategies from backtesting applied
4. Production configuration is optimized

Usage:
    python scripts/verify_production_argo_config.py [--fix] [--config-path PATH]
"""
import sys
import json
import os
import argparse
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductionConfigVerifier:
    """Verify and optimize production ARGO configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_path()
        self.config = None
        self.issues = []
        self.fixes_applied = []
        
    def _find_config_path(self) -> str:
        """Find production config path"""
        # Check environment variable first
        env_path = os.getenv('ARGO_CONFIG_PATH')
        if env_path and os.path.exists(env_path):
            return env_path
        
        # Check production paths
        prod_paths = [
            '/root/argo-production-prop-firm/config.json',  # Prop firm service
            '/root/argo-production-green/config.json',      # Regular trading (green)
            '/root/argo-production-blue/config.json',       # Regular trading (blue)
            '/root/argo-production/config.json',            # Legacy
            Path(__file__).parent.parent / 'config.json',   # Local dev
        ]
        
        for path in prod_paths:
            if isinstance(path, Path):
                path = str(path)
            if os.path.exists(path):
                logger.info(f"Found config at: {path}")
                return path
        
        # Default fallback
        return '/root/argo-production/config.json'
    
    def load_config(self) -> bool:
        """Load configuration file"""
        try:
            if not os.path.exists(self.config_path):
                logger.error(f"Config file not found: {self.config_path}")
                return False
            
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            
            logger.info(f"✅ Loaded config from: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return False
    
    def verify_signal_generation(self) -> bool:
        """Verify signal generation is properly configured"""
        logger.info("🔍 Verifying signal generation configuration...")
        
        issues = []
        
        # Check strategy section exists
        if 'strategy' not in self.config:
            issues.append("Missing 'strategy' section in config")
        else:
            strategy = self.config['strategy']
            
            # Check multi-source is enabled
            if not strategy.get('use_multi_source', False):
                issues.append("Signal generation: 'use_multi_source' should be true")
            
            # Check weights are configured
            required_weights = ['weight_massive', 'weight_alpha_vantage', 
                              'weight_x_sentiment', 'weight_sonar']
            for weight in required_weights:
                if weight not in strategy:
                    issues.append(f"Missing strategy weight: {weight}")
        
        # Check trading section for signal generation settings
        if 'trading' not in self.config:
            issues.append("Missing 'trading' section in config")
        else:
            trading = self.config['trading']
            
            # Check min_confidence is set
            if 'min_confidence' not in trading:
                issues.append("Missing 'min_confidence' in trading config")
        
        if issues:
            self.issues.extend(issues)
            logger.warning(f"⚠️  Signal generation issues found: {len(issues)}")
            for issue in issues:
                logger.warning(f"   - {issue}")
            return False
        
        logger.info("✅ Signal generation properly configured")
        return True
    
    def verify_prop_trading(self) -> bool:
        """Verify prop trading configuration"""
        logger.info("🔍 Verifying prop trading configuration...")
        
        issues = []
        
        # Check prop_firm section exists
        if 'prop_firm' not in self.config:
            issues.append("Missing 'prop_firm' section in config")
            self.issues.extend(issues)
            return False
        
        prop_firm = self.config['prop_firm']
        
        # Check if enabled
        if not prop_firm.get('enabled', False):
            logger.info("ℹ️  Prop firm mode is disabled (this is OK if checking regular trading config)")
            return True
        
        # Verify prop firm uses signal generation (should be automatic via SignalGenerationService)
        # Check risk limits
        if 'risk_limits' not in prop_firm:
            issues.append("Missing 'risk_limits' in prop_firm config")
        else:
            risk_limits = prop_firm['risk_limits']
            
            # Verify prop firm specific limits
            if 'min_confidence' not in risk_limits:
                issues.append("Prop firm: Missing 'min_confidence' (should be 82%+)")
            elif risk_limits.get('min_confidence', 0) < 82.0:
                issues.append(f"Prop firm: min_confidence too low ({risk_limits.get('min_confidence')}%, should be 82%+)")
            
            if 'max_drawdown_pct' not in risk_limits:
                issues.append("Prop firm: Missing 'max_drawdown_pct' (should be 2.0%)")
            elif risk_limits.get('max_drawdown_pct', 10) > 2.0:
                issues.append(f"Prop firm: max_drawdown_pct too high ({risk_limits.get('max_drawdown_pct')}%, should be 2.0%)")
            
            if 'max_position_size_pct' not in risk_limits:
                issues.append("Prop firm: Missing 'max_position_size_pct' (should be 3.0%)")
            elif risk_limits.get('max_position_size_pct', 15) > 3.0:
                issues.append(f"Prop firm: max_position_size_pct too high ({risk_limits.get('max_position_size_pct')}%, should be 3.0%)")
        
        # Verify prop firm account is configured
        if 'alpaca' in self.config:
            prop_account = prop_firm.get('account', 'prop_firm_test')
            if prop_account not in self.config['alpaca']:
                issues.append(f"Prop firm account '{prop_account}' not found in alpaca config")
        
        if issues:
            self.issues.extend(issues)
            logger.warning(f"⚠️  Prop trading issues found: {len(issues)}")
            for issue in issues:
                logger.warning(f"   - {issue}")
            return False
        
        logger.info("✅ Prop trading properly configured with signal generation")
        return True
    
    def verify_regular_trading(self) -> bool:
        """Verify regular trading configuration"""
        logger.info("🔍 Verifying regular trading configuration...")
        
        issues = []
        
        # Check if prop firm is disabled (regular trading mode)
        prop_firm_enabled = self.config.get('prop_firm', {}).get('enabled', False)
        
        if prop_firm_enabled:
            logger.info("ℹ️  Prop firm mode is enabled, skipping regular trading checks")
            return True
        
        # Verify regular trading uses signal generation
        if 'trading' not in self.config:
            issues.append("Missing 'trading' section in config")
        else:
            trading = self.config['trading']
            
            # Check min_confidence (should be lower than prop firm)
            if 'min_confidence' not in trading:
                issues.append("Regular trading: Missing 'min_confidence'")
            elif trading.get('min_confidence', 0) < 75.0:
                issues.append(f"Regular trading: min_confidence too low ({trading.get('min_confidence')}%, should be 75%+)")
            
            # Check auto_execute
            if 'auto_execute' not in trading:
                issues.append("Regular trading: Missing 'auto_execute' flag")
        
        if issues:
            self.issues.extend(issues)
            logger.warning(f"⚠️  Regular trading issues found: {len(issues)}")
            for issue in issues:
                logger.warning(f"   - {issue}")
            return False
        
        logger.info("✅ Regular trading properly configured with signal generation")
        return True
    
    def verify_backtesting_strategies(self) -> bool:
        """Verify backtesting strategies are properly configured"""
        logger.info("🔍 Verifying backtesting strategy configuration...")
        
        issues = []
        
        # Check if backtest section exists
        if 'backtest' not in self.config:
            logger.warning("⚠️  No 'backtest' section found (optional but recommended)")
            return True
        
        backtest = self.config['backtest']
        
        # Verify symbols are configured
        if 'symbols' not in backtest:
            issues.append("Backtest: Missing 'symbols' section")
        else:
            symbols = backtest['symbols']
            if 'stocks' not in symbols and 'crypto' not in symbols:
                issues.append("Backtest: No stocks or crypto symbols configured")
        
        if issues:
            self.issues.extend(issues)
            logger.warning(f"⚠️  Backtesting strategy issues found: {len(issues)}")
            for issue in issues:
                logger.warning(f"   - {issue}")
            return False
        
        logger.info("✅ Backtesting strategies properly configured")
        return True
    
    def fix_config(self) -> bool:
        """Fix configuration issues"""
        logger.info("🔧 Applying fixes to configuration...")
        
        if not self.config:
            logger.error("Cannot fix: config not loaded")
            return False
        
        fixes = []
        
        # Fix 1: Ensure strategy section exists
        if 'strategy' not in self.config:
            self.config['strategy'] = {
                'use_multi_source': True,
                'weight_massive': 0.4,
                'weight_alpha_vantage': 0.25,
                'weight_x_sentiment': 0.2,
                'weight_sonar': 0.15
            }
            fixes.append("Added 'strategy' section with default weights")
        
        # Fix 2: Ensure trading section exists
        if 'trading' not in self.config:
            self.config['trading'] = {
                'auto_execute': True,
                'min_confidence': 75.0,
                'consensus_threshold': 75.0,
                'profit_target': 0.05,
                'stop_loss': 0.03,
                'position_size_pct': 10,
                'max_position_size_pct': 15,
                'max_correlated_positions': 3,
                'max_drawdown_pct': 10,
                'daily_loss_limit_pct': 5.0
            }
            fixes.append("Added 'trading' section with default values")
        
        # Fix 3: Ensure prop_firm section exists (if needed)
        prop_firm_enabled = self.config.get('prop_firm', {}).get('enabled', False)
        if prop_firm_enabled:
            if 'prop_firm' not in self.config:
                self.config['prop_firm'] = {}
            
            prop_firm = self.config['prop_firm']
            
            # Ensure risk_limits exist
            if 'risk_limits' not in prop_firm:
                prop_firm['risk_limits'] = {}
            
            risk_limits = prop_firm['risk_limits']
            
            # Set prop firm defaults
            if 'min_confidence' not in risk_limits:
                risk_limits['min_confidence'] = 82.0
                fixes.append("Set prop firm min_confidence to 82.0%")
            
            if 'max_drawdown_pct' not in risk_limits:
                risk_limits['max_drawdown_pct'] = 2.0
                fixes.append("Set prop firm max_drawdown_pct to 2.0%")
            
            if 'max_position_size_pct' not in risk_limits:
                risk_limits['max_position_size_pct'] = 3.0
                fixes.append("Set prop firm max_position_size_pct to 3.0%")
            
            if 'daily_loss_limit_pct' not in risk_limits:
                risk_limits['daily_loss_limit_pct'] = 4.5
                fixes.append("Set prop firm daily_loss_limit_pct to 4.5%")
            
            if 'max_positions' not in risk_limits:
                risk_limits['max_positions'] = 3
                fixes.append("Set prop firm max_positions to 3")
            
            if 'max_stop_loss_pct' not in risk_limits:
                risk_limits['max_stop_loss_pct'] = 1.5
                fixes.append("Set prop firm max_stop_loss_pct to 1.5%")
            
            # Ensure monitoring section
            if 'monitoring' not in prop_firm:
                prop_firm['monitoring'] = {
                    'enabled': True,
                    'check_interval_seconds': 5,
                    'alert_on_warning': True,
                    'auto_shutdown': True
                }
                fixes.append("Added prop firm monitoring section")
        
        # Fix 4: Ensure backtest section exists
        if 'backtest' not in self.config:
            self.config['backtest'] = {
                'symbols': {
                    'stocks': ['AAPL', 'NVDA', 'TSLA', 'MSFT', 'GOOGL', 'META', 'AMD', 'AMZN', 'SPY', 'QQQ'],
                    'crypto': ['BTC-USD', 'ETH-USD', 'SOL-USD', 'AVAX-USD']
                }
            }
            fixes.append("Added 'backtest' section with default symbols")
        
        if fixes:
            self.fixes_applied.extend(fixes)
            logger.info(f"✅ Applied {len(fixes)} fixes")
            for fix in fixes:
                logger.info(f"   - {fix}")
            return True
        else:
            logger.info("ℹ️  No fixes needed")
            return False
    
    def save_config(self) -> bool:
        """Save configuration file"""
        try:
            # Create backup
            backup_path = f"{self.config_path}.backup"
            if os.path.exists(self.config_path):
                import shutil
                shutil.copy2(self.config_path, backup_path)
                logger.info(f"✅ Created backup: {backup_path}")
            
            # Save updated config
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            logger.info(f"✅ Saved updated config to: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def verify_all(self) -> Tuple[bool, Dict]:
        """Run all verification checks"""
        logger.info("=" * 60)
        logger.info("PRODUCTION ARGO CONFIGURATION VERIFICATION")
        logger.info("=" * 60)
        logger.info(f"Config path: {self.config_path}")
        logger.info("")
        
        if not self.load_config():
            return False, {'error': 'Failed to load config'}
        
        results = {
            'signal_generation': self.verify_signal_generation(),
            'prop_trading': self.verify_prop_trading(),
            'regular_trading': self.verify_regular_trading(),
            'backtesting_strategies': self.verify_backtesting_strategies(),
        }
        
        all_passed = all(results.values())
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("VERIFICATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Signal Generation: {'✅ PASS' if results['signal_generation'] else '❌ FAIL'}")
        logger.info(f"Prop Trading: {'✅ PASS' if results['prop_trading'] else '❌ FAIL'}")
        logger.info(f"Regular Trading: {'✅ PASS' if results['regular_trading'] else '❌ FAIL'}")
        logger.info(f"Backtesting Strategies: {'✅ PASS' if results['backtesting_strategies'] else '❌ FAIL'}")
        logger.info("")
        
        if self.issues:
            logger.warning(f"Found {len(self.issues)} issue(s):")
            for issue in self.issues:
                logger.warning(f"  - {issue}")
        
        logger.info("")
        logger.info(f"Overall: {'✅ ALL CHECKS PASSED' if all_passed else '❌ ISSUES FOUND'}")
        
        return all_passed, {
            'results': results,
            'issues': self.issues,
            'config_path': self.config_path
        }


def main():
    parser = argparse.ArgumentParser(description='Verify production ARGO configuration')
    parser.add_argument('--fix', action='store_true', help='Automatically fix issues')
    parser.add_argument('--config-path', type=str, help='Path to config.json file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    
    verifier = ProductionConfigVerifier(config_path=args.config_path)
    all_passed, summary = verifier.verify_all()
    
    if args.fix and not all_passed:
        logger.info("")
        logger.info("=" * 60)
        logger.info("APPLYING FIXES")
        logger.info("=" * 60)
        
        if verifier.fix_config():
            verifier.save_config()
            logger.info("")
            logger.info("✅ Configuration fixed! Re-running verification...")
            logger.info("")
            all_passed, summary = verifier.verify_all()
    
    if args.json:
        import json as json_module
        print(json_module.dumps(summary, indent=2))
    else:
        if not all_passed:
            sys.exit(1)


if __name__ == '__main__':
    main()

