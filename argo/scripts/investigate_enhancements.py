#!/usr/bin/env python3
"""
Comprehensive investigation script to trace the enhancement pipeline
and verify that performance enhancements are being applied correctly.
"""

import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.backtest.data_manager import DataManager
from argo.backtest.historical_signal_generator import HistoricalSignalGenerator
from argo.backtest.performance_enhancer import PerformanceEnhancer
from argo.core.signal_generation_service import SignalGenerationService

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def investigate_signal_flow(symbol: str = "AAPL", index: int = 100):
    """Trace a single signal through the entire pipeline"""
    
    print(f"\n{'='*80}")
    print(f"🔍 COMPREHENSIVE ENHANCEMENT INVESTIGATION")
    print(f"{'='*80}")
    print(f"Symbol: {symbol}")
    print(f"Index: {index}")
    print(f"{'='*80}\n")
    
    # Initialize components
    print("📦 Initializing components...")
    dm = DataManager()
    signal_service = SignalGenerationService()
    signal_generator = HistoricalSignalGenerator(signal_service, dm)
    enhancer = PerformanceEnhancer(
        min_confidence=60.0,
        require_volume_confirmation=False,
        require_trend_filter=False,
        use_adaptive_stops=True,
        use_trailing_stops=True,
        use_position_sizing=True
    )
    
    # Fetch data
    print(f"\n📊 Fetching data for {symbol}...")
    df = dm.fetch_historical_data(symbol, period="20y")
    if df is None or len(df) == 0:
        print(f"❌ Failed to fetch data for {symbol}")
        return
    
    df = dm._clean_data(df)
    print(f"✅ Data loaded: {len(df)} rows")
    print(f"   Date range: {df.index[0]} to {df.index[-1]}")
    
    if index >= len(df):
        index = len(df) - 1
        print(f"⚠️  Adjusted index to {index}")
    
    # Get current data point
    current_date = df.index[index]
    current_price = float(df.iloc[index]['Close'])
    print(f"\n📅 Current date: {current_date}")
    print(f"💰 Current price: ${current_price:.2f}")
    
    # Step 1: Generate initial signal
    print(f"\n{'─'*80}")
    print("STEP 1: Generate Initial Signal")
    print(f"{'─'*80}")
    
    signal = signal_generator.generate_signal(symbol, df, index)
    
    if not signal:
        print("❌ No signal generated!")
        return
    
    print(f"✅ Signal generated:")
    print(f"   Action: {signal.get('action')}")
    print(f"   Confidence: {signal.get('confidence', 0):.2f}%")
    print(f"   Entry Price: ${signal.get('entry_price', current_price):.2f}")
    print(f"   Stop Price (initial): ${signal.get('stop_price', 'N/A')}")
    print(f"   Target Price (initial): ${signal.get('target_price', 'N/A')}")
    
    initial_stop = signal.get('stop_price')
    initial_target = signal.get('target_price')
    
    # Step 2: Extract indicators
    print(f"\n{'─'*80}")
    print("STEP 2: Extract Indicators")
    print(f"{'─'*80}")
    
    indicators = {
        'sma_20': float(df.iloc[index]['sma_20']) if 'sma_20' in df.columns and not pd.isna(df.iloc[index]['sma_20']) else None,
        'sma_50': float(df.iloc[index]['sma_50']) if 'sma_50' in df.columns and not pd.isna(df.iloc[index]['sma_50']) else None,
        'rsi': float(df.iloc[index]['rsi']) if 'rsi' in df.columns and not pd.isna(df.iloc[index]['rsi']) else None,
        'macd': float(df.iloc[index]['macd']) if 'macd' in df.columns and not pd.isna(df.iloc[index]['macd']) else None,
        'macd_signal': float(df.iloc[index]['macd_signal']) if 'macd_signal' in df.columns and not pd.isna(df.iloc[index]['macd_signal']) else None,
        'volume_ratio': float(df.iloc[index]['volume_ratio']) if 'volume_ratio' in df.columns and not pd.isna(df.iloc[index]['volume_ratio']) else None,
        'volatility': float(df.iloc[index]['volatility']) if 'volatility' in df.columns and not pd.isna(df.iloc[index]['volatility']) else 0.2,
        'current_price': current_price
    }
    
    print("✅ Indicators extracted:")
    for key, value in indicators.items():
        if value is not None:
            print(f"   {key}: {value:.4f}" if isinstance(value, (int, float)) else f"   {key}: {value}")
    
    # Step 3: Calculate ATR for adaptive stops
    print(f"\n{'─'*80}")
    print("STEP 3: Calculate ATR (for Adaptive Stops)")
    print(f"{'─'*80}")
    
    try:
        historical_data = df.iloc[:index+1]
        atr = enhancer.calculate_atr(
            historical_data['High'],
            historical_data['Low'],
            historical_data['Close']
        )
        current_atr = atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else current_price * 0.02
        atr_pct = (current_atr / current_price) * 100
        print(f"✅ ATR calculated:")
        print(f"   ATR: ${current_atr:.4f}")
        print(f"   ATR %: {atr_pct:.4f}%")
    except Exception as e:
        print(f"❌ ATR calculation failed: {e}")
        current_atr = current_price * 0.02
        atr_pct = 2.0
    
    # Step 4: Apply enhancements
    print(f"\n{'─'*80}")
    print("STEP 4: Apply Performance Enhancements")
    print(f"{'─'*80}")
    
    print(f"Enhancer settings:")
    print(f"   min_confidence: {enhancer.min_confidence}")
    print(f"   require_volume_confirmation: {enhancer.require_volume_confirmation}")
    print(f"   require_trend_filter: {enhancer.require_trend_filter}")
    print(f"   use_adaptive_stops: {enhancer.use_adaptive_stops}")
    print(f"   use_trailing_stops: {enhancer.use_trailing_stops}")
    print(f"   use_position_sizing: {enhancer.use_position_sizing}")
    
    enhanced_signal = enhancer.enhance_signal(signal.copy(), indicators, df, index)
    
    if not enhanced_signal:
        print("❌ Signal was filtered out by enhancer!")
        return
    
    print(f"\n✅ Signal enhanced:")
    print(f"   Action: {enhanced_signal.get('action')}")
    print(f"   Confidence: {enhanced_signal.get('confidence', 0):.2f}%")
    print(f"   Entry Price: ${enhanced_signal.get('entry_price', current_price):.2f}")
    print(f"   Stop Price (enhanced): ${enhanced_signal.get('stop_price', 'N/A')}")
    print(f"   Target Price (enhanced): ${enhanced_signal.get('target_price', 'N/A')}")
    
    enhanced_stop = enhanced_signal.get('stop_price')
    enhanced_target = enhanced_signal.get('target_price')
    
    # Step 5: Compare initial vs enhanced
    print(f"\n{'─'*80}")
    print("STEP 5: Comparison")
    print(f"{'─'*80}")
    
    if initial_stop and enhanced_stop:
        stop_diff = abs(enhanced_stop - initial_stop)
        stop_diff_pct = (stop_diff / current_price) * 100
        print(f"Stop Price:")
        print(f"   Initial: ${initial_stop:.4f}")
        print(f"   Enhanced: ${enhanced_stop:.4f}")
        print(f"   Difference: ${stop_diff:.4f} ({stop_diff_pct:.4f}%)")
        if abs(stop_diff) > 0.01:
            print(f"   ✅ STOP PRICE CHANGED")
        else:
            print(f"   ⚠️  STOP PRICE UNCHANGED")
    
    if initial_target and enhanced_target:
        target_diff = abs(enhanced_target - initial_target)
        target_diff_pct = (target_diff / current_price) * 100
        print(f"\nTarget Price:")
        print(f"   Initial: ${initial_target:.4f}")
        print(f"   Enhanced: ${enhanced_target:.4f}")
        print(f"   Difference: ${target_diff:.4f} ({target_diff_pct:.4f}%)")
        if abs(target_diff) > 0.01:
            print(f"   ✅ TARGET PRICE CHANGED")
        else:
            print(f"   ⚠️  TARGET PRICE UNCHANGED")
    
    # Step 6: Calculate expected adaptive stops
    print(f"\n{'─'*80}")
    print("STEP 6: Expected Adaptive Stops Calculation")
    print(f"{'─'*80}")
    
    action = signal.get('action')
    entry_price = signal.get('entry_price', current_price)
    
    if action == 'BUY':
        expected_stop = entry_price * (1 - (atr_pct * 1.5 / 100))
        expected_target = entry_price * (1 + (atr_pct * 2.5 / 100))
        # Clamp
        expected_stop = max(entry_price * 0.90, expected_stop)
        expected_target = min(entry_price * 1.15, expected_target)
    else:  # SELL
        expected_stop = entry_price * (1 + (atr_pct * 1.5 / 100))
        expected_target = entry_price * (1 - (atr_pct * 2.5 / 100))
        # Clamp
        expected_stop = min(entry_price * 1.10, expected_stop)
        expected_target = max(entry_price * 0.85, expected_target)
    
    print(f"Expected (from ATR calculation):")
    print(f"   Stop: ${expected_stop:.4f}")
    print(f"   Target: ${expected_target:.4f}")
    
    if enhanced_stop:
        stop_match = abs(enhanced_stop - expected_stop) < 0.01
        print(f"   Stop matches expected: {'✅ YES' if stop_match else '❌ NO'}")
    
    if enhanced_target:
        target_match = abs(enhanced_target - expected_target) < 0.01
        print(f"   Target matches expected: {'✅ YES' if target_match else '❌ NO'}")
    
    # Step 7: Position sizing
    print(f"\n{'─'*80}")
    print("STEP 7: Position Sizing")
    print(f"{'─'*80}")
    
    base_capital = 100000.0
    confidence = enhanced_signal.get('confidence', 60.0)
    volatility = indicators.get('volatility', 0.2)
    
    position_size = enhancer.calculate_position_size(
        base_capital, confidence, volatility, symbol
    )
    
    print(f"Base capital: ${base_capital:,.2f}")
    print(f"Confidence: {confidence:.2f}%")
    print(f"Volatility: {volatility:.4f}")
    print(f"Position size: ${position_size:,.2f}")
    print(f"Position %: {(position_size / base_capital) * 100:.2f}%")
    
    # Step 8: Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    
    issues = []
    if initial_stop and enhanced_stop and abs(enhanced_stop - initial_stop) < 0.01:
        issues.append("⚠️  Stop price not changed by enhancement")
    if initial_target and enhanced_target and abs(enhanced_target - initial_target) < 0.01:
        issues.append("⚠️  Target price not changed by enhancement")
    if enhanced_stop and abs(enhanced_stop - expected_stop) > 0.01:
        issues.append("⚠️  Enhanced stop doesn't match expected ATR-based calculation")
    if enhanced_target and abs(enhanced_target - expected_target) > 0.01:
        issues.append("⚠️  Enhanced target doesn't match expected ATR-based calculation")
    
    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("✅ All enhancements appear to be working correctly!")
    
    print(f"\n{'='*80}\n")

