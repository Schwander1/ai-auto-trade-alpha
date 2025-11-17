import os
import sys
import requests
from pathlib import Path
from anthropic import Anthropic

# Use Argo-specific secrets manager
try:
    from argo.utils.secrets_manager import get_secret
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False

class PremiumAPIs:
    """Integration with all premium data sources"""
    
    def __init__(self):
        # Try AWS Secrets Manager first, fallback to environment variables
        service = "argo"
        
        if SECRETS_MANAGER_AVAILABLE:
            try:
                self.alpha_vantage_key = get_secret("alpha-vantage-api-key", service=service) or os.getenv('ALPHA_VANTAGE_API_KEY')
                self.anthropic_key = get_secret("anthropic-api-key", service=service) or os.getenv('ANTHROPIC_API_KEY')
                self.perplexity_key = get_secret("perplexity-api-key", service=service) or os.getenv('PERPLEXITY_API_KEY')
                self.xai_key = get_secret("xai-api-key", service=service) or os.getenv('XAI_API_KEY')
            except Exception:
                # Fallback to environment variables
                self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
                self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
                self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
                self.xai_key = os.getenv('XAI_API_KEY')
        else:
            self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
            self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
            self.xai_key = os.getenv('XAI_API_KEY')
        
    def get_fundamental_data(self, symbol):
        """Alpha Vantage - Company fundamentals"""
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol,
            'apikey': self.alpha_vantage_key
        }
        response = requests.get(url, params=params)
        return response.json()
        
    def analyze_sentiment_claude(self, text):
        """Anthropic Claude - Sentiment analysis"""
        if not self.anthropic_key:
            return None
            
        client = Anthropic(api_key=self.anthropic_key)
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"Analyze market sentiment: {text}"
            }]
        )
        return message.content
        
    def research_news(self, query):
        """Perplexity Sonar - News research"""
        if not self.perplexity_key:
            return None
            
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "sonar",
            "messages": [{"role": "user", "content": query}]
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()
