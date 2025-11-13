"""
AI Signal Explainer using Claude
PATENT CLAIM: AI-generated reasoning for each signal must be meaningful and non-empty
"""
import os
import logging

logger = logging.getLogger("SignalExplainer")

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

class SignalExplainer:
    """
    Generates AI-powered reasoning for trading signals
    
    PATENT CLAIM: AI-generated reasoning for each signal
    - Must never return None or empty string
    - Must be meaningful (>20 characters)
    - Includes fallback reasoning if LLM fails
    """
    
    def __init__(self):
        self.llm_failure_count = 0
        if ANTHROPIC_AVAILABLE:
            try:
                self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
                self.enabled = bool(os.getenv("ANTHROPIC_API_KEY"))
            except Exception:
                self.client = None
                self.enabled = False
        else:
            self.client = None
            self.enabled = False
    
    def explain_signal(self, signal: dict) -> str:
        """
        Generate human-readable explanation for signal
        
        PATENT CLAIM: AI-generated reasoning - always returns meaningful text
        
        Returns:
            Non-empty reasoning string (minimum 20 characters)
        """
        # Try LLM generation first
        if self.enabled:
            try:
                reasoning = self._generate_llm_reasoning(signal)
                if reasoning and len(reasoning.strip()) >= 20:
                    return reasoning.strip()
                else:
                    logger.warning("LLM returned insufficient reasoning, using fallback")
                    self.llm_failure_count += 1
            except Exception as e:
                logger.warning(f"LLM reasoning generation failed: {e}, using fallback")
                self.llm_failure_count += 1
        
        # Fallback to structured template reasoning
        return self._generate_fallback_reasoning(signal)
    
    def _generate_llm_reasoning(self, signal: dict) -> str:
        """Generate reasoning using LLM (Claude)"""
        prompt = f"""As a trading expert, explain this signal in 2-3 sentences for a trader:

Symbol: {signal.get('symbol', 'UNKNOWN')}
Action: {signal.get('action', 'UNKNOWN')}
Entry: ${signal.get('entry', signal.get('entry_price', 0))}
Stop Loss: ${signal.get('stop_loss', 0)}
Take Profit: ${signal.get('take_profit', signal.get('target_price', 0))}
Confidence: {signal.get('confidence', 0)}%

Explain: 1) Why this signal was generated, 2) What the confidence means, 3) Risk/reward ratio.
Keep it concise and actionable (minimum 20 characters)."""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def _generate_fallback_reasoning(self, signal: dict) -> str:
        """
        Generate fallback reasoning using structured template
        
        PATENT CLAIM: Always produces meaningful, non-generic reasoning
        """
        symbol = signal.get('symbol', 'UNKNOWN')
        action = signal.get('action', 'UNKNOWN')
        confidence = signal.get('confidence', 0)
        entry = signal.get('entry', signal.get('entry_price', 0))
        stop_loss = signal.get('stop_loss', 0)
        take_profit = signal.get('take_profit', signal.get('target_price', 0))
        
        # Extract data sources if available
        sources = signal.get('data_source', 'weighted_consensus')
        sources_count = signal.get('sources_count', signal.get('consensus_agreement', 0))
        
        # Calculate risk/reward ratio
        if stop_loss and take_profit and entry:
            if action.upper() == 'BUY':
                risk = abs(entry - stop_loss)
                reward = abs(take_profit - entry)
            else:  # SELL
                risk = abs(stop_loss - entry)
                reward = abs(entry - take_profit)
            
            if risk > 0:
                rr_ratio = round(reward / risk, 2)
            else:
                rr_ratio = 0
        else:
            rr_ratio = 0
        
        # Build structured reasoning
        reasoning_parts = [
            f"{action} signal generated for {symbol} with {confidence:.1f}% confidence",
            f"based on consensus from {sources_count if sources_count else 'multiple'} data sources",
            f"including {sources.replace('_', ' ').title()}",
        ]
        
        if rr_ratio > 0:
            reasoning_parts.append(f"Risk-reward ratio: {rr_ratio}:1")
        
        # Add confidence interpretation
        if confidence >= 95:
            reasoning_parts.append("Very high confidence indicates strong consensus across all data sources")
        elif confidence >= 90:
            reasoning_parts.append("High confidence suggests reliable signal with good agreement")
        elif confidence >= 85:
            reasoning_parts.append("Moderate-high confidence with solid technical foundation")
        else:
            reasoning_parts.append("Moderate confidence with mixed signals requiring careful risk management")
        
        reasoning = ". ".join(reasoning_parts) + "."
        
        # Ensure minimum length (patent requirement)
        if len(reasoning) < 20:
            reasoning += f" Entry: ${entry:.2f}, Stop: ${stop_loss:.2f}, Target: ${take_profit:.2f}."
        
        return reasoning
    
    def get_llm_failure_rate(self) -> float:
        """Get LLM failure rate for monitoring"""
        # This would need to track total calls to calculate rate
        # For now, just return the count
        return self.llm_failure_count
