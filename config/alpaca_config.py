from config.secrets import get_secret

class AlpacaConfig:
    """Alpaca Paper Trading configuration"""

    def __init__(self):
        """Load credentials from AWS Secrets Manager"""
        self.secrets = get_secret('alpaca-paper-trading')
        self.key_id = self.secrets['alpaca_key_id']
        self.secret_key = self.secrets['alpaca_secret_key']
        self.base_url = self.secrets['base_url']
        self.environment = 'paper'

    def validate(self):
        """Validate configuration"""
        assert self.key_id, "API Key ID missing"
        assert self.secret_key, "Secret Key missing"
        assert self.base_url, "Base URL missing"
        return True
