#!/usr/bin/env python3
"""
Signal Generation Tracer
Advanced logging and tracing for signal generation pipeline
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from collections import defaultdict
import traceback

try:
    import numpy as np
except ImportError:
    np = None

logger = logging.getLogger(__name__)

class SignalTracer:
    """Advanced tracing for signal generation pipeline"""
    
    def __init__(self, enable_tracing: bool = True, log_file: Optional[str] = None):
        self.enable_tracing = enable_tracing
        self.traces: List[Dict] = []
        self.stats = defaultdict(int)
        self.log_file = log_file
        
        if log_file:
            self.log_path = Path(log_file)
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            self.log_path = None
    
    def trace(
        self,
        stage: str,
        symbol: str,
        data: Dict[str, Any],
        success: bool = True,
        error: Optional[str] = None
    ):
        """Trace a stage in signal generation"""
        if not self.enable_tracing:
            return
        
        trace_entry = {
            'timestamp': datetime.now().isoformat(),
            'stage': stage,
            'symbol': symbol,
            'data': data,
            'success': success,
            'error': error
        }
        
        self.traces.append(trace_entry)
        self.stats[stage] += 1
        
        # Log to file if configured
        if self.log_path:
            try:
                # Convert data to JSON-serializable format
                serializable_entry = self._make_json_serializable(trace_entry)
                with open(self.log_path, 'a') as f:
                    f.write(json.dumps(serializable_entry) + '\n')
            except Exception as e:
                logger.warning(f"Failed to write trace to file: {e}")
    
    def _make_json_serializable(self, obj):
        """Convert object to JSON-serializable format"""
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, (bool, int, float, str, type(None))):
            return obj
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return str(obj)
        
        # Log to console
        if error:
            logger.error(f"[TRACE] {stage} | {symbol} | ERROR: {error}")
        elif not success:
            logger.warning(f"[TRACE] {stage} | {symbol} | FAILED")
        else:
            logger.debug(f"[TRACE] {stage} | {symbol} | SUCCESS")
    
    def trace_indicator_calculation(
        self,
        symbol: str,
        data_len: int,
        indicators: Dict,
        success: bool
    ):
        """Trace indicator calculation"""
        self.trace(
            'indicator_calculation',
            symbol,
            {
                'data_length': data_len,
                'indicators_found': list(indicators.keys()) if indicators else [],
                'sma_20': indicators.get('sma_20'),
                'sma_50': indicators.get('sma_50'),
                'rsi': indicators.get('rsi'),
                'macd': indicators.get('macd'),
                'has_macd_signal': indicators.get('macd_signal') is not None
            },
            success=success,
            error=None if success else "No indicators calculated"
        )
    
    def trace_signal_generation(
        self,
        symbol: str,
        indicators: Dict,
        signals: List[str],
        confidences: List[float],
        final_signal: Optional[Dict],
        min_confidence: float
    ):
        """Trace signal generation from indicators"""
        self.trace(
            'signal_generation',
            symbol,
            {
                'indicators_available': list(indicators.keys()),
                'signals_generated': signals,
                'confidences': confidences,
                'final_action': final_signal.get('action') if final_signal else None,
                'final_confidence': final_signal.get('confidence') if final_signal else None,
                'min_confidence_threshold': min_confidence,
                'above_threshold': final_signal.get('confidence', 0) >= min_confidence if final_signal else False
            },
            success=final_signal is not None,
            error=None if final_signal else f"Signal confidence {final_signal.get('confidence', 0) if final_signal else 0} < {min_confidence}"
        )
    
    def trace_position_entry(
        self,
        symbol: str,
        signal: Dict,
        current_price: float,
        position_opened: bool,
        reason: Optional[str] = None
    ):
        """Trace position entry attempt"""
        self.trace(
            'position_entry',
            symbol,
            {
                'action': signal.get('action'),
                'confidence': signal.get('confidence'),
                'current_price': current_price,
                'entry_price': signal.get('entry_price'),
                'target_price': signal.get('target_price'),
                'stop_price': signal.get('stop_price')
            },
            success=position_opened,
            error=None if position_opened else reason
        )
    
    def get_stats(self) -> Dict:
        """Get tracing statistics"""
        return {
            'total_traces': len(self.traces),
            'stage_counts': dict(self.stats),
            'recent_traces': self.traces[-10:] if self.traces else []
        }
    
    def get_traces_for_symbol(self, symbol: str) -> List[Dict]:
        """Get all traces for a specific symbol"""
        return [t for t in self.traces if t.get('symbol') == symbol]
    
    def clear(self):
        """Clear all traces"""
        self.traces.clear()
        self.stats.clear()
    
    def export_report(self, output_file: str):
        """Export trace report"""
        report = {
            'generated': datetime.now().isoformat(),
            'stats': self.get_stats(),
            'traces': self.traces
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Trace report exported to: {output_file}")

# Global tracer instance
_global_tracer: Optional[SignalTracer] = None

def get_tracer() -> SignalTracer:
    """Get global tracer instance"""
    global _global_tracer
    if _global_tracer is None:
        _global_tracer = SignalTracer(
            enable_tracing=True,
            log_file='argo/reports/signal_traces.jsonl'
        )
    return _global_tracer

