"""Signal Generator with AI Explanations"""
import asyncio
import random
from datetime import datetime
from typing import Dict, List
from argo.ai.explainer import SignalExplainer

# 🆕 COMPLIANCE LOGGING: Import compliance logger  
try:
    import sys
    import os
    # Add parent directory to path to import compliance module
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from compliance.signal_logger import log_signal_with_compliance
    COMPLIANCE_ENABLED = True
except ImportError:
    print("⚠️  Compliance logging not available (optional)")
    COMPLIANCE_ENABLED = False

class SignalGenerator:
    def __init__(self):
        self.symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'MATIC/USD']
        self.explainer = SignalExplainer()
    
    async def generate_signal(self, premium: bool = False) -> Dict:
        symbol = random.choice(self.symbols)
        
        if premium:
            confidence = random.uniform(95.0, 99.5)
            signal_type = "PREMIUM"
        else:
            confidence = random.uniform(75.0, 94.9)
            signal_type = "STANDARD"
        
        action = random.choice(['BUY', 'SELL'])
        
        if 'BTC' in symbol:
            entry_price = random.uniform(30000, 50000)
        elif 'ETH' in symbol:
            entry_price = random.uniform(2000, 3000)
        else:
            entry_price = random.uniform(100, 500)
        
        signal = {
            'id': f"sig_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
            'symbol': symbol,
            'action': action,
            'entry': round(entry_price, 2),
            'stop_loss': round(entry_price * 0.99, 2) if action == 'BUY' else round(entry_price * 1.01, 2),
            'take_profit': round(entry_price * 1.02, 2) if action == 'BUY' else round(entry_price * 0.98, 2),
            'confidence': round(confidence, 2),
            'type': signal_type,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
        }
        
        # Add AI explanation
        signal['explanation'] = self.explainer.explain_signal(signal)
        
        # Calculate risk-reward ratio
        if action == 'BUY':
            risk = entry_price - signal['stop_loss']
            reward = signal['take_profit'] - entry_price
        else:
            risk = signal['stop_loss'] - entry_price
            reward = entry_price - signal['take_profit']
        
        signal['risk_reward_ratio'] = round(reward / risk, 2) if risk > 0 else 0
        
        # 🆕 COMPLIANCE LOGGING: Log signal with SHA-256 and S3 backup
        if COMPLIANCE_ENABLED:
            try:
                compliance_data = {
                    'symbol': signal['symbol'],
                    'direction': signal['action'],
                    'entry': signal['entry'],
                    'exit': signal['take_profit'],
                    'stop': signal['stop_loss'],
                    'confidence': signal['confidence'],
                    'regime': signal_type,
                    'timestamp': signal['timestamp']
                }
                log_signal_with_compliance(compliance_data)
            except Exception as e:
                print(f"⚠️  Compliance logging failed (non-critical): {e}")
        
        return signal
    
    async def get_latest(self, limit: int = 10, premium_only: bool = False) -> List[Dict]:
        signals = []
        for _ in range(limit):
            is_premium = premium_only or (random.random() > 0.5)
            signal = await self.generate_signal(premium=is_premium)
            signals.append(signal)
            await asyncio.sleep(0.01)
        return signals
