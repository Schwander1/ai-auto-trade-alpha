#!/usr/bin/env python3
"""
Configuration Validator
Validates configuration files and settings for production readiness
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ValidationError:
    """Configuration validation error"""
    field: str
    message: str
    severity: str  # 'error', 'warning', 'info'

class ConfigValidator:
    """Validate configuration files"""
    
    REQUIRED_FIELDS = {
        'trading': ['position_size_pct', 'min_confidence'],
        'alpaca': ['api_key', 'secret_key'],
    }
    
    OPTIONAL_FIELDS = {
        'trading': ['max_position_size_pct', 'stop_loss', 'take_profit', 'daily_loss_limit_pct'],
        'prop_firm': ['enabled', 'risk_limits', 'symbols'],
    }
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
    
    def validate_config(self, config: Dict, config_path: Optional[Path] = None) -> bool:
        """
        Validate configuration
        
        Returns:
            True if valid, False otherwise
        """
        self.errors.clear()
        self.warnings.clear()
        
        # Validate required sections
        self._validate_sections(config)
        
        # Validate trading config
        if 'trading' in config:
            self._validate_trading_config(config['trading'])
        
        # Validate Alpaca config
        if 'alpaca' in config:
            self._validate_alpaca_config(config['alpaca'])
        
        # Validate prop firm config
        if 'prop_firm' in config:
            self._validate_prop_firm_config(config['prop_firm'])
        
        # Validate data sources
        if 'data_sources' in config:
            self._validate_data_sources_config(config['data_sources'])
        
        # Report results
        self._report_validation_results(config_path)
        
        return len(self.errors) == 0
    
    def _validate_sections(self, config: Dict):
        """Validate required sections exist"""
        required_sections = ['trading', 'alpaca']
        
        for section in required_sections:
            if section not in config:
                self.errors.append(ValidationError(
                    field=section,
                    message=f"Required section '{section}' is missing",
                    severity='error'
                ))
    
    def _validate_trading_config(self, trading_config: Dict):
        """Validate trading configuration"""
        required_fields = ['position_size_pct', 'min_confidence']
        
        for field in required_fields:
            if field not in trading_config:
                self.errors.append(ValidationError(
                    field=f'trading.{field}',
                    message=f"Required field 'trading.{field}' is missing",
                    severity='error'
                ))
        
        # Validate position size
        if 'position_size_pct' in trading_config:
            position_size = trading_config['position_size_pct']
            if not isinstance(position_size, (int, float)) or position_size <= 0 or position_size > 100:
                self.errors.append(ValidationError(
                    field='trading.position_size_pct',
                    message=f"Invalid position_size_pct: {position_size}. Must be between 0 and 100",
                    severity='error'
                ))
        
        # Validate confidence threshold
        if 'min_confidence' in trading_config:
            confidence = trading_config['min_confidence']
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 100:
                self.errors.append(ValidationError(
                    field='trading.min_confidence',
                    message=f"Invalid min_confidence: {confidence}. Must be between 0 and 100",
                    severity='error'
                ))
        
        # Validate daily loss limit
        if 'daily_loss_limit_pct' in trading_config:
            daily_limit = trading_config['daily_loss_limit_pct']
            if not isinstance(daily_limit, (int, float)) or daily_limit <= 0 or daily_limit > 100:
                self.warnings.append(ValidationError(
                    field='trading.daily_loss_limit_pct',
                    message=f"Unusual daily_loss_limit_pct: {daily_limit}. Typical range is 1-10%",
                    severity='warning'
                ))
    
    def _validate_alpaca_config(self, alpaca_config: Dict):
        """Validate Alpaca configuration"""
        # Check if it's a dict of accounts or single account
        if isinstance(alpaca_config, dict):
            # Check for account-specific configs
            account_keys = ['dev', 'production', 'prop_firm_test']
            has_accounts = any(key in alpaca_config for key in account_keys)
            
            if has_accounts:
                # Validate each account
                for account_name, account_config in alpaca_config.items():
                    if isinstance(account_config, dict):
                        self._validate_alpaca_account(account_config, f'alpaca.{account_name}')
            else:
                # Single account config
                self._validate_alpaca_account(alpaca_config, 'alpaca')
    
    def _validate_alpaca_account(self, account_config: Dict, prefix: str):
        """Validate a single Alpaca account configuration"""
        required_fields = ['api_key', 'secret_key']
        
        for field in required_fields:
            if field not in account_config:
                self.errors.append(ValidationError(
                    field=f'{prefix}.{field}',
                    message=f"Required field '{prefix}.{field}' is missing",
                    severity='error'
                ))
            elif not account_config[field] or account_config[field].strip() == '':
                self.errors.append(ValidationError(
                    field=f'{prefix}.{field}',
                    message=f"Field '{prefix}.{field}' is empty",
                    severity='error'
                ))
    
    def _validate_prop_firm_config(self, prop_firm_config: Dict):
        """Validate prop firm configuration"""
        if prop_firm_config.get('enabled', False):
            # Prop firm is enabled, validate risk limits
            risk_limits = prop_firm_config.get('risk_limits', {})
            
            if not risk_limits:
                self.errors.append(ValidationError(
                    field='prop_firm.risk_limits',
                    message="Prop firm is enabled but risk_limits are not configured",
                    severity='error'
                ))
                return
            
            # Validate risk limits
            required_limits = ['max_drawdown_pct', 'daily_loss_limit_pct', 'max_position_size_pct', 'min_confidence']
            
            for limit in required_limits:
                if limit not in risk_limits:
                    self.errors.append(ValidationError(
                        field=f'prop_firm.risk_limits.{limit}',
                        message=f"Required prop firm risk limit '{limit}' is missing",
                        severity='error'
                    ))
            
            # Validate max drawdown
            if 'max_drawdown_pct' in risk_limits:
                max_dd = risk_limits['max_drawdown_pct']
                if max_dd > 2.5:
                    self.warnings.append(ValidationError(
                        field='prop_firm.risk_limits.max_drawdown_pct',
                        message=f"Max drawdown {max_dd}% exceeds typical prop firm limit of 2.5%",
                        severity='warning'
                    ))
    
    def _validate_data_sources_config(self, data_sources_config: Dict):
        """Validate data sources configuration"""
        # Check weights sum to approximately 1.0
        if 'weights' in data_sources_config:
            weights = data_sources_config['weights']
            total_weight = sum(weights.values())
            
            if abs(total_weight - 1.0) > 0.05:  # 5% tolerance
                self.warnings.append(ValidationError(
                    field='data_sources.weights',
                    message=f"Data source weights sum to {total_weight:.2f}, expected ~1.0",
                    severity='warning'
                ))
    
    def _report_validation_results(self, config_path: Optional[Path] = None):
        """Report validation results"""
        config_name = str(config_path) if config_path else "configuration"
        
        if self.errors:
            logger.error(f"❌ Configuration validation failed for {config_name}")
            for error in self.errors:
                logger.error(f"   ERROR: {error.field} - {error.message}")
        else:
            logger.info(f"✅ Configuration validation passed for {config_name}")
        
        if self.warnings:
            for warning in self.warnings:
                logger.warning(f"   WARNING: {warning.field} - {warning.message}")
    
    def get_validation_report(self) -> Dict:
        """Get validation report as dictionary"""
        return {
            'valid': len(self.errors) == 0,
            'errors': [
                {
                    'field': e.field,
                    'message': e.message,
                    'severity': e.severity
                }
                for e in self.errors
            ],
            'warnings': [
                {
                    'field': w.field,
                    'message': w.message,
                    'severity': w.severity
                }
                for w in self.warnings
            ]
        }

def validate_config_file(config_path: Path) -> bool:
    """Validate a configuration file"""
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        validator = ConfigValidator()
        return validator.validate_config(config, config_path)
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in {config_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error validating {config_path}: {e}")
        return False

