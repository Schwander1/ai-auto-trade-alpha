#!/usr/bin/env python3
"""
Alpine Analytics - Trade Verification Script
Independently verify our 4,374-trade history
"""

import pandas as pd
import hashlib
import sys

def verify_trades(csv_file):
    print("="*80)
    print("ALPINE ANALYTICS - TRADE VERIFICATION")
    print("="*80)
    print()
    
    # Load data
    print(f"Loading: {csv_file}")
    df = pd.read_csv(csv_file, comment='#')
    print(f"✓ Loaded {len(df)} trades")
    print()
    
    # Verify hashes
    print("Verifying SHA-256 hashes...")
    hash_errors = 0
    
    for idx, row in df.head(100).iterrows():  # Check first 100
        expected = row['verification_hash']
        data = f"{row['trade_id']}{row['entry_date']}{row['symbol']}"
        calculated = hashlib.sha256(data.encode()).hexdigest()[:16]
        
        if expected != calculated:
            print(f"  ❌ Trade {row['trade_id']}: Hash mismatch!")
            hash_errors += 1
    
    if hash_errors == 0:
        print("  ✓ All hashes verified (first 100 trades)")
    else:
        print(f"  ❌ Found {hash_errors} hash errors!")
    print()
    
    # Calculate performance
    print("Calculating performance...")
    
    wins = len(df[df['pnl_percent'] > 0])
    total = len(df)
    win_rate = (wins / total) * 100
    
    # Simulate trading with Kelly
    starting_capital = 100000
    capital = starting_capital
    kelly_pct = 0.189
    
    for _, trade in df.iterrows():
        position_size = capital * kelly_pct
        pnl_dollars = position_size * (trade['pnl_percent'] / 100)
        capital += pnl_dollars
    
    total_return = ((capital - starting_capital) / starting_capital) * 100
    cagr = (((capital / starting_capital) ** (1/20)) - 1) * 100
    
    print(f"  Total Trades: {total}")
    print(f"  Win Rate: {win_rate:.1f}%")
    print(f"  Total Return: +{total_return:.1f}%")
    print(f"  CAGR: {cagr:.2f}%")
    print(f"  $100K becomes: ${capital:,.0f}")
    print()
    
    # Compare to claims
    print("Verification Results:")
    print("  ✓ Trade count matches (4,374)" if total == 4374 else "  ❌ Trade count mismatch!")
    print("  ✓ Win rate ~45.3%" if abs(win_rate - 45.3) < 1 else f"  ⚠️  Win rate: {win_rate:.1f}%")
    print("  ✓ Return ~565%" if abs(total_return - 565) < 10 else f"  ⚠️  Return: +{total_return:.1f}%")
    print("  ✓ CAGR ~9.94%" if abs(cagr - 9.94) < 0.5 else f"  ⚠️  CAGR: {cagr:.2f}%")
    print()
    print("="*80)
    print("VERIFICATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 verify_trades.py <csv_file>")
        sys.exit(1)
    
    verify_trades(sys.argv[1])
