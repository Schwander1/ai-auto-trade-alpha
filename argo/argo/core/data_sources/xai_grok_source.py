#!/usr/bin/env python3
"""xAI Grok Data Source - AI Sentiment Analysis (20% weight)"""
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("xAIGrok")

class XAIGrokDataSource:
    """
    xAI Grok integration for sentiment analysis
    Weight: 20% in Alpine Analytics consensus
    NOTE: Requires xAI API key to be configured
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.x.ai/v1/chat/completions"  # Placeholder URL
        self.enabled = bool(api_key)
        
        if not self.enabled:
            logger.warning("⚠️  xAI Grok API key not configured - using fallback sentiment")
    
    async def fetch_sentiment(self, symbol):
        """Get AI-powered sentiment analysis"""
        if not self.enabled:
            # Fallback: Return neutral sentiment
            return {
                'sentiment': 'neutral',
                'score': 0.5,
                'source': 'fallback'
            }
        
        try:
            prompt = f"""Analyze market sentiment for {symbol}:
            
            Consider recent news, social media, and market trends.
            
            Provide:
            1. Sentiment (bullish/bearish/neutral)
            2. Confidence score (0-100)
            3. Key reasoning
            
            Format: SENTIMENT: [sentiment] | SCORE: [0-100] | REASON: [text]"""
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'grok-beta',
                'messages': [
                    {'role': 'system', 'content': 'You are a market sentiment analyst.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.2,
                'max_tokens': 150
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                analysis = data['choices'][0]['message']['content']
                logger.info(f"✅ xAI Grok: {symbol} sentiment received")
                return analysis
            else:
                logger.error(f"xAI API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"xAI Grok error for {symbol}: {e}")
            return None
    
    def generate_signal(self, sentiment_data, symbol):
        """Parse sentiment into trading signal"""
        if not sentiment_data:
            return None
        
        try:
            # If using fallback, return low-confidence neutral
            if isinstance(sentiment_data, dict) and sentiment_data.get('source') == 'fallback':
                return {
                    'direction': 'NEUTRAL',
                    'confidence': 50.0,
                    'source': 'xai_grok_fallback',
                    'weight': 0.20,
                    'note': 'Using fallback sentiment - configure xAI API key'
                }
            
            # Parse actual sentiment analysis
            analysis_lower = str(sentiment_data).lower()
            
            if 'bullish' in analysis_lower or 'sentiment: bullish' in analysis_lower:
                direction = 'LONG'
                confidence = 75.0
            elif 'bearish' in analysis_lower or 'sentiment: bearish' in analysis_lower:
                direction = 'SHORT'
                confidence = 75.0
            else:
                direction = 'NEUTRAL'
                confidence = 60.0
            
            # Extract confidence score if present
            import re
            score_match = re.search(r'score[:\s]+(\d+)', analysis_lower)
            if score_match:
                confidence = float(score_match.group(1))
            
            return {
                'direction': direction,
                'confidence': round(confidence, 2),
                'source': 'xai_grok',
                'weight': 0.20
            }
            
        except Exception as e:
            logger.error(f"Signal parsing error: {e}")
            return None
