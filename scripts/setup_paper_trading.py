#!/usr/bin/env python3
"""
Setup Paper Trading Configuration for Prop Firm
"""
import json
import sys
from pathlib import Path

def setup_paper_trading():
    """Configure system for paper trading with prop firm requirements"""
    config_path = Path(__file__).parent.parent / "argo" / "config.json"
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return False
    
    with open(config_path) as f:
        config = json.load(f)
    
    print("=" * 70)
    print("📋 PAPER TRADING SETUP FOR PROP FIRM")
    print("=" * 70)
    print()
    
    # Check current risk settings
    trading = config.get('trading', {})
    risk = config.get('enhancements', {}).get('risk_monitoring', {})
    
    print("🔍 CURRENT CONFIGURATION:")
    print(f"   Min Confidence: {trading.get('min_confidence', 75.0)}%")
    print(f"   Max Drawdown: {risk.get('max_drawdown_pct', 10.0)}%")
    print(f"   Daily Loss Limit: {risk.get('daily_loss_limit_pct', 5.0)}%")
    print(f"   Position Size: {trading.get('position_size_pct', 10)}%")
    print()
    
    # Prop firm requirements
    print("📊 PROP FIRM REQUIREMENTS:")
    print("   Max Drawdown: ≤2.0% (typical)")
    print("   Daily Loss Limit: ≤4.5% (typical)")
    print("   Min Confidence: 80%+ (recommended)")
    print()
    
    # Check if already configured
    prop_firm_ready = (
        risk.get('max_drawdown_pct', 10.0) <= 2.0 and
        risk.get('daily_loss_limit_pct', 5.0) <= 4.5 and
        trading.get('min_confidence', 75.0) >= 80.0
    )
    
    if prop_firm_ready:
        print("✅ CONFIGURATION STATUS: Ready for Prop Firm Trading!")
        print()
        print("   All requirements met:")
        print("   ✅ Max drawdown ≤2.0%")
        print("   ✅ Daily loss limit ≤4.5%")
        print("   ✅ Min confidence ≥80%")
        print()
    else:
        print("⚠️  CONFIGURATION STATUS: Needs adjustment for prop firm")
        print()
        print("   Recommended changes:")
        if risk.get('max_drawdown_pct', 10.0) > 2.0:
            print(f"   • Reduce max_drawdown_pct: {risk.get('max_drawdown_pct', 10.0)}% → 2.0%")
        if risk.get('daily_loss_limit_pct', 5.0) > 4.5:
            print(f"   • Reduce daily_loss_limit_pct: {risk.get('daily_loss_limit_pct', 5.0)}% → 4.5%")
        if trading.get('min_confidence', 75.0) < 80.0:
            print(f"   • Increase min_confidence: {trading.get('min_confidence', 75.0)}% → 80.0%")
        print()
    
    # Paper trading checklist
    print("📋 PAPER TRADING CHECKLIST:")
    print()
    print("   [ ] 1. Choose prop firm (FTMO, TopStep, etc.)")
    print("   [ ] 2. Create demo/paper account")
    print("   [ ] 3. Configure API connection (if available)")
    print("   [ ] 4. Set risk limits in prop firm platform")
    print("   [ ] 5. Start with small position sizes")
    print("   [ ] 6. Monitor signals (80%+ confidence only)")
    print("   [ ] 7. Track performance daily")
    print("   [ ] 8. Validate profitability before going live")
    print()
    
    # Risk monitoring status
    risk_enabled = config.get('feature_flags', {}).get('risk_monitoring', False)
    if risk_enabled:
        print("✅ Risk monitoring: ENABLED")
        print("   • Real-time drawdown tracking")
        print("   • Daily loss limit enforcement")
        print("   • Emergency shutdown capability")
    else:
        print("⚠️  Risk monitoring: DISABLED")
        print("   • Enable in config.json: feature_flags.risk_monitoring = true")
    print()
    
    print("=" * 70)
    print("💡 NEXT STEPS:")
    print("   1. Monitor signals: python3 scripts/monitor_signals.py")
    print("   2. Start paper trading with prop firm")
    print("   3. Validate profitability over 1-2 weeks")
    print("   4. Fund live account once profitable")
    print("=" * 70)
    
    return prop_firm_ready

if __name__ == '__main__':
    try:
        setup_paper_trading()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

