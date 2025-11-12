#!/usr/bin/env python3
"""Sonar AI (Perplexity) Data Source - AI Analysis (15% weight)"""
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SonarAI")

class SonarDataSource:
    """
    Perplexity Sonar AI integration for deep analysis
    Weight: 15% in Alpine Analytics consensus
    """
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        
    def fetch_ai_analysis(self, symbol):
        """Get AI-powered analysis for a symbol"""
        try:
            prompt = f"""Analyze {symbol} for trading:
            
            Consider:
            - Technical indicators (RSI, MACD, moving averages)
            - Recent price action and volume
            - Market sentiment
            - News and fundamentals
            
            Provide:
            1. Signal direction (LONG/SHORT/NEUTRAL)
            2. Confidence (0-100)
            3. Brief reasoning (1-2 sentences)
            
            Format: SIGNAL: [direction] | CONFIDENCE: [0-100] | REASONING: [text]"""
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'llama-3.1-sonar-small-128k-online',
                'messages': [
                    {'role': 'system', 'content': 'You are a professional trading analyst providing concise signal analysis.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.2,
                'max_tokens': 200
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                analysis = data['choices'][0]['message']['content']
                logger.info(f"✅ Sonar AI: {symbol} analysis received")
                return analysis
            else:
                logger.error(f"Sonar API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Sonar AI error for {symbol}: {e}")
            return None
    
    def generate_signal(self, analysis, symbol):
        """Parse AI analysis into structured signal"""
        if not analysis:
            return None
        
        try:
            # Parse the analysis
            analysis_lower = analysis.lower()
            
            # Extract direction
            if 'signal: long' in analysis_lower or 'bullish' in analysis_lower:
                direction = 'LONG'
            elif 'signal: short' in analysis_lower or 'bearish' in analysis_lower:
                direction = 'SHORT'
            else:
                direction = 'NEUTRAL'
            
            # Extract confidence (look for numbers)
            confidence = 75.0  # Default
            import re
            conf_match = re.search(r'confidence[:\s]+(\d+)', analysis_lower)
            if conf_match:
                confidence = float(conf_match.group(1))
            
            # Extract reasoning
            reasoning_match = re.search(r'reasoning[:\s]+(.+?)(?:\n|$)', analysis, re.IGNORECASE)
            reasoning = reasoning_match.group(1).strip() if reasoning_match else "AI analysis completed"
            
            return {
                'direction': direction,
                'confidence': round(confidence, 2),
                'source': 'sonar_ai',
                'weight': 0.15,
                'reasoning': reasoning[:200]  # Limit to 200 chars
            }
            
        except Exception as e:
            logger.error(f"Signal parsing error: {e}")
            return None
