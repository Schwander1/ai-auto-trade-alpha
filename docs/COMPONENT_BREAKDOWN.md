# Complete Component Breakdown

**Date:** January 16, 2025  
**Version:** 1.0  
**Status:** Comprehensive Component Inventory

---

## Table of Contents

1. [Argo Trading Engine](#1-argo-trading-engine)
2. [Alpine Backend](#2-alpine-backend)
3. [Alpine Frontend](#3-alpine-frontend)
4. [Infrastructure & DevOps](#4-infrastructure--devops)
5. [Shared Packages](#5-shared-packages)
6. [Development Tools](#6-development-tools)

---

## 1. Argo Trading Engine

**Location:** `argo/`  
**Type:** Python/FastAPI  
**Purpose:** Trading signal generation and execution

### 1.1 Core Services

#### 1.1.1 Signal Generation Service
**File:** `argo/core/signal_generation_service.py`

**Responsibilities:**
- Generates trading signals every 5 seconds
- Orchestrates multi-source data aggregation
- Applies Weighted Consensus v6.0 algorithm
- Manages 7-layer risk validation
- Executes trades via Paper Trading Engine
- Tracks signal lifecycle and performance

**Key Sub-Components:**
- `generate_signals_cycle()` - Main generation loop
- `generate_signal_for_symbol()` - Per-symbol signal generation
- `_fetch_market_data_signals()` - Parallel market data fetching
- `_fetch_independent_source_signals()` - Parallel independent source fetching
- `_calculate_consensus()` - Weighted consensus calculation
- `_validate_trade()` - 7-layer risk validation
- `_execute_trade_if_valid()` - Trade execution orchestration

**Optimizations:**
- Consensus calculation caching (6,024x speedup)
- AI reasoning caching (1 hour TTL)
- Price change threshold filtering (0.5% minimum)
- Priority-based symbol processing (volatility-based)
- Adaptive confidence thresholds by market regime

#### 1.1.2 Weighted Consensus Engine
**File:** `argo/core/weighted_consensus_engine.py`

**Responsibilities:**
- Combines signals from multiple data sources
- Applies weighted voting algorithm
- Calculates consensus confidence scores
- Manages source weights and priorities

**Key Features:**
- 75% consensus threshold (configurable)
- Source weight configuration
- Consensus calculation caching
- Weighted voting algorithm

#### 1.1.3 Paper Trading Engine
**File:** `argo/core/paper_trading_engine.py`

**Responsibilities:**
- Executes trades on Alpaca paper trading
- Manages position sizing (confidence & volatility-based)
- Handles order submission (market/limit orders)
- Places bracket orders (stop-loss/take-profit)
- Tracks order lifecycle and status
- Implements retry logic with exponential backoff

**Key Sub-Components:**
- `execute_signal()` - Main execution entry point
- `_execute_live()` - Live Alpaca execution
- `_execute_sim()` - Simulation mode
- `_prepare_order_details()` - Position size calculation
- `_submit_main_order()` - Order submission to Alpaca
- `_place_bracket_orders()` - Stop/target order placement
- `get_positions()` - Position retrieval
- `get_order_status()` - Order status tracking

**Environment Support:**
- Dev environment (dev Alpaca account)
- Production environment (prod Alpaca account)
- Prop Firm mode (separate prop firm account)

**Optimizations:**
- Volatility caching (1 hour TTL)
- Account data caching (30 second TTL)
- Position caching (10 second TTL)

### 1.2 Data Sources

**Location:** `argo/core/data_sources/`

#### 1.2.1 Alpaca Pro Source
**File:** `data_sources/alpaca_pro_source.py`
- Primary market data source
- Real-time price data
- 40% weight in consensus
- Fallback to Massive.com

#### 1.2.2 Massive.com Source
**File:** `data_sources/massive_source.py`
- Fallback market data source
- S3-based data storage
- 40% weight in consensus
- Used when Alpaca Pro unavailable

#### 1.2.3 YFinance Source
**File:** `data_sources/yfinance_source.py`
- Primary technical indicators
- Free market data
- 25% weight in consensus
- Historical data support

#### 1.2.4 Alpha Vantage Source
**File:** `data_sources/alpha_vantage_source.py`
- Supplemental technical indicators
- Premium API access
- 25% weight in consensus
- Advanced technical analysis

#### 1.2.5 xAI Grok Source
**File:** `data_sources/xai_grok_source.py`
- Sentiment analysis
- AI-powered market insights
- 20% weight in consensus
- Option 2B optimization (market hours stocks, 24/7 crypto, 90s cache)

#### 1.2.6 Sonar AI Source
**File:** `data_sources/sonar_source.py`
- AI analysis and predictions
- Market intelligence
- 15% weight in consensus
- Optimized caching (120s cache)

#### 1.2.7 Chinese Models Source
**File:** `data_sources/chinese_models_source.py`
- Chinese market data integration
- Alternative data source

### 1.3 Core Infrastructure

#### 1.3.1 Signal Tracking
**File:** `argo/core/signal_tracker.py`
- Tracks signal history
- Performance metrics
- Signal lifecycle management

#### 1.3.2 Signal Quality Scorer
**File:** `argo/core/signal_quality_scorer.py`
- Calculates signal quality scores
- Win rate tracking
- Confidence calibration

#### 1.3.3 Regime Detector
**File:** `argo/core/regime_detector.py`
- Detects market regimes (BULL, BEAR, CHOP, CRISIS)
- Adjusts confidence based on regime
- Regime-based threshold adaptation

#### 1.3.4 Win Rate Calculator
**File:** `argo/core/win_rate_calculator.py`
- Calculates win rates for signals
- Performance tracking
- Statistical analysis

#### 1.3.5 Adaptive Weight Manager
**File:** `argo/core/adaptive_weight_manager.py`
- Dynamically adjusts source weights
- Performance-based optimization
- Adaptive learning

#### 1.3.6 Performance Monitoring
**Files:**
- `argo/core/performance_monitor.py` - General performance monitoring
- `argo/core/performance_metrics.py` - Metrics collection
- `argo/core/performance_budget_monitor.py` - Budget-based monitoring
- `argo/core/baseline_metrics.py` - Baseline comparison

#### 1.3.7 Caching Systems
**Files:**
- `argo/core/adaptive_cache.py` - Adaptive caching
- `argo/core/adaptive_cache_ttl.py` - TTL management
- `argo/core/redis_cache.py` - Redis integration
- `argo/core/json_cache.py` - JSON-specific caching
- `argo/core/api_cache.py` - API response caching

#### 1.3.8 Rate Limiting
**File:** `argo/core/rate_limiter.py`
- API rate limiting
- Request throttling
- Protection against abuse

#### 1.3.9 Circuit Breaker
**File:** `argo/core/circuit_breaker.py`
- Fault tolerance
- Automatic failure detection
- Service degradation handling

#### 1.3.10 Request Coalescing
**File:** `argo/core/request_coalescer.py`
- Combines duplicate requests
- Reduces redundant API calls
- Performance optimization

#### 1.3.11 Error Recovery
**File:** `argo/core/error_recovery.py`
- Automatic error recovery
- Retry logic
- Failure handling

#### 1.3.12 Data Source Health
**File:** `argo/core/data_source_health.py`
- Monitors data source availability
- Health checks
- Automatic failover

#### 1.3.13 Incremental Fetcher
**File:** `argo/core/incremental_fetcher.py`
- Incremental data fetching
- Delta updates
- Efficiency optimization

#### 1.3.14 Multi-Source Aggregator
**File:** `argo/core/multi_source_aggregator.py`
- Aggregates data from multiple sources
- Data fusion
- Conflict resolution

#### 1.3.15 WebSocket Streams
**File:** `argo/core/websocket_streams.py`
- Real-time data streaming
- WebSocket connections
- Live updates

#### 1.3.16 Alpine Sync
**File:** `argo/core/alpine_sync.py`
- Synchronizes signals with Alpine backend
- API integration
- Data consistency

#### 1.3.17 Feature Flags
**File:** `argo/core/feature_flags.py`
- Feature flag management
- A/B testing support
- Gradual rollouts

#### 1.3.18 Configuration Management
**Files:**
- `argo/core/config_loader.py` - Configuration loading
- `argo/core/config_validator.py` - Configuration validation
- `argo/core/environment.py` - Environment detection

#### 1.3.19 API Key Management
**File:** `argo/core/api_key_manager.py`
- API key rotation
- Key management
- Security

#### 1.3.20 Alerting
**File:** `argo/core/alerting.py`
- Alert generation
- Notification system
- Critical event handling

#### 1.3.21 Monitoring Dashboard
**File:** `argo/core/monitoring_dashboard.py`
- Real-time monitoring
- Dashboard metrics
- Visualization

#### 1.3.22 Enhanced Logging
**File:** `argo/core/enhanced_logging.py`
- Structured logging
- Log aggregation
- Debugging support

#### 1.3.23 Enhanced Metrics
**File:** `argo/core/enhanced_metrics.py`
- Prometheus metrics
- System metrics (CPU, memory, disk)
- Custom metrics

#### 1.3.24 Database Optimization
**Files:**
- `argo/core/database_indexes.py` - Index management
- `argo/core/database_optimizer.py` - Query optimization

#### 1.3.25 Improvement Validator
**File:** `argo/core/improvement_validator.py`
- Validates performance improvements
- A/B testing validation
- Change verification

### 1.4 Risk Management

**Location:** `argo/risk/`

#### 1.4.1 Prop Firm Risk Monitor
**File:** `risk/prop_firm_risk_monitor.py`
- Monitors prop firm account limits
- Drawdown tracking
- Daily loss limits
- Position size limits

#### 1.4.2 Enhanced Prop Firm Monitor
**File:** `risk/prop_firm_monitor_enhanced.py`
- Advanced prop firm monitoring
- Enhanced risk metrics
- Real-time alerts

#### 1.4.3 Advanced Correlation Manager
**File:** `risk/advanced_correlation_manager.py`
- Sector correlation analysis
- Position correlation tracking
- Risk diversification

#### 1.4.4 Risk Manager
**File:** `risk/risk_manager.py`
- General risk management
- Risk calculations
- Risk limits enforcement

### 1.5 Backtesting System

**Location:** `argo/backtest/`

#### 1.5.1 Base Backtester
**File:** `backtest/base_backtester.py`
- Base class for all backtesters
- Common functionality
- Abstract interface

#### 1.5.2 Strategy Backtester
**File:** `backtest/strategy_backtester.py`
- Strategy-specific backtesting
- Custom strategy support

#### 1.5.3 Quick Backtester
**File:** `backtest/quick_backtester.py`
- Fast backtesting
- Quick validation
- Lightweight testing

#### 1.5.4 Comprehensive Backtester
**File:** `backtest/comprehensive_backtest.py`
- Full-featured backtesting
- Complete analysis
- Detailed reporting

#### 1.5.5 Monte Carlo Backtester
**File:** `backtest/monte_carlo_backtester.py`
- Monte Carlo simulation
- Statistical analysis
- Risk assessment

#### 1.5.6 Walk-Forward Backtester
**File:** `backtest/walk_forward.py`
- Walk-forward optimization
- Out-of-sample testing
- Robust validation

#### 1.5.7 Incremental Backtester
**File:** `backtest/incremental_backtester.py`
- Incremental backtesting
- Progressive analysis
- Real-time updates

#### 1.5.8 Batch Backtester
**File:** `backtest/batch_backtester.py`
- Batch processing
- Multiple symbol testing
- Parallel execution

#### 1.5.9 Prop Firm Backtester
**File:** `backtest/prop_firm_backtester.py`
- Prop firm rule simulation
- Account limit testing
- Risk constraint validation

#### 1.5.10 CPCV Backtester
**File:** `backtest/cpcv_backtester.py`
- Combinatorial Purged Cross-Validation
- Advanced validation technique
- Bias prevention

#### 1.5.11 Calibrated Backtester
**File:** `backtest/calibrated_backtester.py`
- Calibrated backtesting
- Bias correction
- Accuracy improvement

#### 1.5.12 Enhanced Backtester
**File:** `backtest/enhanced_backtester.py`
- Enhanced features
- Advanced metrics
- Extended analysis

#### 1.5.13 Fixed Backtester
**File:** `backtest/fixed_backtester.py`
- Bug fixes and improvements
- Stable version

#### 1.5.14 Profit Backtester
**File:** `backtest/profit_backtester.py`
- Profit-focused analysis
- Revenue optimization

#### 1.5.15 Result Processing
**Files:**
- `backtest/result_validator.py` - Result validation
- `backtest/result_visualizer.py` - Visualization
- `backtest/result_exporter.py` - Export functionality
- `backtest/results_analyzer.py` - Analysis tools
- `backtest/results_storage.py` - Storage management

#### 1.5.16 Data Management
**Files:**
- `backtest/data_manager.py` - Data handling
- `backtest/data_converter.py` - Format conversion
- `backtest/historical_signal_generator.py` - Historical signal generation

#### 1.5.17 Analysis Tools
**Files:**
- `backtest/performance_monitor.py` - Performance tracking
- `backtest/performance_optimizer.py` - Optimization
- `backtest/performance_enhancer.py` - Enhancement
- `backtest/transaction_cost_analyzer.py` - Cost analysis
- `backtest/enhanced_transaction_cost.py` - Advanced cost modeling
- `backtest/market_regime_analyzer.py` - Regime analysis
- `backtest/symbol_classifier.py` - Symbol classification
- `backtest/signal_tracer.py` - Signal tracing

#### 1.5.18 Optimization
**Files:**
- `backtest/optimizer.py` - General optimization
- `backtest/ml_threshold_optimizer.py` - ML-based optimization

#### 1.5.19 Bias Prevention
**File:** `backtest/bias_prevention.py`
- Prevents overfitting
- Bias detection
- Statistical validation

#### 1.5.20 Utilities
**Files:**
- `backtest/constants.py` - Constants
- `backtest/utils.py` - Utility functions
- `backtest/indicators.py` - Technical indicators
- `backtest/symbol_config.py` - Symbol configuration
- `backtest/error_handling.py` - Error handling
- `backtest/exceptions.py` - Custom exceptions

### 1.6 Validation System

**Location:** `argo/validation/`

#### 1.6.1 Data Quality Monitor
**File:** `validation/data_quality.py`
- Monitors data quality
- Anomaly detection
- Data validation

#### 1.6.2 Signal Lifecycle
**File:** `validation/signal_lifecycle.py`
- Tracks signal lifecycle
- State management
- Lifecycle validation

#### 1.6.3 Win Rate Validator
**File:** `validation/win_rate_validator.py`
- Validates win rates
- Statistical validation
- Performance verification

#### 1.6.4 Reconciliation
**File:** `validation/reconciliation.py`
- Data reconciliation
- Consistency checks
- Error detection

### 1.7 API Layer

**Location:** `argo/api/`

#### 1.7.1 Main Server
**File:** `api/server.py`
- FastAPI application
- Route registration
- Middleware setup
- Background task management

#### 1.7.2 Signals API
**File:** `api/signals.py`
- Signal retrieval endpoints
- Signal filtering
- Signal metadata

#### 1.7.3 Trading API
**File:** `api/trading.py`
- Trading operations
- Order management
- Position queries

#### 1.7.4 Backtest API
**File:** `api/backtest.py`
- Backtest execution
- Result retrieval
- Analysis endpoints

#### 1.7.5 Health API
**File:** `api/health.py`
- Health check endpoints
- System status
- Service availability

#### 1.7.6 Metrics API
**File:** `api/metrics.py`
- Prometheus metrics
- Performance metrics
- System metrics

#### 1.7.7 Performance API
**File:** `api/performance.py`
- Performance data
- Statistics
- Analytics

#### 1.7.8 Symbols API
**File:** `api/symbols.py`
- Symbol management
- Symbol metadata
- Symbol configuration

#### 1.7.9 Tradervue API
**File:** `api/tradervue.py`
- Tradervue integration
- Trade journaling
- Performance tracking

#### 1.7.10 Validation API
**File:** `api/validation.py`
- Validation endpoints
- Data validation
- Signal validation

### 1.8 Compliance

**Location:** `argo/compliance/`

#### 1.8.1 Daily Backup
**File:** `compliance/daily_backup.py`
- Automated daily backups
- S3 storage
- Backup verification

#### 1.8.2 Weekly Report
**File:** `compliance/weekly_report.py`
- Weekly compliance reports
- Performance summaries
- Regulatory reporting

#### 1.8.3 Integrity Monitor
**File:** `compliance/integrity_monitor.py`
- Data integrity monitoring
- Anomaly detection
- Security monitoring

#### 1.8.4 Signal Logger
**File:** `compliance/signal_logger.py`
- Signal logging
- Audit trail
- Compliance tracking

#### 1.8.5 Backup Verification
**File:** `compliance/verify_backup.py`
- Backup verification
- Integrity checks
- Recovery testing

#### 1.8.6 Health Check
**File:** `compliance/health_check.py`
- Compliance health checks
- System validation
- Status reporting

#### 1.8.7 S3 Lifecycle Policy
**File:** `compliance/s3_lifecycle_policy.py`
- S3 lifecycle management
- Data retention
- Cost optimization

### 1.9 Integrations

**Location:** `argo/integrations/`

#### 1.9.1 Tradervue Integration
**Files:**
- `integrations/tradervue_integration.py` - Main integration
- `integrations/tradervue_client.py` - API client

**Features:**
- Trade journaling
- Performance tracking
- Automatic trade logging

#### 1.9.2 MyFXBook Client
**File:** `integrations/myfxbook_client.py`
- MyFXBook API integration
- Account tracking
- Performance monitoring

#### 1.9.3 Notion Command Center
**File:** `integrations/notion_command_center.py`
- Notion integration
- Command center sync
- Documentation sync

#### 1.9.4 Premium APIs
**File:** `integrations/premium_apis.py`
- Premium API integrations
- External service connections

#### 1.9.5 Complete Tracking
**File:** `integrations/complete_tracking.py`
- Comprehensive tracking
- Multi-platform integration
- Unified tracking

### 1.10 Strategies

**Location:** `argo/strategies/`

#### 1.10.1 Base Strategy
**File:** `strategies/base_strategy.py`
- Base class for strategies
- Common interface
- Abstract methods

#### 1.10.2 Momentum Strategy
**File:** `strategies/momentum/momentum_strategy.py`
- Momentum-based trading
- Trend following
- Breakout detection

#### 1.10.3 Mean Reversion Strategy
**File:** `strategies/mean_reversion/mean_reversion_strategy.py`
- Mean reversion trading
- Oversold/overbought detection
- Range trading

#### 1.10.4 ML Ensemble
**File:** `strategies/ml/ml_ensemble.py`
- Machine learning ensemble
- ML-based signals
- Model aggregation

### 1.11 AI Components

**Location:** `argo/ai/`

#### 1.11.1 Signal Explainer
**File:** `ai/explainer.py`
- AI-generated signal explanations
- Reasoning generation
- Natural language explanations

### 1.12 Signals Module

**Location:** `argo/signals/`

#### 1.12.1 Signal Generator
**File:** `signals/generator.py`
- Signal generation utilities
- Signal formatting
- Signal processing

#### 1.12.2 Compliance Wrapper
**File:** `signals/add_compliance_wrapper.py`
- Compliance metadata
- Regulatory information
- Audit trail

### 1.13 Utilities

**Location:** `argo/utils/`

- Secrets management
- Logging utilities
- Helper functions

---

## 2. Alpine Backend

**Location:** `alpine-backend/`  
**Type:** Python/FastAPI  
**Purpose:** User management, subscriptions, signal distribution

### 2.1 API Endpoints

**Location:** `backend/api/`

#### 2.1.1 Authentication
**Files:**
- `api/auth.py` - Main authentication endpoints
- `api/auth_2fa.py` - Two-factor authentication
- `api/two_factor.py` - 2FA management

**Endpoints:**
- `/api/v1/auth/login` - User login
- `/api/v1/auth/signup` - User registration
- `/api/v1/auth/logout` - User logout
- `/api/v1/auth/refresh` - Token refresh
- `/api/v1/auth/2fa/enable` - Enable 2FA
- `/api/v1/auth/2fa/verify` - Verify 2FA
- `/api/v1/auth/2fa/disable` - Disable 2FA

#### 2.1.2 User Management
**File:** `api/users.py`

**Endpoints:**
- `/api/v1/users/me` - Get current user
- `/api/v1/users/{user_id}` - Get user by ID
- `/api/v1/users/{user_id}` - Update user
- `/api/v1/users/{user_id}` - Delete user

#### 2.1.3 Subscriptions
**File:** `api/subscriptions.py`

**Endpoints:**
- `/api/v1/subscriptions` - List subscriptions
- `/api/v1/subscriptions/{subscription_id}` - Get subscription
- `/api/v1/subscriptions` - Create subscription
- `/api/v1/subscriptions/{subscription_id}` - Update subscription
- `/api/v1/subscriptions/{subscription_id}` - Cancel subscription

#### 2.1.4 Payments
**File:** `api/payments.py`

**Endpoints:**
- `/api/v1/payments/checkout` - Create checkout session
- `/api/v1/payments/portal` - Create portal session
- `/api/v1/payments/webhook` - Stripe webhook handler

#### 2.1.5 Signals
**File:** `api/signals.py`

**Endpoints:**
- `/api/v1/signals` - List signals
- `/api/v1/signals/{signal_id}` - Get signal
- `/api/v1/signals/history` - Signal history
- `/api/v1/signals/live` - Live signals (WebSocket)

#### 2.1.6 Trading
**File:** `api/trading.py`

**Endpoints:**
- `/api/v1/trading/positions` - Get positions
- `/api/v1/trading/orders` - Get orders
- `/api/v1/trading/performance` - Performance metrics

#### 2.1.7 Argo Sync
**File:** `api/argo_sync.py`

**Endpoints:**
- `/api/v1/argo/sync` - Sync signals from Argo
- `/api/v1/argo/status` - Sync status

#### 2.1.8 External Signal Sync
**File:** `api/external_signal_sync.py`

**Endpoints:**
- `/api/v1/external/signals` - External signal sync
- `/api/v1/external/status` - Sync status

#### 2.1.9 Admin
**File:** `api/admin.py`

**Endpoints:**
- `/api/v1/admin/users` - User management
- `/api/v1/admin/signals` - Signal management
- `/api/v1/admin/stats` - System statistics

#### 2.1.10 Roles
**File:** `api/roles.py`

**Endpoints:**
- `/api/v1/roles` - List roles
- `/api/v1/roles/{role_id}` - Get role
- `/api/v1/roles` - Create role
- `/api/v1/roles/{role_id}` - Update role
- `/api/v1/roles/{role_id}` - Delete role

#### 2.1.11 Notifications
**File:** `api/notifications.py`

**Endpoints:**
- `/api/v1/notifications` - List notifications
- `/api/v1/notifications/{notification_id}` - Get notification
- `/api/v1/notifications/{notification_id}/read` - Mark as read

#### 2.1.12 Webhooks
**File:** `api/webhooks.py`

**Endpoints:**
- `/api/v1/webhooks` - List webhooks
- `/api/v1/webhooks` - Create webhook
- `/api/v1/webhooks/{webhook_id}` - Update webhook
- `/api/v1/webhooks/{webhook_id}` - Delete webhook

#### 2.1.13 Security Dashboard
**File:** `api/security_dashboard.py`

**Endpoints:**
- `/api/v1/security/dashboard` - Security metrics
- `/api/v1/security/events` - Security events
- `/api/v1/security/alerts` - Security alerts

### 2.2 Core Infrastructure

**Location:** `backend/core/`

#### 2.2.1 Database
**File:** `core/database.py`
- SQLAlchemy setup
- Database connection management
- Session management

#### 2.2.2 Configuration
**Files:**
- `core/config.py` - Main configuration
- `core/config_utils.py` - Configuration utilities

#### 2.2.3 Caching
**Files:**
- `core/cache.py` - Redis caching
- `core/cache_constants.py` - Cache constants
- `core/query_cache.py` - Query result caching

#### 2.2.4 Security
**Files:**
- `core/security_utils.py` - Security utilities
- `core/security_headers.py` - Security headers middleware
- `core/security_logging.py` - Security event logging
- `core/csrf.py` - CSRF protection
- `core/input_sanitizer.py` - Input sanitization
- `core/token_blacklist.py` - JWT token blacklist

#### 2.2.5 Authentication
**Location:** `backend/auth/`

**Files:**
- `auth/security.py` - Password hashing, JWT tokens
- `auth/password_validator.py` - Password validation
- `auth/totp.py` - TOTP (2FA) implementation

#### 2.2.6 Authorization
**Files:**
- `core/rbac.py` - Role-based access control
- `core/resource_ownership.py` - Resource ownership checks

#### 2.2.7 Rate Limiting
**File:** `core/rate_limit.py`
- API rate limiting
- Per-user limits
- Per-endpoint limits

#### 2.2.8 Account Lockout
**File:** `core/account_lockout.py`
- Failed login tracking
- Account lockout after failed attempts
- Lockout duration management

#### 2.2.9 Validation
**File:** `core/validation.py`
- Input validation
- Data validation
- Schema validation

#### 2.2.10 Error Handling
**Files:**
- `core/error_handling.py` - Error handling utilities
- `core/error_responses.py` - Standardized error responses

#### 2.2.11 Logging
**Files:**
- `core/logging_middleware.py` - Request/response logging
- `core/request_logging.py` - Detailed request logging

#### 2.2.12 Metrics
**Files:**
- `core/metrics.py` - Prometheus metrics
- `core/metrics_middleware.py` - Metrics collection middleware

#### 2.2.13 Performance
**Files:**
- `core/performance_monitor.py` - Performance monitoring
- `core/query_optimizer.py` - Query optimization

#### 2.2.14 Request Tracking
**Files:**
- `core/request_tracking.py` - Request ID tracking
- `core/request_logging.py` - Request logging

#### 2.2.15 Response Formatting
**Files:**
- `core/response_formatter.py` - Response formatting
- `core/response_utils.py` - Response utilities

#### 2.2.16 Data Transformation
**File:** `core/data_transform.py`
- Data transformation utilities
- Format conversion

#### 2.2.17 HTTP Client
**File:** `core/http_client.py`
- HTTP client utilities
- External API calls
- Retry logic

#### 2.2.18 API Utilities
**File:** `core/api_utils.py`
- API helper functions
- Common API operations

#### 2.2.19 API Documentation
**File:** `core/api_docs.py`
- OpenAPI documentation
- API schema generation

#### 2.2.20 Type Utilities
**File:** `core/type_utils.py`
- Type conversion utilities
- Type validation

#### 2.2.21 Signal Sync Utilities
**File:** `core/signal_sync_utils.py`
- Signal synchronization utilities
- Data transformation for sync

#### 2.2.22 Webhook Retry Queue
**File:** `core/webhook_retry_queue.py`
- Webhook retry mechanism
- Failed webhook handling
- Exponential backoff

#### 2.2.23 Alerting
**File:** `core/alerting.py`
- Alert generation
- Notification system

#### 2.2.24 Test Utilities
**File:** `core/test_utils.py`
- Testing utilities
- Test helpers
- Mock data

### 2.3 Data Models

**Location:** `backend/models/`

#### 2.3.1 User Model
**File:** `models/user.py`
- User entity
- User tiers (FREE, BASIC, PREMIUM, INSTITUTIONAL)
- User relationships

#### 2.3.2 Signal Model
**File:** `models/signal.py`
- Signal entity
- Signal metadata
- Signal relationships

#### 2.3.3 Subscription Model
**File:** `models/subscription.py` (via User model)
- Subscription entity
- Subscription status
- Billing information

#### 2.3.4 Notification Model
**File:** `models/notification.py`
- Notification entity
- Notification types
- Read status

#### 2.3.5 Backtest Model
**File:** `models/backtest.py`
- Backtest entity
- Backtest results
- Backtest metadata

#### 2.3.6 Role Model
**File:** `models/role.py`
- Role entity
- Permissions
- Role assignments

### 2.4 Main Application

**File:** `backend/main.py`
- FastAPI application setup
- Middleware configuration
- Route registration
- CORS configuration
- Startup/shutdown events

---

## 3. Alpine Frontend

**Location:** `alpine-frontend/`  
**Type:** Next.js/TypeScript/React  
**Purpose:** Web dashboard and user interface

### 3.1 Pages

**Location:** `app/`

#### 3.1.1 Landing Page
**File:** `app/page.tsx`
- Homepage
- Hero section
- Feature highlights
- Call-to-action

#### 3.1.2 Dashboard
**File:** `app/dashboard/page.tsx`
- Main user dashboard
- Signal display
- Performance charts
- Account overview

#### 3.1.3 Signals Page
**File:** `app/signals/page.tsx`
- Signal browsing
- Signal filtering
- Signal details
- Real-time updates

#### 3.1.4 Backtest Page
**File:** `app/backtest/page.tsx`
- Backtest results
- Performance analysis
- Equity curve visualization
- Download functionality

#### 3.1.5 Account Page
**File:** `app/account/page.tsx`
- User account settings
- Profile management
- Subscription management
- Billing information

#### 3.1.6 Pricing Page
**File:** `app/pricing/page.tsx`
- Subscription plans
- Feature comparison
- Checkout flow

#### 3.1.7 Login Page
**File:** `app/login/page.tsx`
- User login
- 2FA support
- Password reset

#### 3.1.8 Signup Page
**File:** `app/signup/page.tsx`
- User registration
- Account creation
- Email verification

#### 3.1.9 Admin Page
**File:** `app/admin/page.tsx`
- Admin dashboard
- User management
- System statistics
- Signal management

#### 3.1.10 Contact Page
**File:** `app/contact/page.tsx`
- Contact form
- Support information

#### 3.1.11 Methodology Page
**File:** `app/methodology/page.tsx`
- Trading methodology
- Algorithm explanation
- Strategy details

#### 3.1.12 Legal Pages
**Files:**
- `app/privacy/page.tsx` - Privacy policy
- `app/terms/page.tsx` - Terms of service
- `app/refunds/page.tsx` - Refund policy

### 3.2 API Routes

**Location:** `app/api/`

#### 3.2.1 Authentication Routes
**Location:** `app/api/auth/`
- `[...nextauth]/route.ts` - NextAuth.js handler
- `signup/route.ts` - Signup endpoint

#### 3.2.2 Stripe Routes
**Location:** `app/api/stripe/`
- `create-checkout-session/route.ts` - Checkout session creation
- `create-portal-session/route.ts` - Customer portal
- `webhook/route.ts` - Stripe webhook handler

#### 3.2.3 Health Routes
**Location:** `app/api/health/`
- `route.ts` - Health check
- `liveness/route.ts` - Liveness probe
- `readiness/route.ts` - Readiness probe

#### 3.2.4 Other Routes
- `checkout/route.ts` - Checkout processing
- `download-backtest/route.ts` - Backtest download
- `feedback/route.ts` - Feedback submission
- `user/me/route.ts` - Current user info

### 3.3 Components

**Location:** `components/`

#### 3.3.1 Dashboard Components
**Location:** `components/dashboard/`

**Files:**
- `Navigation.tsx` - Dashboard navigation
- `SignalCard.tsx` - Signal display card
- `SymbolTable.tsx` - Symbol data table
- `PerformanceChart.tsx` - Performance visualization
- `PricingTable.tsx` - Pricing display
- `PaymentModal.tsx` - Payment modal
- `TradingEnvironmentBadge.tsx` - Environment indicator
- `UserMenu.tsx` - User menu dropdown

#### 3.3.2 Stripe Components
**Location:** `components/stripe/`

**Files:**
- `CheckoutButton.tsx` - Checkout button
- `ManageSubscriptionButton.tsx` - Subscription management

#### 3.3.3 Tradervue Components
**Location:** `components/tradervue/`

**Files:**
- `TradervueMetrics.tsx` - Metrics display
- `TradervueWidget.tsx` - Widget integration

#### 3.3.4 UI Components
**Location:** `components/ui/`

**Files:**
- `button.tsx` - Button component
- `input.tsx` - Input component
- `tabs.tsx` - Tabs component
- `accordion.tsx` - Accordion component

#### 3.3.5 Marketing Components
**Files:**
- `Hero.tsx` - Hero section
- `Features.tsx` - Features display
- `Pricing.tsx` - Pricing section
- `FAQ.tsx` - FAQ section
- `SocialProof.tsx` - Social proof
- `Testimonials.tsx` - Testimonials
- `HowItWorks.tsx` - How it works
- `Problem.tsx` - Problem statement
- `Solution.tsx` - Solution presentation
- `Proof.tsx` - Proof/evidence
- `TheProof.tsx` - Detailed proof
- `OurEdge.tsx` - Competitive advantage
- `WhoIsItFor.tsx` - Target audience
- `WhatToExpect.tsx` - Expectations
- `OriginStory.tsx` - Company story
- `ContinuousImprovement.tsx` - Improvement process

#### 3.3.6 Signal Components
**Files:**
- `signal-card.tsx` - Signal card display
- `SignalCard.tsx` - Alternative signal card
- `SignalQuality.tsx` - Quality indicators
- `SignalSelectivity.tsx` - Selectivity metrics
- `HighConfidenceSignals.tsx` - High confidence display
- `SymbolTable.tsx` - Symbol table
- `RegimeCards.tsx` - Market regime cards

#### 3.3.7 Chart Components
**Files:**
- `PerformanceChart.tsx` - Performance charts
- `EquityCurveChart.tsx` - Equity curve visualization

#### 3.3.8 Legal/Compliance Components
**Files:**
- `LegalDisclaimer.tsx` - Legal disclaimer
- `RiskDisclosure.tsx` - Risk disclosure
- `RiskWarning.tsx` - Risk warnings
- `VerificationSection.tsx` - Verification display

#### 3.3.9 Comparison Components
**Files:**
- `Comparison.tsx` - Feature comparison
- `CompetitorComparison.tsx` - Competitor comparison

#### 3.3.10 Other Components
**Files:**
- `Header.tsx` - Site header
- `Footer.tsx` - Site footer
- `Navigation.tsx` - Main navigation
- `Contact.tsx` - Contact form
- `FeedbackForm.tsx` - Feedback form
- `ErrorBoundary.tsx` - Error boundary
- `GradientButton.tsx` - Styled button
- `TrustIndicator.tsx` - Trust indicators
- `InstitutionalFeatures.tsx` - Institutional features
- `TechnicalInfrastructure.tsx` - Infrastructure display
- `HonestDisclosure.tsx` - Honest disclosure
- `FinalCTA.tsx` - Final call-to-action
- `CSVPreview.tsx` - CSV preview
- `providers.tsx` - React providers

### 3.4 Hooks

**Location:** `hooks/`

#### 3.4.1 useSignals
**File:** `hooks/useSignals.ts`
- Signal data fetching
- Real-time signal updates
- Signal filtering

#### 3.4.2 useWebSocket
**File:** `hooks/useWebSocket.ts`
- WebSocket connection
- Real-time updates
- Connection management

#### 3.4.3 useTradingEnvironment
**File:** `hooks/useTradingEnvironment.ts`
- Trading environment detection
- Environment switching
- Environment state

#### 3.4.4 useIntersectionObserver
**File:** `hooks/useIntersectionObserver.ts`
- Intersection Observer hook
- Scroll-based animations
- Lazy loading

### 3.5 Libraries

**Location:** `lib/`

#### 3.5.1 API Client
**File:** `lib/api.ts`
- API client utilities
- HTTP requests
- Error handling

#### 3.5.2 Authentication
**File:** `lib/auth.ts`
- Authentication utilities
- Session management
- Token handling

#### 3.5.3 Database
**File:** `lib/db.ts`
- Prisma client
- Database queries
- Type-safe queries

#### 3.5.4 Stripe
**Files:**
- `lib/stripe.ts` - Stripe client
- `lib/stripe-helpers.ts` - Stripe utilities

#### 3.5.5 Utilities
**Files:**
- `lib/utils.ts` - General utilities
- `lib/brand.ts` - Brand constants

### 3.6 Types

**Location:** `types/`

#### 3.6.1 NextAuth Types
**File:** `types/next-auth.d.ts`
- NextAuth type definitions
- Session types
- User types

#### 3.6.2 Signal Types
**File:** `types/signal.ts`
- Signal type definitions
- Signal data structures

### 3.7 Configuration

**Files:**
- `next.config.js` - Next.js configuration
- `tsconfig.json` - TypeScript configuration
- `tailwind.config.ts` - Tailwind CSS configuration
- `postcss.config.js` - PostCSS configuration
- `jest.config.js` - Jest configuration
- `playwright.config.ts` - Playwright configuration
- `prisma/schema.prisma` - Prisma schema

---

## 4. Infrastructure & DevOps

### 4.1 Deployment Commands

**Location:** `commands/`

#### 4.1.1 Deploy Command
**File:** `commands/deploy`
- Deployment orchestration
- Service deployment
- Environment management

#### 4.1.2 Health Command
**File:** `commands/health`
- Health check execution
- Service status
- Health monitoring

#### 4.1.3 Status Command
**File:** `commands/status`
- Service status
- Deployment status
- System status

#### 4.1.4 Logs Command
**File:** `commands/logs`
- Log viewing
- Log following
- Log filtering

#### 4.1.5 Start Command
**File:** `commands/start`
- Service startup
- Local development
- Service orchestration

#### 4.1.6 Stop Command
**File:** `commands/stop`
- Service shutdown
- Graceful termination

#### 4.1.7 Restart Command
**File:** `commands/restart`
- Service restart
- Rolling restarts

#### 4.1.8 Rollback Command
**File:** `commands/rollback`
- Deployment rollback
- Version reversion

#### 4.1.9 Command Libraries
**Location:** `commands/lib/`

**Files:**
- `health-check-local.sh` - Local health checks
- `health-check-production.sh` - Production health checks
- `start-local-services.sh` - Local service startup
- `stop-local-services.sh` - Local service shutdown
- `restart-local-services.sh` - Local service restart
- `status-check-local.sh` - Local status checks
- `status-check-production.sh` - Production status checks
- `view-logs-local.sh` - Local log viewing
- `view-logs-production.sh` - Production log viewing

### 4.2 Deployment Scripts

**Location:** `scripts/`

#### 4.2.1 Main Deployment
**Files:**
- `deploy.sh` - Main deployment script
- `deploy_production.sh` - Production deployment
- `deploy_production_v6.0.sh` - v6.0 deployment
- `deploy_prop_firm_to_production.sh` - Prop firm deployment
- `deploy_all_v6.0.sh` - Full v6.0 deployment
- `deploy_dual_services.sh` - Dual service deployment

#### 4.2.2 Health Checks
**Files:**
- `health_check.sh` - Basic health check
- `health-check.sh` - Alternative health check
- `health_check_production.sh` - Production health check
- `comprehensive_health_check.py` - Comprehensive health check
- `comprehensive_health_analysis.py` - Health analysis
- `full-health-check.sh` - Full health check
- `local_health_check.sh` - Local health check
- `comprehensive_local_health_check.sh` - Comprehensive local check

#### 4.2.3 Verification
**Files:**
- `verify_deployment.sh` - Deployment verification
- `verify_production_deployment.sh` - Production verification
- `verify_performance_evaluation_deployment.sh` - Performance verification
- `post_deployment_verification.sh` - Post-deployment checks
- `pre_deployment_validation.sh` - Pre-deployment validation
- `quick_deployment_check.sh` - Quick checks

#### 4.2.4 Monitoring
**Files:**
- `monitor_production.sh` - Production monitoring
- `monitor_signals.py` - Signal monitoring
- `continuous_monitor.py` - Continuous monitoring

#### 4.2.5 Setup Scripts
**Files:**
- `first-time-setup.sh` - Initial setup
- `setup_local_dev.sh` - Local development setup
- `setup-production-env.sh` - Production environment setup
- `setup-env.sh` - Environment setup
- `setup_monitoring.sh` - Monitoring setup
- `setup-argo-alpine-sync.sh` - Sync setup

#### 4.2.6 Security Scripts
**Files:**
- `security-audit.sh` - Security audit
- `security-monitor.sh` - Security monitoring
- `local_security_audit.sh` - Local security audit
- `security_audit_complete.py` - Complete security audit

#### 4.2.7 Performance Scripts
**Files:**
- `optimize.sh` - Performance optimization
- `optimize_performance.py` - Performance optimization
- `optimize-integrity-monitor.sh` - Integrity monitor optimization

#### 4.2.8 Database Scripts
**Files:**
- `init-database.sh` - Database initialization
- `run-migration.sh` - Migration execution
- `run-alpine-migration.sh` - Alpine migration

#### 4.2.9 Rollback Scripts
**Files:**
- `rollback.sh` - Rollback execution
- `rollback_deployment.sh` - Deployment rollback

#### 4.2.10 Status Scripts
**Files:**
- `monorepo-status.sh` - Monorepo status
- `validate_local_system.sh` - Local system validation

### 4.3 Agentic Automation

**Location:** `scripts/agentic/`

#### 4.3.1 Automated Deployment
**File:** `agentic/automated-deployment.sh`
- AI-powered deployment
- Automated decision making
- Safety gates

#### 4.3.2 Automated Troubleshooting
**File:** `agentic/automated-troubleshooting.sh`
- AI-powered troubleshooting
- Problem diagnosis
- Solution generation

#### 4.3.3 Code Review
**File:** `agentic/weekly-code-review.sh`
- Automated code reviews
- Quality analysis
- Improvement suggestions

#### 4.3.4 Test Coverage Analysis
**File:** `agentic/test-coverage-analysis.sh`
- Coverage analysis
- Gap identification
- Improvement recommendations

#### 4.3.5 Documentation Updates
**File:** `agentic/monthly-docs-update.sh`
- Automated documentation updates
- Documentation sync
- Content generation

#### 4.3.6 Usage Tracking
**File:** `agentic/usage_tracker.py`
- Usage monitoring
- Analytics collection
- Reporting

#### 4.3.7 Monitoring
**File:** `agentic/monitor.py`
- System monitoring
- Alert generation
- Status reporting

#### 4.3.8 Rate Limiting
**File:** `agentic/rate_limiter.py`
- API rate limiting
- Usage limits
- Quota management

#### 4.3.9 Copilot Integration
**File:** `agentic/copilot-with-rules.sh`
- Cursor Copilot integration
- Rule-based automation
- AI assistance

#### 4.3.10 Templates
**Location:** `agentic/templates/`

**Files:**
- `deployment-template.sh` - Deployment template
- `refactoring-template.sh` - Refactoring template
- `troubleshooting-template.sh` - Troubleshooting template

### 4.4 Docker Configuration

**Location:** `alpine-backend/`

#### 4.4.1 Docker Compose Files
**Files:**
- `docker-compose.yml` - Main compose file
- `docker-compose.local.yml` - Local development
- `docker-compose.production.yml` - Production
- `docker-compose.blue.yml` - Blue deployment
- `docker-compose.green.yml` - Green deployment
- `docker-compose.complete.yml` - Complete stack

#### 4.4.2 Dockerfiles
**Files:**
- `argo/Dockerfile` - Argo Docker image
- `alpine-backend/backend/Dockerfile` - Alpine backend image

### 4.5 Nginx Configuration

**Location:** `alpine-backend/nginx/`

#### 4.5.1 Nginx Config
**File:** `nginx/nginx.conf`
- Reverse proxy configuration
- SSL termination
- Load balancing
- Rate limiting

#### 4.5.2 SSL Certificates
**Location:** `nginx/ssl/`
- SSL certificate storage
- Certificate management

### 4.6 Monitoring

**Location:** `alpine-backend/monitoring/`

#### 4.6.1 Prometheus
**Files:**
- Prometheus configuration
- Metrics collection
- Scrape configuration

#### 4.6.2 Grafana
**Files:**
- Grafana dashboards
- Visualization configuration
- Alert rules

### 4.7 Systemd Services

**Location:** `infrastructure/systemd/`

**Files:**
- Service unit files
- Service management
- Auto-start configuration

---

## 5. Shared Packages

**Location:** `packages/shared/`

### 5.1 Verification

**Location:** `packages/shared/verification/`

#### 5.1.1 SHA-256 Verification
**File:** `verification/sha256.py`
- SHA-256 hash generation
- Signal verification
- Integrity checking

### 5.2 Utilities

**Location:** `packages/shared/utils/`

#### 5.2.1 Secrets Manager
**File:** `utils/secrets_manager.py`
- AWS Secrets Manager integration
- Secret retrieval
- Secret rotation

#### 5.2.2 Logger
**File:** `utils/logger.py`
- Shared logging utilities
- Log formatting
- Log levels

### 5.3 Types

**Location:** `packages/shared/types/`

#### 5.3.1 Signal Types
**File:** `types/signal.py`
- Signal type definitions
- Signal data structures
- Type validation

---

## 6. Development Tools

### 6.1 Testing

#### 6.1.1 Unit Tests
**Locations:**
- `argo/tests/unit/` - Argo unit tests
- `alpine-backend/tests/` - Alpine backend tests
- `alpine-frontend/__tests__/` - Frontend unit tests

#### 6.1.2 Integration Tests
**Locations:**
- `argo/tests/backtest/` - Backtest tests
- `alpine-backend/tests/integration/` - Backend integration tests

#### 6.1.3 E2E Tests
**Location:** `alpine-frontend/e2e/`
- Playwright E2E tests
- User flow testing
- Browser automation

### 6.2 Code Quality

#### 6.2.1 Linting
- **Python:** Ruff, Black, isort
- **TypeScript:** ESLint, Prettier

#### 6.2.2 Type Checking
- **Python:** mypy
- **TypeScript:** TypeScript compiler

#### 6.2.3 Formatting
- **Python:** Black
- **TypeScript/JavaScript:** Prettier

### 6.3 Build Tools

#### 6.3.1 Turbo
**File:** `turbo.json`
- Monorepo build orchestration
- Task caching
- Parallel execution

#### 6.3.2 Package Management
- **Node.js:** pnpm (workspace)
- **Python:** pip, requirements.txt

### 6.4 CI/CD

#### 6.4.1 GitHub Actions
**Location:** `.github/workflows/`
- Automated testing
- Deployment pipelines
- Code quality checks

### 6.5 Documentation

#### 6.5.1 Documentation Files
**Location:** `docs/`
- 270+ markdown files
- System documentation
- API documentation
- Guides and tutorials

### 6.6 Git Hooks

#### 6.6.1 Husky
- Pre-commit hooks
- Commit message validation
- Code quality checks

#### 6.6.2 Commitlint
**File:** `commitlint.config.js`
- Commit message linting
- Conventional commits

### 6.7 Versioning

#### 6.7.1 Changesets
- Version management
- Changelog generation
- Release automation

---

## Summary Statistics

### Component Counts

- **Argo Core Services:** 25+
- **Data Sources:** 7
- **Backtesting Modules:** 30+
- **API Endpoints (Argo):** 10
- **API Endpoints (Alpine):** 13
- **Frontend Pages:** 12
- **Frontend Components:** 50+
- **Infrastructure Scripts:** 100+
- **Agentic Automation:** 10
- **Total Python Files:** 256+
- **Total TypeScript/TSX Files:** 100+

### Technology Stack

**Backend:**
- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- Alpaca API
- Stripe API

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Prisma
- NextAuth.js

**Infrastructure:**
- Docker
- Docker Compose
- Nginx
- Prometheus
- Grafana
- AWS (S3, Secrets Manager)
- Systemd

**Development:**
- pnpm
- Turbo
- Jest
- Pytest
- Playwright
- GitHub Actions
- Husky

---

**Last Updated:** January 16, 2025  
**Maintained By:** Development Team

