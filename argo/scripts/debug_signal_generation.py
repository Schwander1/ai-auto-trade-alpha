#!/usr/bin/env python3
"""
Debug Signal Generation
Interactive debugging tool for signal generation pipeline
"""
import sys
import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from argo.backtest.historical_signal_generator import HistoricalSignalGenerator
from argo.backtest.data_manager import DataManager
from argo.core.signal_generation_service import SignalGenerationService
from argo.backtest.signal_tracer import get_tracer
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_signal_pipeline(symbol: str = 'AAPL', index: int = 200):
    """Debug the entire signal generation pipeline"""
    print("\n" + "="*80)
    print(f"🔍 DEBUGGING SIGNAL GENERATION PIPELINE")
    print("="*80)
    print(f"Symbol: {symbol}")
    print(f"Index: {index}")
    print("="*80)
    
    tracer = get_tracer()
    tracer.clear()
    
    try:
        # Initialize components
        dm = DataManager(use_polars=True)
        signal_service = SignalGenerationService()
        generator = HistoricalSignalGenerator(signal_service, dm)
        
        # Get data - try 20y first (we have cached data for this)
        print(f"\n📊 Step 1: Loading data...")
        df = dm.fetch_historical_data(symbol, period="20y")
        if df is None:
            # Try 5y as fallback
            print("   Trying 5y period...")
            df = dm.fetch_historical_data(symbol, period="5y")
        if df is None:
            print("❌ No data available")
            return
        
        # Convert to pandas
        try:
            import polars as pl
            if isinstance(df, pl.DataFrame):
                df = df.to_pandas()
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'])
                    df = df.set_index('Date')
        except:
            import pandas as pd
        
        if len(df) < index + 1:
            print(f"❌ Not enough data: {len(df)} < {index + 1}")
            return
        
        print(f"✅ Data loaded: {len(df)} rows")
        print(f"   Date range: {df.index[0]} to {df.index[-1]}")
        
        # Get historical data up to index
        historical_df = df.iloc[:index+1].copy()
        current_date = df.index[index]
        current_price = float(df.iloc[index]['Close'])
        
        print(f"\n📈 Step 2: Calculating indicators...")
        if hasattr(current_date, 'date'):
            print(f"   Current date: {current_date.date()}")
        else:
            print(f"   Current date: {current_date}")
        print(f"   Current price: ${current_price:.2f}")
        print(f"   Historical data length: {len(historical_df)}")
        
        indicators = generator._calculate_indicators(historical_df)
        tracer.trace_indicator_calculation(symbol, len(historical_df), indicators, bool(indicators))
        
        if not indicators:
            print("❌ No indicators calculated!")
            return
        
        print(f"✅ Indicators calculated:")
        for key, value in indicators.items():
            if value is not None:
                if isinstance(value, float):
                    print(f"   {key}: {value:.4f}")
                else:
                    print(f"   {key}: {value}")
        
        # Generate signal
        print(f"\n🎯 Step 3: Generating signal from indicators...")
        signal = generator._generate_signal_from_indicators(
            symbol,
            current_price,
            indicators,
            historical_df
        )
        
        if signal:
            print(f"✅ Signal generated:")
            print(f"   Action: {signal.get('action')}")
            print(f"   Confidence: {signal.get('confidence', 0):.2f}%")
            print(f"   Direction: {signal.get('direction')}")
            print(f"   Target: ${signal.get('target_price', 0):.2f}")
            print(f"   Stop: ${signal.get('stop_price', 0):.2f}")
        else:
            print(f"❌ No signal generated!")
            print(f"   This is the problem - need to investigate why")
        
        # Export trace report
        tracer.export_report('argo/reports/signal_debug_report.json')
        print(f"\n📁 Trace report saved to: argo/reports/signal_debug_report.json")
        
        # Show stats
        stats = tracer.get_stats()
        print(f"\n📊 Tracing Statistics:")
        print(f"   Total traces: {stats['total_traces']}")
        print(f"   Stage counts: {stats['stage_counts']}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'AAPL'
    index = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    
    asyncio.run(debug_signal_pipeline(symbol, index))

