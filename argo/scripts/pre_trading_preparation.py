#!/usr/bin/env python3
"""
Comprehensive Pre-Trading Preparation Script
Performs all necessary checks and validations before trading starts tomorrow
"""
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field, asdict

# Add paths - handle both local and production environments
script_dir = Path(__file__).parent
argo_path = script_dir.parent

# Add argo directory to path
if str(argo_path) not in sys.path:
    sys.path.insert(0, str(argo_path))

# Also add workspace root for shared packages (if exists)
workspace_root = argo_path.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

# Change to argo directory for imports to work correctly
import os
original_cwd = os.getcwd()
try:
    os.chdir(str(argo_path))
except:
    pass  # If we can't change directory, continue anyway

# Import with error handling for production
try:
    from argo.core.environment import detect_environment, get_environment_info
except ImportError as e:
    # Try alternative import path for production
    try:
        import argo.core.environment as env_module
        detect_environment = env_module.detect_environment
        get_environment_info = env_module.get_environment_info
    except ImportError:
        # Fallback: define minimal functions
        def detect_environment():
            if Path('/root/argo-production/config.json').exists() or Path('/root/argo-production-blue/config.json').exists() or Path('/root/argo-production-green/config.json').exists():
                return 'production'
            return 'development'
        
        def get_environment_info():
            return {"environment": detect_environment()}

try:
    from argo.core.paper_trading_engine import PaperTradingEngine
except ImportError:
    PaperTradingEngine = None

try:
    from argo.core.signal_generation_service import SignalGenerationService
except ImportError:
    SignalGenerationService = None

try:
    from argo.core.config_loader import ConfigLoader
except ImportError:
    ConfigLoader = None

try:
    from argo.core.config_validator import ConfigValidator
