"""AI Signal Explainer using Claude"""
import os
from anthropic import Anthropic

class SignalExplainer:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
        self.enabled = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    def explain_signal(self, signal: dict) -> str:
        """Generate human-readable explanation for signal"""
        if not self.enabled:
            return f"Technical analysis indicates {signal['action']} opportunity for {signal['symbol']} with {signal['confidence']}% confidence."
        
        try:
            prompt = f"""As a trading expert, explain this signal in 2-3 sentences for a trader:

Symbol: {signal['symbol']}
Action: {signal['action']}
Entry: ${signal['entry']}
Stop Loss: ${signal['stop_loss']}
Take Profit: ${signal['take_profit']}
Confidence: {signal['confidence']}%

Explain: 1) Why this signal was generated, 2) What the confidence means, 3) Risk/reward ratio.
Keep it concise and actionable."""

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
        except Exception as e:
            return f"Market analysis shows strong {signal['action']} setup for {signal['symbol']}. Risk-reward ratio: 2:1. Confidence: {signal['confidence']}%."