def investigate_multiple_signals(symbol: str = "AAPL", num_signals: int = 10):
    """Investigate multiple signals to find patterns"""
    
    print(f"\n{'='*80}")
    print(f"🔍 BATCH INVESTIGATION: {num_signals} signals for {symbol}")
    print(f"{'='*80}\n")
    
    dm = DataManager()
    signal_service = SignalGenerationService()
    signal_generator = HistoricalSignalGenerator(signal_service, dm)
    enhancer = PerformanceEnhancer(
        min_confidence=60.0,
        require_volume_confirmation=False,
        require_trend_filter=False,
        use_adaptive_stops=True,
        use_trailing_stops=True,
        use_position_sizing=True
    )
    
    df = dm.fetch_historical_data(symbol, period="20y")
    if df is None or df.empty:
        print(f"❌ Failed to fetch data")
        return
    
    df = dm._clean_data(df)
    
    stats = {
        'total_signals': 0,
        'signals_enhanced': 0,
        'stops_changed': 0,
        'targets_changed': 0,
        'stops_match_expected': 0,
        'targets_match_expected': 0
    }
    
    # Sample indices across the dataset
    indices = np.linspace(100, len(df) - 100, num_signals, dtype=int)
    
    for idx in indices:
        signal = signal_generator.generate_signal(symbol, df, idx)
        if not signal:
            continue
        
        stats['total_signals'] += 1
        
        current_price = float(df.iloc[idx]['Close'])
        indicators = {
            'sma_20': float(df.iloc[idx]['sma_20']) if 'sma_20' in df.columns and not pd.isna(df.iloc[idx]['sma_20']) else None,
            'sma_50': float(df.iloc[idx]['sma_50']) if 'sma_50' in df.columns and not pd.isna(df.iloc[idx]['sma_50']) else None,
            'rsi': float(df.iloc[idx]['rsi']) if 'rsi' in df.columns and not pd.isna(df.iloc[idx]['rsi']) else None,
            'macd': float(df.iloc[idx]['macd']) if 'macd' in df.columns and not pd.isna(df.iloc[idx]['macd']) else None,
            'macd_signal': float(df.iloc[idx]['macd_signal']) if 'macd_signal' in df.columns and not pd.isna(df.iloc[idx]['macd_signal']) else None,
            'volume_ratio': float(df.iloc[idx]['volume_ratio']) if 'volume_ratio' in df.columns and not pd.isna(df.iloc[idx]['volume_ratio']) else None,
            'volatility': float(df.iloc[idx]['volatility']) if 'volatility' in df.columns and not pd.isna(df.iloc[idx]['volatility']) else 0.2,
            'current_price': current_price
        }
        
        initial_stop = signal.get('stop_price')
        initial_target = signal.get('target_price')
        
        enhanced_signal = enhancer.enhance_signal(signal.copy(), indicators, df, idx)
        
        if not enhanced_signal:
            continue
        
        stats['signals_enhanced'] += 1
        
        enhanced_stop = enhanced_signal.get('stop_price')
        enhanced_target = enhanced_signal.get('target_price')
        
        if initial_stop and enhanced_stop and abs(enhanced_stop - initial_stop) > 0.01:
            stats['stops_changed'] += 1
        
        if initial_target and enhanced_target and abs(enhanced_target - initial_target) > 0.01:
            stats['targets_changed'] += 1
        
        # Check if matches expected
        try:
            historical_data = df.iloc[:idx+1]
            atr = enhancer.calculate_atr(
                historical_data['High'],
                historical_data['Low'],
                historical_data['Close']
            )
            current_atr = atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else current_price * 0.02
            atr_pct = (current_atr / current_price) * 100
            
            action = signal.get('action')
            entry_price = signal.get('entry_price', current_price)
            
            if action == 'BUY':
                expected_stop = entry_price * (1 - (atr_pct * 1.5 / 100))
                expected_target = entry_price * (1 + (atr_pct * 2.5 / 100))
                expected_stop = max(entry_price * 0.90, expected_stop)
                expected_target = min(entry_price * 1.15, expected_target)
            else:
                expected_stop = entry_price * (1 + (atr_pct * 1.5 / 100))
                expected_target = entry_price * (1 - (atr_pct * 2.5 / 100))
                expected_stop = min(entry_price * 1.10, expected_stop)
                expected_target = max(entry_price * 0.85, expected_target)
            
            if enhanced_stop and abs(enhanced_stop - expected_stop) < 0.01:
                stats['stops_match_expected'] += 1
            
            if enhanced_target and abs(enhanced_target - expected_target) < 0.01:
                stats['targets_match_expected'] += 1
        except:
            pass
    
    print(f"\n📊 BATCH STATISTICS:")
    print(f"   Total signals generated: {stats['total_signals']}")
    print(f"   Signals enhanced: {stats['signals_enhanced']}")
    print(f"   Stops changed: {stats['stops_changed']} ({stats['stops_changed']/max(stats['signals_enhanced'],1)*100:.1f}%)")
    print(f"   Targets changed: {stats['targets_changed']} ({stats['targets_changed']/max(stats['signals_enhanced'],1)*100:.1f}%)")
    print(f"   Stops match expected: {stats['stops_match_expected']} ({stats['stops_match_expected']/max(stats['signals_enhanced'],1)*100:.1f}%)")
    print(f"   Targets match expected: {stats['targets_match_expected']} ({stats['targets_match_expected']/max(stats['signals_enhanced'],1)*100:.1f}%)")
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    # Single signal investigation
    investigate_signal_flow("AAPL", 100)
    
    # Batch investigation
    investigate_multiple_signals("AAPL", 10)