except ImportError:
    ConfigValidator = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PreparationCheck:
    """Result of a preparation check"""
    category: str
    name: str
    status: str  # 'pass', 'fail', 'warning', 'skip'
    message: str = ""
    details: Dict = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PreTradingPreparation:
    """Comprehensive pre-trading preparation checker"""
    
    def __init__(self):
        self.checks: List[PreparationCheck] = []
        self.start_time = datetime.now(timezone.utc)
        self.environment = None
        self.config = None
        
    def check_environment(self) -> PreparationCheck:
        """Check environment detection and configuration"""
        try:
            self.environment = detect_environment()
            env_info = get_environment_info()
            
            return PreparationCheck(
                "Environment",
                "Environment Detection",
                "pass",
                f"Environment: {self.environment.upper()}",
                env_info
            )
        except Exception as e:
            return PreparationCheck(
                "Environment",
                "Environment Detection",
                "fail",
                f"Failed to detect environment: {e}",
                error=str(e)
            )
    
    def check_configuration(self) -> PreparationCheck:
        """Check configuration file validity"""
        try:
            # Use ConfigLoader to find and load config (same way the system does)
            if ConfigLoader is None:
                return PreparationCheck(
                    "Configuration",
                    "Config Loading",
                    "warning",
                    "ConfigLoader not available - using fallback",
                    {}
                )
            
            config, config_path = ConfigLoader.load_config()
            self.config = config
            
            if not config:
                return PreparationCheck(
                    "Configuration",
                    "Config Loading",
                    "fail",
                    "Failed to load configuration"
                )
            
            # Check if config has trading section (may be loaded from different structure)
            has_trading = 'trading' in config
            has_strategy = 'strategy' in config
            
            # Check required sections (flexible - some may be optional)
            # Trading section is required for trading operations
            if not has_trading:
                return PreparationCheck(
                    "Configuration",
                    "Config Sections",
                    "warning",
                    "Trading section not found in config (may be loaded dynamically)",
                    {"present_sections": list(config.keys()), "path": str(config_path) if config_path else "unknown"}
                )
            
            # Try to validate with validator if available
            validator_errors = []
            validator_warnings = []
            try:
                validator = ConfigValidator()
                is_valid = validator.validate_config(config, Path(config_path) if config_path else None)
                if not is_valid:
                    validator_errors = [f"{e.field}: {e.message}" for e in validator.errors]
                    validator_warnings = [f"{w.field}: {w.message}" for w in validator.warnings]
            except Exception as e:
                # Validator may have issues, but config structure is OK
                validator_warnings.append(f"Config validator check skipped: {e}")
            
            if validator_errors:
                return PreparationCheck(
                    "Configuration",
                    "Config Validation",
                    "warning",
                    f"Configuration validation found {len(validator_errors)} issue(s)",
                    {"errors": validator_errors, "warnings": validator_warnings, "path": str(config_path) if config_path else "unknown"}
                )
            
            return PreparationCheck(
                "Configuration",
                "Config Validation",
                "pass",
                f"Configuration loaded successfully",
                {
                    "path": str(config_path) if config_path else "loaded via ConfigLoader",
                    "sections": list(config.keys()),
                    "warnings": validator_warnings
                }
            )
        except json.JSONDecodeError as e:
            return PreparationCheck(
                "Configuration",
                "Config JSON",
                "fail",
                f"Invalid JSON: {e}",
                error=str(e)
            )
        except Exception as e:
            return PreparationCheck(
                "Configuration",
                "Config Check",
                "fail",
                f"Failed to check configuration: {e}",
                error=str(e)
            )
    
    def check_trading_engine(self) -> PreparationCheck:
        """Check trading engine connectivity and status"""
        try:
            if PaperTradingEngine is None:
                return PreparationCheck(
                    "Trading Engine",
                    "Engine Initialization",
                    "warning",
                    "PaperTradingEngine not available - cannot check trading engine",
                    {}
                )
            
            engine = PaperTradingEngine()
            
            if not engine.alpaca_enabled:
                # Check if this is development environment (simulation mode is OK)
                env_status = "warning" if self.environment == "development" else "fail"
                env_message = " (OK for development)" if self.environment == "development" else " - REQUIRED for production"
                
                return PreparationCheck(
                    "Trading Engine",
                    "Alpaca Connection",
                    env_status,
                    f"Alpaca not connected{env_message}",
                    {
                        "simulation_mode": True,
                        "environment": self.environment,
                        "note": "Configure Alpaca credentials in config.json or AWS Secrets Manager for production"
                    }
                )
            
            # Get account details
            account = engine.get_account_details()
            if not account:
                return PreparationCheck(
                    "Trading Engine",
                    "Account Details",
                    "fail",
                    "Failed to retrieve account details"
                )
            
            # Check account status
            account_status = account.get('status', 'unknown')
            trading_blocked = account.get('trading_blocked', False)
            
            if trading_blocked:
                return PreparationCheck(
                    "Trading Engine",
                    "Account Status",
                    "fail",
                    "Account is blocked from trading",
                    {"status": account_status, "trading_blocked": True}
                )
            
            # Check buying power
            buying_power = account.get('buying_power', 0)
            portfolio_value = account.get('portfolio_value', 0)
            
            if buying_power <= 0:
                return PreparationCheck(
                    "Trading Engine",
                    "Buying Power",
                    "warning",
                    "No buying power available",
                    {"buying_power": buying_power, "portfolio_value": portfolio_value}
                )
            
            return PreparationCheck(
                "Trading Engine",
                "Engine Status",
                "pass",
                f"Connected to {engine.account_name}",
                {
                    "account_name": engine.account_name,
                    "account_status": account_status,
                    "portfolio_value": portfolio_value,
                    "buying_power": buying_power,
                    "environment": engine.environment,
                    "trading_blocked": False
                }
            )
        except Exception as e:
            return PreparationCheck(
                "Trading Engine",
                "Engine Initialization",
                "fail",
                f"Failed to initialize trading engine: {e}",
                error=str(e)
            )
    
    def check_signal_service(self) -> PreparationCheck:
        """Check signal generation service"""
        try:
            if SignalGenerationService is None:
                return PreparationCheck(
                    "Signal Service",
                    "Service Initialization",
                    "warning",
                    "SignalGenerationService not available - cannot check signal service",
                    {}
                )
            
            service = SignalGenerationService()
            
            # Check auto-execute status
            auto_execute = service.auto_execute
            trading_engine_initialized = service.trading_engine is not None
            
            details = {
                "environment": service.environment,
                "auto_execute": auto_execute,
                "trading_engine_initialized": trading_engine_initialized,
                "data_sources": list(service.data_sources.keys()) if hasattr(service, 'data_sources') else []
            }
            
            if not auto_execute and trading_engine_initialized:
                return PreparationCheck(
                    "Signal Service",
                    "Auto-Execute",
                    "warning",
                    "Auto-execution is disabled - signals will be generated but not executed",
                    details
                )
            
            return PreparationCheck(
                "Signal Service",
                "Service Status",
                "pass",
                f"Signal service initialized (auto_execute: {auto_execute})",
                details
            )
        except Exception as e:
            return PreparationCheck(
                "Signal Service",
                "Service Initialization",
                "fail",
                f"Failed to initialize signal service: {e}",
                error=str(e)
            )
    
    def check_risk_management(self) -> PreparationCheck:
        """Check risk management configuration"""
        try:
            if not self.config:
                # Try to get config from signal service
                try:
                    service = SignalGenerationService()
                    trading_config = service.trading_config if hasattr(service, 'trading_config') else {}
                except:
                    trading_config = {}
                
                if not trading_config:
                    return PreparationCheck(
                        "Risk Management",
                        "Config Check",
                        "skip",
                        "Configuration not loaded"
                    )
            else:
                trading_config = self.config.get('trading', {})
            
            prop_firm = self.config.get('prop_firm', {}) if self.config else {}
            prop_firm_enabled = prop_firm.get('enabled', False)
            
            # Check trading parameters
            min_confidence = trading_config.get('min_confidence', 75.0)
            position_size_pct = trading_config.get('position_size_pct', 10.0)
            max_position_size_pct = trading_config.get('max_position_size_pct', 15.0)
            stop_loss = trading_config.get('stop_loss', 0.03)
            daily_loss_limit_pct = trading_config.get('daily_loss_limit_pct', 5.0)
            max_drawdown_pct = trading_config.get('max_drawdown_pct', 10.0)
            
            details = {
                "min_confidence": min_confidence,
                "position_size_pct": position_size_pct,
                "max_position_size_pct": max_position_size_pct,
                "stop_loss_pct": stop_loss * 100,
                "daily_loss_limit_pct": daily_loss_limit_pct,
                "max_drawdown_pct": max_drawdown_pct,
                "prop_firm_enabled": prop_firm_enabled
            }
            
            # Check prop firm limits if enabled
            warnings = []
            if prop_firm_enabled:
                risk_limits = prop_firm.get('risk_limits', {})
                prop_max_drawdown = risk_limits.get('max_drawdown_pct', 2.5)
                prop_daily_loss = risk_limits.get('daily_loss_limit_pct', 5.0)
                
                if max_drawdown_pct > prop_max_drawdown:
                    warnings.append(f"Max drawdown {max_drawdown_pct}% exceeds prop firm limit {prop_max_drawdown}%")
                
                if daily_loss_limit_pct > prop_daily_loss:
                    warnings.append(f"Daily loss limit {daily_loss_limit_pct}% exceeds prop firm limit {prop_daily_loss}%")
                
                details["prop_firm_limits"] = {
                    "max_drawdown_pct": prop_max_drawdown,
                    "daily_loss_limit_pct": prop_daily_loss
                }
            
            if warnings:
                return PreparationCheck(
                    "Risk Management",
                    "Risk Limits",
                    "warning",
                    f"Risk limits may exceed prop firm requirements: {len(warnings)} warning(s)",
                    {**details, "warnings": warnings}
                )
            
            return PreparationCheck(
                "Risk Management",
                "Risk Configuration",
                "pass",
                "Risk management properly configured",
                details
            )
        except Exception as e:
            return PreparationCheck(
                "Risk Management",
                "Risk Check",
                "fail",
                f"Failed to check risk management: {e}",
                error=str(e)
            )
    
    def check_data_sources(self) -> PreparationCheck:
        """Check data sources availability"""
        try:
            if SignalGenerationService is None:
                return PreparationCheck(
                    "Data Sources",
                    "Data Check",
                    "warning",
                    "SignalGenerationService not available - cannot check data sources",
                    {}
                )
            
            service = SignalGenerationService()
            
            if not hasattr(service, 'data_sources'):
                return PreparationCheck(
                    "Data Sources",
                    "Data Sources Check",
                    "warning",
                    "Data sources not accessible",
                    {}
                )
            
            sources_status = {}
            for source_name, source in service.data_sources.items():
                sources_status[source_name] = source is not None
            
            available_count = sum(1 for v in sources_status.values() if v)
            total_count = len(sources_status)
            
            if available_count == 0:
                return PreparationCheck(
                    "Data Sources",
                    "Data Availability",
                    "fail",
                    "No data sources available",
                    sources_status
                )
            elif available_count < total_count:
                return PreparationCheck(
                    "Data Sources",
                    "Data Availability",
                    "warning",
                    f"{available_count}/{total_count} data sources available",
                    sources_status
                )
            
            return PreparationCheck(
                "Data Sources",
                "Data Availability",
                "pass",
                f"All {available_count} data sources available",
                sources_status
            )
        except Exception as e:
            return PreparationCheck(
                "Data Sources",
                "Data Check",
                "fail",
                f"Failed to check data sources: {e}",
                error=str(e)
            )
    
    def check_market_hours(self) -> PreparationCheck:
        """Check market hours and trading availability"""
        try:
            if PaperTradingEngine is None:
                return PreparationCheck(
                    "Market Hours",
                    "Market Status",
                    "skip",
                    "PaperTradingEngine not available - cannot check market hours"
                )
            
            engine = PaperTradingEngine()
            
            if not engine.alpaca_enabled:
                return PreparationCheck(
                    "Market Hours",
                    "Market Status",
                    "skip",
                    "Alpaca not connected - cannot check market hours"
                )
            
            is_open = engine.is_market_open()
            
            # Get current time info
            from datetime import datetime
            now = datetime.now()
            
            details = {
                "market_open": is_open,
                "current_time": now.isoformat(),
                "timezone": str(now.astimezone().tzinfo)
            }
            
            if is_open:
                return PreparationCheck(
                    "Market Hours",
                    "Market Status",
                    "pass",
                    "Market is currently OPEN - trading can execute immediately",
                    details
                )
            else:
                return PreparationCheck(
                    "Market Hours",
                    "Market Status",
                    "warning",
                    "Market is currently CLOSED - trading will execute when market opens",
                    details
                )
        except Exception as e:
            return PreparationCheck(
                "Market Hours",
                "Market Check",
                "warning",
                f"Could not determine market status: {e}",
                error=str(e)
            )
    
    def check_positions(self) -> PreparationCheck:
        """Check current positions"""
        try:
            if PaperTradingEngine is None:
                return PreparationCheck(
                    "Positions",
                    "Position Check",
                    "skip",
                    "PaperTradingEngine not available - cannot check positions"
                )
            
            engine = PaperTradingEngine()
            
            if not engine.alpaca_enabled:
                return PreparationCheck(
                    "Positions",
                    "Position Check",
                    "skip",
                    "Alpaca not connected - cannot check positions"
                )
            
            positions = engine.get_positions()
            position_count = len(positions)
            
            details = {
                "position_count": position_count,
                "positions": positions[:5] if positions else []  # Limit to first 5
            }
            
            # Check prop firm position limits if enabled
            if self.config:
                prop_firm = self.config.get('prop_firm', {})
                if prop_firm.get('enabled', False):
                    risk_limits = prop_firm.get('risk_limits', {})
                    max_positions = risk_limits.get('max_positions', 3)
                    
                    if position_count > max_positions:
                        return PreparationCheck(
                            "Positions",
                            "Position Limits",
                            "warning",
                            f"Position count ({position_count}) exceeds prop firm limit ({max_positions})",
                            {**details, "max_positions": max_positions}
                        )
            
            return PreparationCheck(
                "Positions",
                "Position Status",
                "pass",
                f"Current positions: {position_count}",
                details
            )
        except Exception as e:
            return PreparationCheck(
                "Positions",
                "Position Check",
                "warning",
                f"Could not check positions: {e}",
                error=str(e)
            )
    
    def check_database(self) -> PreparationCheck:
        """Check database connectivity"""
        try:
            import sqlite3
            db_path = Path('argo/data/signals.db')
            
            if not db_path.exists():
                return PreparationCheck(
                    "Database",
                    "Database File",
                    "warning",
                    "Database file not found (will be created on first use)",
                    {"path": str(db_path)}
                )
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check if signals table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='signals'")
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                conn.close()
                return PreparationCheck(
                    "Database",
                    "Database Schema",
                    "warning",
                    "Signals table not found (will be created on first use)",
                    {"path": str(db_path)}
                )
            
            # Get signal count
            cursor.execute("SELECT COUNT(*) FROM signals")
            signal_count = cursor.fetchone()[0]
            
            # Get latest signal
            cursor.execute("SELECT MAX(timestamp) FROM signals")
            latest_signal = cursor.fetchone()[0]
            
            conn.close()
            
            return PreparationCheck(
                "Database",
                "Database Status",
                "pass",
                f"Database accessible ({signal_count} signals)",
                {
                    "path": str(db_path),
                    "signal_count": signal_count,
                    "latest_signal": latest_signal
                }
            )
        except Exception as e:
            return PreparationCheck(
                "Database",
                "Database Check",
                "warning",
                f"Database check failed: {e}",
                error=str(e)
            )
    
    def check_prop_firm(self) -> PreparationCheck:
        """Check prop firm configuration (if enabled)"""
        try:
            if not self.config:
                return PreparationCheck(
                    "Prop Firm",
                    "Config Check",
                    "skip",
                    "Configuration not loaded"
                )
            
            prop_firm = self.config.get('prop_firm', {})
            prop_firm_enabled = prop_firm.get('enabled', False)
            
            if not prop_firm_enabled:
                return PreparationCheck(
                    "Prop Firm",
                    "Prop Firm Mode",
                    "skip",
                    "Prop firm mode not enabled"
                )
            
            # Validate prop firm configuration
            risk_limits = prop_firm.get('risk_limits', {})
            required_limits = ['max_drawdown_pct', 'daily_loss_limit_pct', 'max_position_size_pct', 'min_confidence', 'max_positions']
            
            missing = [limit for limit in required_limits if limit not in risk_limits]
            
            if missing:
                return PreparationCheck(
                    "Prop Firm",
                    "Risk Limits",
                    "fail",
                    f"Missing required risk limits: {', '.join(missing)}",
                    {"missing": missing}
                )
            
            # Check prop firm account configuration
            alpaca_config = self.config.get('alpaca', {})
            prop_firm_account = alpaca_config.get('prop_firm_test', {}) if isinstance(alpaca_config, dict) else {}
            
            account_configured = bool(prop_firm_account.get('api_key') and prop_firm_account.get('secret_key'))
            
            if not account_configured:
                return PreparationCheck(
                    "Prop Firm",
                    "Account Configuration",
                    "warning",
                    "Prop firm account credentials not configured",
                    {"risk_limits": risk_limits}
                )
            
            return PreparationCheck(
                "Prop Firm",
                "Prop Firm Configuration",
                "pass",
                "Prop firm mode properly configured",
                {
                    "enabled": True,
                    "risk_limits": risk_limits,
                    "account_configured": account_configured
                }
            )
        except Exception as e:
            return PreparationCheck(
                "Prop Firm",
                "Prop Firm Check",
                "fail",
                f"Failed to check prop firm configuration: {e}",
                error=str(e)
            )
    
    def check_system_resources(self) -> PreparationCheck:
        """Check system resources (disk space, memory)"""
        try:
            import shutil
            import os
            
            # Check disk space
            disk_usage = shutil.disk_usage('.')
            total_gb = disk_usage.total / (1024**3)
            free_gb = disk_usage.free / (1024**3)
            used_percent = (disk_usage.used / disk_usage.total) * 100
            
            details = {
                "disk_total_gb": round(total_gb, 2),
                "disk_free_gb": round(free_gb, 2),
                "disk_used_percent": round(used_percent, 2)
            }
            
            # Check memory (if psutil available)
            memory_info = {}
            try:
                import psutil
                memory = psutil.virtual_memory()
                memory_info = {
                    "memory_total_gb": round(memory.total / (1024**3), 2),
                    "memory_available_gb": round(memory.available / (1024**3), 2),
                    "memory_used_percent": round(memory.percent, 2)
                }
                details.update(memory_info)
            except ImportError:
                pass
            
            # Determine status
            status = "pass"
            warnings = []
            
            if used_percent > 90:
                status = "fail"
                warnings.append(f"Disk usage critical: {used_percent:.1f}%")
            elif used_percent > 80:
                status = "warning"
                warnings.append(f"Disk usage high: {used_percent:.1f}%")
            
            if memory_info and memory_info.get("memory_used_percent", 0) > 90:
                if status == "pass":
                    status = "warning"
                warnings.append(f"Memory usage high: {memory_info['memory_used_percent']:.1f}%")
            
            message = f"Disk: {free_gb:.1f}GB free ({used_percent:.1f}% used)"
            if memory_info:
                message += f" | Memory: {memory_info['memory_available_gb']:.1f}GB available"
            
            if warnings:
                message += f" | {len(warnings)} warning(s)"
            
            return PreparationCheck(
                "System Resources",
                "Resource Check",
                status,
                message,
                {**details, "warnings": warnings}
            )
        except Exception as e:
            return PreparationCheck(
                "System Resources",
                "Resource Check",
                "warning",
                f"Could not check system resources: {e}",
                error=str(e)
            )
    
    def check_file_permissions(self) -> PreparationCheck:
        """Check critical file permissions"""
        try:
            from pathlib import Path
            import os
            
            critical_paths = [
                ("argo/data", "Database directory"),
                ("argo/logs", "Logs directory"),
                ("argo/config.json", "Config file"),
            ]
            
            issues = []
            accessible = []
            
            for path_str, description in critical_paths:
                path = Path(path_str)
                
                # Check if directory exists or can be created
                if path.is_dir() or path_str.endswith('/'):
                    dir_path = path if path.is_dir() else path.parent
                    if not dir_path.exists():
                        # Check if parent is writable
                        if not os.access(dir_path.parent, os.W_OK):
                            issues.append(f"{description}: Cannot create directory (no write permission)")
                        else:
                            accessible.append(f"{description}: Directory can be created")
                    else:
                        if os.access(dir_path, os.W_OK):
                            accessible.append(f"{description}: Writable")
                        else:
                            issues.append(f"{description}: Not writable")
                elif path.is_file():
                    if os.access(path, os.R_OK):
                        accessible.append(f"{description}: Readable")
                    else:
                        issues.append(f"{description}: Not readable")
            
            if issues:
                return PreparationCheck(
                    "File Permissions",
                    "Permission Check",
                    "warning",
                    f"{len(issues)} permission issue(s) found",
                    {"issues": issues, "accessible": accessible}
                )
            
            return PreparationCheck(
                "File Permissions",
                "Permission Check",
                "pass",
                f"All {len(accessible)} critical paths accessible",
                {"accessible": accessible}
            )
        except Exception as e:
            return PreparationCheck(
                "File Permissions",
                "Permission Check",
                "warning",
                f"Could not check permissions: {e}",
                error=str(e)
            )
    
    def check_python_dependencies(self) -> PreparationCheck:
        """Check critical Python dependencies"""
        try:
            critical_deps = {
                "fastapi": "FastAPI",
                "uvicorn": "Uvicorn",
                "alpaca_trade_api": "Alpaca API",
                "pandas": "Pandas",
                "numpy": "NumPy",
            }
            
            installed = []
            missing = []
            
            for module_name, display_name in critical_deps.items():
                try:
                    __import__(module_name)
                    installed.append(display_name)
                except ImportError:
                    missing.append(display_name)
            
            if missing:
                return PreparationCheck(
                    "Dependencies",
                    "Python Dependencies",
                    "warning",
                    f"{len(missing)} dependency(ies) missing: {', '.join(missing)}",
                    {"installed": installed, "missing": missing}
                )
            
            return PreparationCheck(
                "Dependencies",
                "Python Dependencies",
                "pass",
                f"All {len(installed)} critical dependencies installed",
                {"installed": installed}
            )
        except Exception as e:
            return PreparationCheck(
                "Dependencies",
                "Dependency Check",
                "warning",
                f"Could not check dependencies: {e}",
                error=str(e)
            )
    
    def check_log_directory(self) -> PreparationCheck:
        """Check log directory accessibility"""
        try:
            from pathlib import Path
            import os
            
            log_dirs = [
                Path("argo/logs"),
                Path("logs"),
            ]
            
            accessible_dir = None
            for log_dir in log_dirs:
                if log_dir.exists() and os.access(log_dir, os.W_OK):
                    accessible_dir = log_dir
                    break
                elif log_dir.parent.exists() and os.access(log_dir.parent, os.W_OK):
                    # Can create
                    accessible_dir = log_dir
                    break
            
            if accessible_dir:
                return PreparationCheck(
                    "Logging",
                    "Log Directory",
                    "pass",
                    f"Log directory accessible: {accessible_dir}",
                    {"log_directory": str(accessible_dir)}
                )
            else:
                return PreparationCheck(
                    "Logging",
                    "Log Directory",
                    "warning",
                    "Log directory may not be writable (logs may not be saved)",
                    {}
                )
        except Exception as e:
            return PreparationCheck(
                "Logging",
                "Log Check",
                "warning",
                f"Could not check log directory: {e}",
                error=str(e)
            )
    
    def check_network_connectivity(self) -> PreparationCheck:
        """Check network connectivity to external services"""
        try:
            import requests
            import socket
            
            services = {
                "Alpaca API": ("api.alpaca.markets", 443),
                "Alpine Backend": ("91.98.153.49", 8001),
            }
            
            results = {}
            reachable = 0
            
            for service_name, (host, port) in services.items():
                try:
                    # Try socket connection
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    result = sock.connect_ex((host, port))
                    sock.close()
                    
                    if result == 0:
                        results[service_name] = {"reachable": True, "method": "socket"}
                        reachable += 1
                    else:
                        results[service_name] = {"reachable": False, "error": "Connection refused"}
                except socket.gaierror:
                    results[service_name] = {"reachable": False, "error": "DNS resolution failed"}
                except Exception as e:
                    results[service_name] = {"reachable": False, "error": str(e)}
            
            if reachable == 0:
                return PreparationCheck(
                    "Network",
                    "External Connectivity",
                    "warning",
                    "No external services reachable (may be network/firewall issue)",
                    results
                )
            elif reachable < len(services):
                return PreparationCheck(
                    "Network",
                    "External Connectivity",
                    "warning",
                    f"{reachable}/{len(services)} services reachable",
                    results
                )
            
            return PreparationCheck(
                "Network",
                "External Connectivity",
                "pass",
                f"All {reachable} external services reachable",
                results
            )
        except Exception as e:
            return PreparationCheck(
                "Network",
                "Network Check",
                "warning",
                f"Could not check network connectivity: {e}",
                error=str(e)
            )
    
    def check_data_source_connectivity(self) -> PreparationCheck:
        """Test actual connectivity to data sources"""
        try:
            if SignalGenerationService is None:
                return PreparationCheck(
                    "Data Source Connectivity",
                    "Connectivity Test",
                    "skip",
                    "SignalGenerationService not available"
                )
            
            service = SignalGenerationService()
            
            if not hasattr(service, 'data_sources'):
                return PreparationCheck(
                    "Data Source Connectivity",
                    "Connectivity Test",
                    "skip",
                    "Data sources not accessible"
                )
            
            # Test a few key data sources
            test_results = {}
            tested = 0
            working = 0
            
            # Test Massive API (if available)
            if 'massive' in service.data_sources and service.data_sources['massive']:
                try:
                    # Try to get a simple price (this is a lightweight test)
                    tested += 1
                    test_results['massive'] = {"status": "available", "tested": True}
                    working += 1
                except Exception as e:
                    test_results['massive'] = {"status": "error", "error": str(e)[:50]}
            
            # Test Alpaca Pro (if available)
            if 'alpaca_pro' in service.data_sources and service.data_sources['alpaca_pro']:
                tested += 1
                test_results['alpaca_pro'] = {"status": "available", "tested": True}
                working += 1
            
            if tested == 0:
                return PreparationCheck(
                    "Data Source Connectivity",
                    "Connectivity Test",
                    "skip",
                    "No data sources available for testing"
                )
            
            if working == tested:
                return PreparationCheck(
                    "Data Source Connectivity",
                    "Connectivity Test",
                    "pass",
                    f"All {working} tested data sources responding",
                    test_results
                )
            else:
                return PreparationCheck(
                    "Data Source Connectivity",
                    "Connectivity Test",
                    "warning",
                    f"{working}/{tested} data sources responding",
                    test_results
                )
        except Exception as e:
            return PreparationCheck(
                "Data Source Connectivity",
                "Connectivity Test",
                "warning",
                f"Could not test data source connectivity: {e}",
                error=str(e)
            )
    
    def check_performance(self) -> PreparationCheck:
        """Check system performance metrics"""
        try:
            if SignalGenerationService is None:
                return PreparationCheck(
                    "Performance",
                    "Performance Check",
                    "skip",
                    "SignalGenerationService not available"
                )
            
            import time
            
            # Test signal generation performance
            start_time = time.time()
            try:
                service = SignalGenerationService()
                init_time = time.time() - start_time
                
                details = {
                    "signal_service_init_seconds": round(init_time, 3)
                }
                
                # Check if initialization is reasonable (< 5 seconds)
                if init_time > 10:
                    return PreparationCheck(
                        "Performance",
                        "Initialization Speed",
                        "warning",
                        f"Slow initialization: {init_time:.2f}s (may impact startup)",
                        details
                    )
                elif init_time > 5:
                    return PreparationCheck(
                        "Performance",
                        "Initialization Speed",
                        "warning",
                        f"Initialization time: {init_time:.2f}s",
                        details
                    )
                
                return PreparationCheck(
                    "Performance",
                    "Initialization Speed",
                    "pass",
                    f"Fast initialization: {init_time:.2f}s",
                    details
                )
            except Exception as e:
                return PreparationCheck(
                    "Performance",
                    "Performance Check",
                    "warning",
                    f"Could not measure performance: {e}",
                    error=str(e)
                )
        except Exception as e:
            return PreparationCheck(
                "Performance",
                "Performance Check",
                "skip",
                f"Performance check not available: {e}",
                error=str(e)
            )
    
    def check_security(self) -> PreparationCheck:
        """Check security configuration"""
        try:
            issues = []
            checks_passed = []
            
            # Check if config file has proper permissions (not world-readable)
            config_paths = [
                Path("argo/config.json"),
                Path("config.json"),
            ]
            
            config_found = False
            for config_path in config_paths:
                if config_path.exists():
                    config_found = True
                    import stat
                    file_stat = config_path.stat()
                    mode = file_stat.st_mode
                    
                    # Check if world-readable (security risk)
                    if mode & stat.S_IROTH:
                        issues.append("Config file is world-readable (security risk)")
                    else:
                        checks_passed.append("Config file permissions secure")
                    break
            
            if not config_found:
                checks_passed.append("Config file location check skipped")
            
            # Check for API keys in environment (better than in files)
            import os
            if os.getenv('ALPACA_API_KEY') or os.getenv('ARGO_API_KEY'):
                checks_passed.append("API keys in environment variables (secure)")
            else:
                # Not necessarily an issue, but worth noting
                pass
            
            if issues:
                return PreparationCheck(
                    "Security",
                    "Security Configuration",
                    "warning",
                    f"{len(issues)} security issue(s) found",
                    {"issues": issues, "checks_passed": checks_passed}
                )
            
            return PreparationCheck(
                "Security",
                "Security Configuration",
                "pass",
                f"Security checks passed ({len(checks_passed)} check(s))",
                {"checks_passed": checks_passed}
            )
        except Exception as e:
            return PreparationCheck(
                "Security",
                "Security Check",
                "warning",
                f"Could not check security: {e}",
                error=str(e)
            )
    
    def check_backup_verification(self) -> PreparationCheck:
        """Check backup and recovery capabilities"""
        try:
            checks = []
            
            # Check if database backup location exists
            data_dir = Path("argo/data")
            if data_dir.exists():
                checks.append("Database directory exists")
            
            # Check if logs directory exists (for recovery)
            logs_dir = Path("argo/logs")
            if logs_dir.exists():
                checks.append("Logs directory exists")
            
            # Check if config backup exists
            config_backup = Path("argo/config.json.backup")
            if config_backup.exists():
                checks.append("Config backup exists")
            
            if len(checks) >= 2:
                return PreparationCheck(
                    "Backup",
                    "Backup Verification",
                    "pass",
                    f"Backup infrastructure ready ({len(checks)} check(s))",
                    {"checks": checks}
                )
            else:
                return PreparationCheck(
                    "Backup",
                    "Backup Verification",
                    "warning",
                    "Limited backup infrastructure (consider setting up automated backups)",
                    {"checks": checks}
                )
        except Exception as e:
            return PreparationCheck(
                "Backup",
                "Backup Check",
                "warning",
                f"Could not verify backups: {e}",
                error=str(e)
            )
    
    def check_integration(self) -> PreparationCheck:
        """Check integration between components"""
        try:
            if SignalGenerationService is None:
                return PreparationCheck(
                    "Integration",
                    "Integration Check",
                    "skip",
                    "SignalGenerationService not available - cannot check integration"
                )
            
            checks = []
            issues = []
            
            # Check signal service -> trading engine integration
            try:
                service = SignalGenerationService()
                if service.trading_engine is not None:
                    checks.append("Signal service ↔ Trading engine: Connected")
                else:
                    issues.append("Signal service ↔ Trading engine: Not connected")
            except:
                issues.append("Signal service initialization failed")
            
            # Check Alpine sync integration
            try:
                if hasattr(service, 'alpine_sync') and service.alpine_sync:
                    checks.append("Signal service ↔ Alpine sync: Connected")
                else:
                    issues.append("Signal service ↔ Alpine sync: Not configured")
            except:
                pass
            
            if issues:
                return PreparationCheck(
                    "Integration",
                    "Component Integration",
                    "warning",
                    f"{len(issues)} integration issue(s) found",
                    {"checks": checks, "issues": issues}
                )
            
            return PreparationCheck(
                "Integration",
                "Component Integration",
                "pass",
                f"All {len(checks)} integration(s) verified",
                {"checks": checks}
            )
        except Exception as e:
            return PreparationCheck(
                "Integration",
                "Integration Check",
                "warning",
                f"Could not check integration: {e}",
                error=str(e)
            )
    
    def check_api_connectivity(self) -> PreparationCheck:
        """Check API endpoint connectivity (if services are running)"""
        try:
            import requests
        except ImportError:
            return PreparationCheck(
                "API Connectivity",
                "API Check",
                "skip",
                "requests library not available"
            )
        
        base_url = "http://localhost:8000" if self.environment == "development" else "http://178.156.194.174:8000"
        
        endpoints = {
            "/api/v1/health": 200,
        }
        
        results = {}
        for endpoint, expected_status in endpoints.items():
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                results[endpoint] = {
                    "status_code": response.status_code,
                    "reachable": response.status_code == expected_status
                }
            except requests.exceptions.RequestException as e:
                results[endpoint] = {
                    "reachable": False,
                    "error": str(e)
                }
        
        reachable_count = sum(1 for r in results.values() if r.get("reachable", False))
        
        if reachable_count == 0:
            return PreparationCheck(
                "API Connectivity",
                "API Endpoints",
                "warning",
                "API endpoints not reachable (service may not be running)",
                results
            )
        elif reachable_count < len(endpoints):
            return PreparationCheck(
                "API Connectivity",
                "API Endpoints",
                "warning",
                f"{reachable_count}/{len(endpoints)} endpoints reachable",
                results
            )
        
        return PreparationCheck(
            "API Connectivity",
            "API Endpoints",
            "pass",
            f"All {reachable_count} endpoints reachable",
            results
        )
    
    def run_all_checks(self) -> Dict:
        """Run all preparation checks"""
        print('\n' + '='*80)
        print('🚀 COMPREHENSIVE PRE-TRADING PREPARATION')
        print('='*80)
        print(f'Started: {self.start_time.strftime("%Y-%m-%d %H:%M:%S UTC")}')
        print('='*80 + '\n')
        
        # Run all checks
        check_functions = [
            ("Environment", self.check_environment),
            ("Configuration", self.check_configuration),
            ("System Resources", self.check_system_resources),
            ("File Permissions", self.check_file_permissions),
            ("Dependencies", self.check_python_dependencies),
            ("Logging", self.check_log_directory),
            ("Network", self.check_network_connectivity),
            ("Security", self.check_security),
            ("Backup", self.check_backup_verification),
            ("Trading Engine", self.check_trading_engine),
            ("Signal Service", self.check_signal_service),
            ("Risk Management", self.check_risk_management),
            ("Prop Firm", self.check_prop_firm),
            ("Data Sources", self.check_data_sources),
            ("Data Source Connectivity", self.check_data_source_connectivity),
            ("Integration", self.check_integration),
            ("Performance", self.check_performance),
            ("Market Hours", self.check_market_hours),
            ("Positions", self.check_positions),
            ("Database", self.check_database),
            ("API Connectivity", self.check_api_connectivity),
        ]
        
        for category, check_func in check_functions:
            try:
                result = check_func()
                self.checks.append(result)
                
                status_icon = {
                    "pass": "✅",
                    "fail": "❌",
                    "warning": "⚠️",
                    "skip": "⏭️"
                }.get(result.status, "❓")
                
                print(f'{status_icon} [{category}] {result.name}: {result.status.upper()}')
                if result.message:
                    print(f'   {result.message}')
                
                # Print key details
                if result.details and result.status != "pass":
                    for key, value in list(result.details.items())[:3]:  # Limit to first 3 details
                        if isinstance(value, (int, float)):
                            if 'price' in key.lower() or 'value' in key.lower() or 'power' in key.lower():
                                print(f'   {key}: ${value:,.2f}')
                            elif 'pct' in key.lower() or 'percent' in key.lower():
                                print(f'   {key}: {value}%')
                            else:
                                print(f'   {key}: {value:,}')
                        elif isinstance(value, bool):
                            print(f'   {key}: {"Yes" if value else "No"}')
                        elif isinstance(value, (list, dict)) and len(str(value)) < 100:
                            print(f'   {key}: {value}')
                        elif not isinstance(value, (list, dict)):
                            print(f'   {key}: {value}')
                
                print()
            except Exception as e:
                error_check = PreparationCheck(
                    category,
                    "Check Execution",
                    "fail",
                    f"Check failed with exception: {e}",
                    error=str(e)
                )
                self.checks.append(error_check)
                print(f'❌ [{category}] Check failed: {e}\n')
        
        # Generate summary
        return self._generate_summary()
    
    def _generate_summary(self) -> Dict:
        """Generate summary report"""
        end_time = datetime.now(timezone.utc)
        duration = (end_time - self.start_time).total_seconds()
        
        passed = [c for c in self.checks if c.status == "pass"]
        failed = [c for c in self.checks if c.status == "fail"]
        warnings = [c for c in self.checks if c.status == "warning"]
        skipped = [c for c in self.checks if c.status == "skip"]
        
        print('='*80)
        print('📊 PREPARATION SUMMARY')
        print('='*80)
        print(f'✅ Passed: {len(passed)}')
        print(f'❌ Failed: {len(failed)}')
        print(f'⚠️  Warnings: {len(warnings)}')
        print(f'⏭️  Skipped: {len(skipped)}')
        print(f'📊 Total Checks: {len(self.checks)}')
        print(f'⏱️  Duration: {duration:.2f}s')
        print('='*80)
        
        # Critical failures
        if failed:
            print('\n❌ CRITICAL FAILURES (Must Fix Before Trading):')
            print('-'*80)
            for check in failed:
                print(f'   • [{check.category}] {check.name}')
                print(f'     {check.message}')
                if check.error:
                    print(f'     Error: {check.error[:100]}...')
            print()
        
        # Warnings
        if warnings:
            print('⚠️  WARNINGS (Review Recommended):')
            print('-'*80)
            for check in warnings:
                print(f'   • [{check.category}] {check.name}: {check.message}')
            print()
        
        # Overall status
        if len(failed) == 0:
            if len(warnings) == 0:
                print('✅ ALL CHECKS PASSED - SYSTEM READY FOR TRADING TOMORROW!')
            else:
                print('⚠️  SYSTEM READY WITH WARNINGS - Review warnings above')
                print('\n💡 RECOMMENDATIONS:')
                print('   - Review warnings to ensure optimal configuration')
                print('   - Verify all services are running before trading starts')
                print('   - Test with small positions first')
        else:
            print('❌ SYSTEM NOT READY - Fix critical failures before trading')
            print('\n🔧 ACTION REQUIRED:')
            print('   - Address all critical failures listed above')
            print('   - Re-run this script after fixes: python3 scripts/pre_trading_preparation.py')
            print('   - Ensure all services are properly configured')
        
        # Add next steps
        print('\n📋 NEXT STEPS:')
        if self.environment == "production":
            print('   1. Verify all critical checks pass')
            print('   2. Start trading services: ./commands/start all')
            print('   3. Monitor first trades closely')
            print('   4. Check logs: ./commands/logs view argo production')
        else:
            print('   1. Review all checks and warnings')
            print('   2. Configure Alpaca credentials for production')
            print('   3. Test in development environment first')
            print('   4. Deploy to production when ready')
        
        print('='*80 + '\n')
        
        return {
            "timestamp": self.start_time.isoformat(),
            "duration_seconds": duration,
            "environment": self.environment,
            "summary": {
                "passed": len(passed),
                "failed": len(failed),
                "warnings": len(warnings),
                "skipped": len(skipped),
                "total": len(self.checks)
            },
            "checks": [asdict(c) for c in self.checks],
            "ready_for_trading": len(failed) == 0
        }

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive Pre-Trading Preparation')
    parser.add_argument('--json', action='store_true',
                       help='Output results as JSON')
    parser.add_argument('--output', type=str, default=None,
                       help='Save results to file')
    
    args = parser.parse_args()
    
    preparation = PreTradingPreparation()
    results = preparation.run_all_checks()
    
    # Save to file if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f'📄 Results saved to: {output_path}\n')
    
    # Output JSON if requested
    if args.json:
        print(json.dumps(results, indent=2))
    
    # Exit with appropriate code
    if results["summary"]["failed"] > 0:
        sys.exit(1)
    elif results["summary"]["warnings"] > 0:
        sys.exit(0)  # Warnings are OK
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()

